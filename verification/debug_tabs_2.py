
from playwright.sync_api import sync_playwright, expect

def verify_tabs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        import os
        cwd = os.getcwd()
        url = f"file://{cwd}/legacy-index.html"
        page.goto(url)

        active_panel = page.locator("#active")

        # Check if it has content. If it is empty, maybe Playwright considers it hidden if height is 0?
        # The content is a div with id="active-list".
        # Initially empty.

        # Add some content
        page.evaluate("document.getElementById(\"active-list\").innerHTML = \"Test Content\"")

        print("Computed Display:", active_panel.evaluate("el => window.getComputedStyle(el).display"))
        print("Bounding Box:", active_panel.bounding_box())

        # Force visibility check
        is_visible = active_panel.is_visible()
        print(f"Is visible: {is_visible}")

        if not is_visible:
             # Check visibility of parents
             parent = active_panel.locator("..")
             print("Parent Display:", parent.evaluate("el => window.getComputedStyle(el).display"))

        browser.close()

if __name__ == "__main__":
    verify_tabs()
