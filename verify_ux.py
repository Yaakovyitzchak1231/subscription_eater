
import os
from playwright.sync_api import sync_playwright

def verify_ux():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock backend URL
        page.add_init_script("window.BACKEND_URL = 'http://mock-backend/api';")

        # Mock subscriptions
        mock_subs = [{
            "id": 1,
            "service_name": "Netflix",
            "cost": 15.99,
            "currency": "USD",
            "billing_cycle": "monthly",
            "category": "Entertainment",
            "status": "active",
            "source_email_from": "info@netflix.com",
            "source_email_subject": "Your receipt",
            "confidence_score": 0.99,
            "renewal_date": "2023-12-01"
        }]

        page.route("**/subscriptions", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=str(mock_subs).replace("'", '"')
        ))

        # Load file
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/legacy-index.html")

        # Check theme toggle aria-label
        toggle = page.locator("#theme-toggle")
        print(f"Theme toggle aria-label: {toggle.get_attribute('aria-label')}")
        assert toggle.get_attribute("aria-label") == "Toggle theme"

        # Open modal
        page.click("button:text('Details')")

        # Check focus
        focused = page.evaluate("document.activeElement.id")
        print(f"Focused element ID: {focused}")
        assert focused == "edit-cost"

        # Check modal close aria-label
        close_btn = page.locator(".modal-close")
        print(f"Close button aria-label: {close_btn.get_attribute('aria-label')}")
        assert close_btn.get_attribute("aria-label") == "Close modal"

        # Screenshot
        os.makedirs("verification", exist_ok=True)
        page.screenshot(path="verification/modal_ux.png")
        print("Screenshot saved to verification/modal_ux.png")

        browser.close()

if __name__ == "__main__":
    verify_ux()
