# AI Agents for Developers – Demo Project

This repository contains three example projects demonstrating the use of multi-agent AI systems and admin tooling for developers. Each example is self-contained and showcases a different use case or integration.

## Examples

### 1. create_lint_rule

A multi-agent system (powered by [crewAI](https://crewai.com)) that demonstrates how agents can collaborate to create a lint rule. The system is highly configurable, allowing you to define your own agents and tasks.

- **Directory:** `create_lint_rule`
- **Key Features:**
  - Multi-agent collaboration
  - Easily extensible via YAML config files
  - Generates a `report.md` as output

### 2. docs_updater

Another crewAI-based multi-agent system, this one focused on updating documentation. Like the lint rule example, it is highly configurable and outputs a `report.md` file.

- **Directory:** `docs_updater`
- **Key Features:**
  - Multi-agent collaboration
  - Customizable agents and tasks
  - Designed for documentation workflows

### 3. app-admin-mcp

A server providing admin functionalities for a CRM app, including note storage, summarization, and note-adding tools. Integrates with the Model Context Protocol (MCP) and is suitable for use with tools like Claude Desktop.

- **Directory:** `app-admin-mcp`
- **Key Features:**
  - Note storage and summarization
  - MCP server integration
  - Example configuration for Claude Desktop

---

## Installation

All examples require **Python 3.10–3.13** and use [uv](https://docs.astral.sh/uv/) for dependency management.

1. **Install uv** (if not already installed):

```bash
pip install uv
```

2. **Install dependencies for each example:**

```bash
cd <example-directory>
uv sync
```

For the `create_lint_rule` and `docs_updater` examples, you also need to install the Javascript dependencies:

```bash
cd <example-directory>
npm install
```

3. **Set up environment variables:**

- Add your `OPENROUTER_API_KEY` to the `.env` file in each example directory (if required).

---

## Running the Examples

### docs_updater

The doc updater example is a simple crewAI-based multi-agent system that updates a documentation website.

You can start the demo application by running:

```bash
npm run dev
```

This will start the dev server on http://localhost:5173.

You can run the docs (which are built with VitePress) by running:

```bash
npm run docs:dev
```

This will start the docs server on http://localhost:5174.

You can then edit the app (in `src/App.tsx`) and start the doc updater by running:

```bash
uv run src/docs_updater/main.py
```

### create_lint_rule

The create lint rule example is a crewAI-based workflow that creates an eslint rule.

You can run it by running:

```bash
uv run src/create_lint_rule/main.py "<description of the rule>"
```

You can also start the MCP server by running:

```bash
uv run src/create_lint_rule/mcp_server.py
```

Then, you can then add this server to your Cursor editor:

```json
{
  "mcpServers": {
    "create-lint-rule": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```
