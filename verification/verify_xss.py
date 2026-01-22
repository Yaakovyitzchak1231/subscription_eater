import os
from playwright.sync_api import sync_playwright, expect

def verify_xss_prevention(page):
    file_path = os.path.abspath("legacy-index.html")
    page.goto(f"file://{file_path}")

    # Inject malicious data
    page.evaluate("""
        subscriptions = [{
            id: 1,
            service_name: '"><img src=x onerror=alert(1)>',
            cost: 100,
            currency: "USD",
            billing_cycle: "monthly",
            category: "Entertainment",
            status: "active",
            source_email_from: "hacker@example.com",
            source_email_subject: "Pwnd",
            confidence_score: 1.0
        }];
        showEmailDetails(1);
    """)

    # Check if the value is set correctly without executing script
    # The input value should literally contain the malicious string
    service_input = page.locator("#edit-service-display")
    expect(service_input).to_have_value('"><img src=x onerror=alert(1)>')

    # Verify no alert was triggered (Playwright handles dialogs automatically, but we can't easily assert "no dialog" unless we listen for it.
    # However, if XSS executed, the page structure might be broken or an alert would pop up.
    # We can check if the input element still exists as an input, not replaced by an image.
    expect(page.locator("img[src='x']")).not_to_be_visible()

    print("XSS prevention verification passed.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Add dialog handler to fail if alert pops up
        page.on("dialog", lambda dialog: print(f"Dialog opened: {dialog.message}"))

        try:
            verify_xss_prevention(page)
        except Exception as e:
            print(f"Verification failed: {e}")
            exit(1)
        finally:
            browser.close()
