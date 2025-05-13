from crewai.tools import BaseTool
from playwright.sync_api import sync_playwright
from pathlib import Path

PATH = Path(__file__).parent.parent.parent.parent / "example-app" / "docs" / "screenshot.png"

class TakeScreenshotTool(BaseTool):
    name: str = "Take screenshot"
    description: str = (
        "Take a screenshot of the current page."
    )

    def _run(self) -> str:
        print("Taking screenshot")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://localhost:5173")
            page.screenshot(path=PATH, full_page=True)
            browser.close()
        return "Successfully took a new screenshot"
