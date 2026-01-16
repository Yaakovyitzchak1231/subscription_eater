
from playwright.sync_api import sync_playwright, expect

def verify_tabs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        import os
        cwd = os.getcwd()
        url = f"file://{cwd}/legacy-index.html"
        print(f"Loading {url}")
        page.goto(url)

        # Debug: Print content of body
        # print(page.content())

        active_panel = page.locator("#active")

        print("Classes:", active_panel.get_attribute("class"))
        print("Style:", active_panel.get_attribute("style"))
        print("Computed Display:", active_panel.evaluate("el => window.getComputedStyle(el).display"))

        page.screenshot(path="verification/debug_tabs.png")

        expect(active_panel).to_be_visible()
        print("Visible!")

        browser.close()

if __name__ == "__main__":
    verify_tabs()
