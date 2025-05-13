from crewai import Agent, Crew, Process, Task
from crewai_tools import FileReadTool, FileWriterTool
from crewai.project import CrewBase, agent, crew, task
from pathlib import Path
from .tools.take_screenshot_tool import TakeScreenshotTool

docs_updater = Agent(
	role="Technical writer of user documentation",
	goal="Update the user documentation to reflect the latest changes in the codebase",
	backstory="You are a technical writer with a deep understanding of the codebase and the user needs. You are able to write clear and concise documentation that is easy to understand.",
	tools=[
		FileReadTool(file_path=Path(__file__).parent.parent.parent / "example-app" / "docs" / "user-docs.md"),
		FileWriterTool()
	],
	verbose=True,
	llm="openrouter/openai/gpt-4o"
)

docs_updater_task = Task(
	description="Update the user documentation to reflect the latest changes in the codebase. Here is the diff of the changes:\n\n```\n{diff}\n```\n\nUse the tools provided to read and update the user documentation.",
	expected_output="A quick summary of the changes you made to the user documentation.",
	agent=docs_updater
)

screenshot_updater = Agent(
	role="Technical writer of user documentation",
	goal="Update the user documentation to reflect the latest changes in the codebase",
	backstory="You are a technical writer with a deep understanding of the codebase and the user needs. You are able to write clear and concise documentation that is easy to understand.",
	tools=[TakeScreenshotTool()],
	verbose=True,
	llm="openrouter/openai/gpt-4o"
)

screenshot_updater_task = Task(
	description="Take a new screenshot of the updated UI if something changed in the UI. Use the provided tool to capture the screenshot.",
	expected_output="A summary of the screenshot(s) taken and their location.",
	agent=screenshot_updater
)

docs_updater_crew = Crew(
	agents=[docs_updater, screenshot_updater],
	tasks=[docs_updater_task, screenshot_updater_task],
	process=Process.sequential,
	verbose=True
)
