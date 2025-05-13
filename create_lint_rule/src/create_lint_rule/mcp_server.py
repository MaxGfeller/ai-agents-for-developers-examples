from fastmcp import FastMCP
from main import LintRuleFlow

mcp = FastMCP("Create Lint Rule 🚀")

@mcp.tool()
async def create_lint_rule(description: str) -> str:
    """Create a lint rule"""
    flow = LintRuleFlow(description)
    return await flow.kickoff_async()

if __name__ == "__main__":
    mcp.run(transport="sse")
