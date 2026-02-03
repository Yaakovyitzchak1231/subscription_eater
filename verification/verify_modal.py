from playwright.sync_api import sync_playwright
import os
import json

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Path to the legacy-index.html file
        file_path = os.path.abspath("legacy-index.html")

        # Define mock data
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
            "confidence_score": 0.95,
            "renewal_date": "2023-12-01"
        }]

        # Inject mock fetch before page loads
        # We need to make sure mock_subs is properly formatted as JSON string for JS injection
        mock_subs_json = json.dumps(mock_subs)

        page.add_init_script(f"""
            window.BACKEND_URL = 'http://mock-backend';

            // Mock fetch
            const originalFetch = window.fetch;
            window.fetch = async (url, options) => {{
                console.log("Fetching:", url);
                if (url.includes('/subscriptions') && (!options || options.method === 'GET' || !options.method)) {{
                    return {{
                        ok: true,
                        json: async () => ({mock_subs_json})
                    }};
                }}
                return {{ ok: false, status: 404 }};
            }};
        """)

        print(f"Loading file://{file_path}")
        page.goto(f"file://{file_path}")

        # Wait for the subscription to appear
        # The script loads fetchSubscriptions on window.onload
        try:
            page.wait_for_selector(".subscription-item", timeout=5000)
            print("Subscriptions loaded.")
        except Exception as e:
            print("Timed out waiting for subscription-item. Dumping console logs.")
            # We can't dump console logs easily in sync mode without listener, but we proceed.
            raise e

        # Click Details
        page.get_by_role("button", name="Details").click()
        print("Clicked Details.")

        # Wait for modal
        page.wait_for_selector("#email-modal.active")
        print("Modal opened.")

        # Verify Close Button ARIA label
        close_btn = page.locator(".modal-close")
        aria_label = close_btn.get_attribute("aria-label")
        assert aria_label == "Close modal", f"Expected 'Close modal', got '{aria_label}'"
        print("Verified Close Button ARIA label.")

        # Verify Save Button is visible
        save_btn = page.locator("#save-btn")
        assert save_btn.is_visible(), "Save Changes button is not visible"
        print("Verified Save Changes button is visible.")

        # Verify saveSubscription function exists
        is_defined = page.evaluate("typeof saveSubscription === 'function'")
        assert is_defined, "saveSubscription function is not defined"
        print("Verified saveSubscription function exists.")

        # Verify Labels have 'for' attributes
        labels = [
            "edit-service-name",
            "edit-cost",
            "edit-currency",
            "edit-cycle",
            "edit-category",
            "edit-status"
        ]

        for label_for in labels:
            label = page.locator(f"label[for='{label_for}']")
            assert label.is_visible(), f"Label for '{label_for}' not found or not visible"
            print(f"Verified label for {label_for}")

        # Check for duplicates?
        # We can check if 'edit-cost' ID is unique
        cost_inputs = page.locator("#edit-cost").count()
        assert cost_inputs == 1, f"Expected 1 input with id='edit-cost', found {cost_inputs}"
        print("Verified unique ID for edit-cost.")

        # Take screenshot
        screenshot_path = os.path.abspath("verification/modal_verified.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run()
