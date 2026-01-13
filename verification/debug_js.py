
from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Enable console logs
        page.on('console', lambda msg: print(f'Console: {msg.text}'))

        url = 'file://' + os.path.abspath('index.html')
        page.goto(url)

        page.evaluate('''
            // Check if subscriptions exists
            console.log('Subs length before:', window.subscriptions ? window.subscriptions.length : 'undefined');

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

            console.log('Subs length after:', window.subscriptions.length);

            // Check if showEmailDetails exists
            console.log('showEmailDetails exists:', typeof showEmailDetails);

            // Call it
            showEmailDetails(1);

            // Check body immediately
            console.log('Body HTML length:', document.getElementById('modal-body').innerHTML.length);
        ''')

        browser.close()

if __name__ == '__main__':
    run()
