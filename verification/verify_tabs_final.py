
from playwright.sync_api import sync_playwright, expect

def verify_tabs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        import os
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/legacy-index.html")

        # Inject content so the panel has height
        page.evaluate("document.getElementById(\"active-list\").innerHTML = \"<p>Active Content</p>\"")
        page.evaluate("document.getElementById(\"cancelled-list\").innerHTML = \"<p>Cancelled Content</p>\"")

        # Verify tablist role
        tablist = page.locator("[role=\"tablist\"]")
        expect(tablist).to_be_visible()

        # Verify initial state (Active tab selected)
        active_tab = page.locator("#tab-active")
        expect(active_tab).to_have_attribute("aria-selected", "true")

        cancelled_tab = page.locator("#tab-cancelled")
        expect(cancelled_tab).to_have_attribute("aria-selected", "false")

        # Verify panel association
        active_panel = page.locator("#active")
        expect(active_panel).to_have_attribute("role", "tabpanel")
        expect(active_panel).to_have_attribute("aria-labelledby", "tab-active")
        expect(active_panel).to_be_visible()

        # Click Cancelled tab
        cancelled_tab.click()

        # Verify state change
        expect(active_tab).to_have_attribute("aria-selected", "false")
        expect(cancelled_tab).to_have_attribute("aria-selected", "true")

        expect(active_panel).not_to_be_visible()
        cancelled_panel = page.locator("#cancelled")
        expect(cancelled_panel).to_be_visible()

        # Take screenshot
        page.screenshot(path="verification/tabs_verification.png")
        print("Verification successful!")

        browser.close()

if __name__ == "__main__":
    verify_tabs()
