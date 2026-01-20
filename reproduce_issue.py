
import os
import json
from playwright.sync_api import sync_playwright, expect

def test_modal_layout(page):
    # Set BACKEND_URL to a dummy HTTP URL so we can intercept it
    page.add_init_script("window.BACKEND_URL = 'http://api.local/api';")

    # Load the local file
    cwd = os.getcwd()
    file_path = f"file://{cwd}/legacy-index.html"

    # Mock the fetch response
    mock_subs = [
        {
            "id": 1,
            "service_name": "Netflix",
            "cost": 15.99,
            "currency": "USD",
            "billing_cycle": "monthly",
            "category": "Entertainment",
            "status": "active",
            "source_email_from": "info@netflix.com",
            "source_email_subject": "Your receipt",
            "confidence_score": 0.95
        }
    ]

    # Intercept network requests to our dummy backend
    page.route("**/subscriptions", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(mock_subs)
    ))

    # Log console messages to help debug
    page.on("console", lambda msg: print(f"Console: {msg.text}"))
    page.on("pageerror", lambda err: print(f"Page Error: {err}"))

    page.goto(file_path)

    # Click details button (might need to wait for it to appear)
    details_btn = page.locator(".subscription-actions button").first
    details_btn.wait_for(timeout=5000)
    details_btn.click()

    # Wait for modal to appear
    modal = page.locator("#email-modal")
    expect(modal).to_be_visible()

    # Take screenshot of the modal
    page.screenshot(path="/home/jules/verification/modal_issue.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        # Disable web security to allow file:// to fetch http://
        browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
        page = browser.new_page()
        try:
            test_modal_layout(page)
            print("Screenshot taken: /home/jules/verification/modal_issue.png")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
