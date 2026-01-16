
from playwright.sync_api import sync_playwright, expect

def verify_tabs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Listen to console
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"PAGE ERROR: {exc}"))

        import os
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/legacy-index.html")

        # Inject content so the panel has height
        page.evaluate("document.getElementById(\"active-list\").innerHTML = \"<p>Active Content</p>\"")

        cancelled_tab = page.locator("#tab-cancelled")

        print("Clicking cancelled tab...")
        cancelled_tab.click()

        active_tab = page.locator("#tab-active")

        # Check attribute value manually
        val = active_tab.get_attribute("aria-selected")
        print(f"Active tab aria-selected: {val}")

        expect(active_tab).to_have_attribute("aria-selected", "false")

        browser.close()

if __name__ == "__main__":
    verify_tabs()
