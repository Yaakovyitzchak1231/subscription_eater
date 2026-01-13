
from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Enable console logs
        page.on('console', lambda msg: print(f'Console: {msg.text}'))
        page.on('pageerror', lambda msg: print(f'PageError: {msg}'))

        url = 'file://' + os.path.abspath('index.html')
        print(f'Loading {url}')

        page.goto(url)

        print('Page loaded, injecting data...')

        page.evaluate('''
            // Reset subscriptions
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

            console.log('Calling showEmailDetails(1)');
            try {
                showEmailDetails(1);
            } catch (e) {
                console.error('Error in showEmailDetails:', e);
            }
        ''')

        # Debug: Dump HTML of modal body
        html = page.evaluate('document.getElementById("modal-body").innerHTML')
        print(f'Modal Body HTML: {html}')

        browser.close()

if __name__ == '__main__':
    run()
