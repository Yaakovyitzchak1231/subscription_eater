
from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = 'file://' + os.path.abspath('index.html')
        page.goto(url)

        page.evaluate('''
            // Mock data
            window.subscriptions = [
                {
                    id: 1,
                    service_name: 'Test Netflix',
                    cost: 15.99,
                    currency: 'USD',
                    billing_cycle: 'monthly',
                    category: 'Entertainment',
                    status: 'active',
                    source_email_from: 'info@netflix.com',
                    source_email_subject: 'Your bill',
                    confidence_score: 0.95
                }
            ];

            // Populate modal
            showEmailDetails(1);
        ''')

        # Verify inputs exist
        inputs = page.locator('input').count()
        print(f'Total inputs found in modal: {inputs}')

        # Verify specific inputs
        # Use simple locators to avoid f-string issues in my echo
        has_cost = page.locator('#edit-cost').count() > 0
        has_curr = page.locator('#edit-currency').count() > 0
        has_cycle = page.locator('#edit-cycle').count() > 0

        print(f'Edit cost exists: {has_cost}')
        print(f'Edit currency exists: {has_curr}')
        print(f'Edit cycle exists: {has_cycle}')

        page.screenshot(path='verification/modal_content_check.png')
        browser.close()

if __name__ == '__main__':
    run()
