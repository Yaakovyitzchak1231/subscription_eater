
from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on('console', lambda msg: print(f'Console: {msg.text}'))

        url = 'file://' + os.path.abspath('index.html')
        page.goto(url)

        page.evaluate('''
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

            // Redefine to debug
            window.showEmailDetails = function(id) {
                console.log('Called with ID:', id);
                console.log('Subscriptions:', JSON.stringify(window.subscriptions));
                const sub = window.subscriptions.find(s => s.id === id);
                console.log('Found sub:', sub);

                if (!sub) return;

                const body = document.getElementById('modal-body');
                console.log('Body element:', body);

                body.innerHTML = '<h1>TEST CONTENT</h1>';
                console.log('Set content to TEST CONTENT');
            }

            showEmailDetails(1);
        ''')

        html = page.evaluate('document.getElementById("modal-body").innerHTML')
        print(f'Modal Body HTML: {html}')

        browser.close()

if __name__ == '__main__':
    run()
