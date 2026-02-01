import os
import json
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock subscriptions
        subscriptions = [
            {
                "id": 1,
                "service_name": "Test Service",
                "status": "active",
                "cost": 10.0,
                "currency": "USD",
                "billing_cycle": "monthly",
                "source_email_from": "test@example.com",
                "source_email_subject": "Invoice",
                "confidence_score": 0.9,
                "category": "Utilities",
                "renewal_date": "2023-10-01"
            }
        ]

        page.add_init_script("window.BACKEND_URL = 'http://mock-backend/api';")

        def handle_subscriptions(route):
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(subscriptions)
            )

        page.route("**/subscriptions", handle_subscriptions)

        cwd = os.getcwd()
        file_path = f"file://{cwd}/legacy-index.html"
        page.goto(file_path)

        page.wait_for_selector(".subscription-item")

        # Verify List Button aria-label
        details_btn = page.locator(".subscription-item button")
        details_label = details_btn.get_attribute("aria-label")
        print(f"Details button aria-label: {details_label}")

        details_btn.click()

        modal = page.wait_for_selector("#email-modal .modal-content")

        # Verify Close Button aria-label
        close_btn = page.locator(".modal-close")
        close_label = close_btn.get_attribute("aria-label")
        print(f"Close button aria-label: {close_label}")

        # Scroll to bottom
        page.evaluate("document.querySelector('.modal-content').scrollTop = document.querySelector('.modal-content').scrollHeight")

        # Verify Delete Button
        delete_btn = page.locator("#delete-btn")
        if delete_btn.is_visible():
            print("Delete button is visible")
            print(f"Delete button text: {delete_btn.inner_text()}")
        else:
            print("Delete button is NOT visible")

        # Screenshot
        output_path = "verification/legacy_modal_footer.png"
        modal.screenshot(path=output_path)
        print(f"Screenshot saved to {output_path}")

        browser.close()

if __name__ == "__main__":
    run()
