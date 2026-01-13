
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on('console', lambda msg: print(f'Console: {msg.text}'))

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

        url = 'http://localhost:8080/index.html'
        print(f'Loading {url}')

        page.goto(url)
        page.wait_for_timeout(1000)

        try:
            page.click('text=Details', timeout=2000)
            print('Clicked Details')
        except:
            print('Failed to click details')
            html = page.evaluate('document.getElementById("active-list").innerHTML')
            print(f'List HTML: {html}')
            return

        page.wait_for_selector('#email-modal.active')

        # Check modal content
        html = page.evaluate('document.getElementById("modal-body").innerHTML')
        # print(f'Modal Body HTML: {html}')

        # Verify specific inputs exist
        has_cost = page.locator('#edit-cost').count() > 0
        print(f'Edit cost exists: {has_cost}')

        page.screenshot(path='verification/modal_correct.png')

        browser.close()

if __name__ == '__main__':
    run()
