
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Intercept network requests
        page.route('**/api/subscriptions', lambda route: route.fulfill(
            status=200,
            content_type='application/json',
            body='''[{
                "id": 1,
                "service_name": "Test Netflix",
                "cost": 15.99,
                "currency": "USD",
                "billing_cycle": "monthly",
                "category": "Entertainment",
                "status": "active",
                "source_email_from": "info@netflix.com",
                "source_email_subject": "Your bill",
                "confidence_score": 0.95
            }]'''
        ))

        url = 'http://localhost:8081/index.html'
        page.goto(url)
        page.wait_for_timeout(1000)

        page.click('text=Details')
        page.wait_for_selector('#email-modal.active')

        # Verify input
        count = page.locator('#edit-cost').count()
        print(f'Edit Cost Input Count: {count}')

        if count == 0:
            print('ERROR: Input missing!')
        else:
            print('SUCCESS: Input present.')

        page.screenshot(path='verification/modal_final_proof.png')
        browser.close()

if __name__ == '__main__':
    run()
