from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence
from crewai import Agent, LLM, Task, Crew
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel, Field, model_validator

"""
Pydantic model which we can use as structured output for the example agent. For simplicity,
this also includes the rule name.
"""
class ExampleSet(BaseModel):
    positive_examples: list[str] = Field(..., description="Should trigger the rule")
    negative_examples: list[str] = Field(..., description="Should *not* trigger the rule")

    @model_validator(mode="after")
    def _check_lengths(self):
        if len(self.positive_examples) != 3 or len(self.negative_examples) != 3:
            raise ValueError("Need exactly three positive and three negative examples")
        return self

class CodeExamples(BaseModel):
    rule_name: str = Field(..., description="The name of the rule in kebab-case")
    examples: ExampleSet


"""
Pydantic model which we can use as structured output for the rule agent. This forces the
LLM to output a valid JS code without backticks and without markdown.
"""
class LintRule(BaseModel):
    """JS source for the rule."""
    rule_source: str = Field(..., description="The complete source code for the rule`")


"""
This agent is responsible for producing thorough positive/negative snippets for a rule.
"""
example_agent = Agent(
    role="ESLint test‑case creator",
    goal="Produce thorough positive/negative snippets for a rule.",
    backstory="You are a senior JS dev writing exhaustive ESLint tests.",
    llm=LLM("openrouter/openai/gpt-4o"),
)

"""
This agent is responsible for producing a fully‑functional rule with id `custom-rule`.
"""
rule_agent = Agent(
    role="ESLint rule implementor",
    goal="Turn requirements into a fully‑functional rule with id `custom-rule`.",
    backstory="Veteran JS tooling engineer specialized in ESLint plugins.",
    llm=LLM("openrouter/openai/o4-mini"),
)

EXAMPLE_TASK_DESCRIPTION = """
You are producing test cases for an ESLint rule.

**Important constraints**

1. "positive_examples" MUST violate the rule – ESLint should report exactly one error.
2. "negative_examples" MUST comply – ESLint should report zero errors.
3. Do not duplicate snippets across the two lists.
4. Return **ONLY** valid JSON, conforming to the CodeExamples schema
   (no markdown, comments or back‑ticks).
5. Return exactly three positive and three negative examples.

Rule to test (natural language description):
{description}
"""


RULE_TASK_DESCRIPTION = """
    Provide ONLY the CommonJS source code (no markdown) for an ESLint rule with id
    `custom-rule` that enforces: ```\n{description}\n```\n
    Make sure you are using the correct syntax for ESLint 8.x. Return **only**:
    module.exports = {
    meta: { … },
    create(context) { … }
    };

    No array, no 'rules: key, no markdown.
"""

"""
This is the task that produces the examples for the rule.
"""
example_task = Task(
        description=EXAMPLE_TASK_DESCRIPTION,
        expected_output="JSON conforming to CodeExamples schema.",
        output_pydantic=CodeExamples,
        agent=example_agent,
    )

"""
We are assembling a simple crew with the example agent and the example task.
"""
example_crew = Crew(
    agents=[example_agent],
    tasks=[example_task],
)


"""
This is the task that produces the rule.
"""
rule_task = Task(
        description=RULE_TASK_DESCRIPTION,
        expected_output="A complete Javascript implementation of the rule, that starts with `module.exports = [...];` and contains the severity level, too.",
        output_pydantic=LintRule,
        agent=rule_agent,
    )

"""
We are assembling a simple crew with the rule agent and the rule task.
"""
rule_crew = Crew(
    agents=[rule_agent],
    tasks=[rule_task],
)

GENERATED_DIR = Path(__file__).with_suffix("").parent / "generated"
RULES_DIR = Path(__file__).with_suffix("").parent / "rules"
RULE_FILE = GENERATED_DIR / "custom-rule.js"
EXAMPLES_FILE = GENERATED_DIR / "examples.json"


def _write_rule(source: str) -> None:
    print("source", source)
    GENERATED_DIR.mkdir(exist_ok=True)
    RULE_FILE.write_text(source, encoding="utf-8")

def _delete_rule() -> None:
    if RULE_FILE.exists():
        RULE_FILE.unlink()

def _eslint_messages(code: str) -> Sequence[dict]:
    cmd = [
        "npx",
        "eslint",
        "--stdin",
        "--stdin-filename",
        "file.jsx",
        "--parser-options", "ecmaVersion:latest",
        "--parser-options", "sourceType:module",
        "--parser-options", "ecmaFeatures.jsx:true",
        "--rule",
        "example/custom-rule: 2",
        "-f",
        "json",
    ]
    result = subprocess.run(cmd, input=code, capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent.resolve())
    print("result", result)

    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr)

    output = result.stdout.strip() or "[]"
    parsed = json.loads(output)
    return parsed[0].get("messages", []) if parsed else []


def validate_rule(rule_source: str, examples: CodeExamples) -> bool:
    _write_rule(rule_source)

    print("examples", examples)
    for snippet in examples.examples.positive_examples:
        if not _eslint_messages(snippet):
            print("⚠️  Expected error, got none:\n", snippet)
            return False

    for snippet in examples.examples.negative_examples:
        if _eslint_messages(snippet):
            print("⚠️  Unexpected error:\n", snippet)
            return False

    return True

class CreateLintRuleState(BaseModel):
    rule_name: Optional[str] = None
    description: Optional[str] = None
    examples: Optional[CodeExamples] = None
    rule_source: Optional[str] = None
    validated: bool = False
    validation_error_message: Optional[str] = None
    validation_attempts: int = 0
    previous_rule_source: Optional[str] = None


class LintRuleFlow(Flow[CreateLintRuleState]):
    def __init__(self, description: str):
        super().__init__()
        self.state.description = description

    # 1️⃣  Examples ---------------------------------------------------------
    @start()
    def generate_examples(self):
        result = example_crew.kickoff(inputs={"description": self.state.description})

        self.state.examples = result.pydantic
        self.state.rule_name = result.pydantic.rule_name
        print(self.state.examples)
        print("✅ Examples generated")

    @listen(generate_examples)
    def implement_rule(self):
        context = {"description": self.state.description}
        result = rule_crew.kickoff(inputs=context)
        parsed_lint_rule = result.pydantic
        self.state.previous_rule_source = self.state.rule_source  # Save previous rule
        self.state.rule_source = parsed_lint_rule.rule_source
        print("✅ Rule implemented")

    @router(implement_rule)
    def validate_and_save(self):
        assert self.state.rule_source and self.state.examples
        try:
            ok = validate_rule(self.state.rule_source, self.state.examples)  # type: ignore[arg-type]
        except Exception as e:
            ok = False
            error_message = str(e)
        else:
            error_message = None if ok else "Validation failed (no error message)"
        self.state.validated = ok
        if not ok:
            self.state.validation_attempts += 1
            # ❌ rule failed but examples look suspicious → regenerate examples
            if "Expected error, got none" in error_message:
                return "generate_examples"

            self.state.validation_error_message = error_message
            if self.state.validation_attempts < 5:
                print("❌ Validation failed, retrying...")
                return "implement_rule"
            else:
                print("❌ Validation failed after 5 attempts.")
                _delete_rule()
                return "Failed to create lint rule, " + error_message
        else:
            print("✅ Validation passed, writing file...")
            _delete_rule()
            self.state.validation_error_message = None
            self.state.validation_attempts = 0
            return "write_file"

    @listen(validate_and_save)
    def finish(self):
        RULES_DIR.mkdir(exist_ok=True)
        RULE_FILE = RULES_DIR / f"{self.state.rule_name}.js"
        RULE_FILE.write_text(self.state.rule_source)
        print("✅ Flow completed successfully.")
        return f"Lint rule {self.state.rule_name} created successfully in {RULES_DIR}. This needs to be included in the eslint.config.js file, so please make sure to do that."

    def fail(self):
        print(f"❌ Flow failed after 5 attempts. Last error: {self.state.validation_error_message}")
        return f"Failed to create lint rule, {self.state.validation_error_message}"
        # sys.exit(1)

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python crewai_eslint_rule_generator.py \"<rule description>\"")
        sys.exit(1)

    flow = LintRuleFlow(sys.argv[1])
    flow.kickoff()


if __name__ == "__main__":
    main()
