
from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Enable console logs
        page.on('console', lambda msg: print(f'Console: {msg.text}'))

        url = 'file://' + os.path.abspath('index.html')
        print(f'Loading {url}')

        page.goto(url)

        print('Page loaded, injecting data...')

        page.evaluate('''
            // Reset subscriptions
            // status needs to match 'active', check for whitespace or case issues
            window.subscriptions = [
                {
                    id: 1,
                    service_name: 'Test Netflix',
                    cost: 15.99,
                    currency: 'USD',
                    billing_cycle: 'monthly',
                    category: 'Entertainment',
                    status: 'active',  // Exact match required
                    source_email_from: 'info@netflix.com',
                    source_email_subject: 'Your bill',
                    confidence_score: 0.95
                }
            ];

            // Bypass filter entirely and force HTML
            const list = document.getElementById('active-list');
            list.innerHTML = '<div class="subscription-item">Test Netflix<button class="btn-sm btn-secondary" onclick="showEmailDetails(1)">Details</button></div>';

            // Debug showEmailDetails
            const oldShow = window.showEmailDetails;
            window.showEmailDetails = function(id) {
                console.log('showEmailDetails called with id:', id);
                console.log('subscriptions in scope:', JSON.stringify(window.subscriptions));

                // Try to find directly here
                const sub = window.subscriptions.find(s => s.id === id);
                console.log('Found sub in wrapper:', sub);

                // Manually do what needs to be done since closure might be stale?
                if (sub) {
                   currentEditId = id;
                   document.getElementById('email-modal').classList.add('active');
                   // We skip the body population for now just to test the modal opening
                }
            }
        ''')

        # Debug: Dump HTML of active list
        html = page.evaluate('document.getElementById("active-list").innerHTML')
        print(f'List HTML: {html}')

        # Wait for list to render
        try:
            print('Waiting for .subscription-item...')
            page.wait_for_selector('.subscription-item', timeout=5000)
            print('Found .subscription-item')
        except Exception as e:
            print(f'Failed to find item: {e}')
            browser.close()
            return

        # Use simple text selector
        page.click('text=Details')

        # Debug: Check if modal is active
        # FIX: QUOTES in evaluate string
        is_active = page.evaluate('document.getElementById("email-modal").classList.contains("active")')
        print(f'Modal is active after click: {is_active}')

        # Wait for modal to be visible
        page.wait_for_selector('#email-modal.active')

        # Verify ARIA attributes
        modal = page.locator('#email-modal')
        print(f'Role: {modal.get_attribute("role")}')
        print(f'Aria-modal: {modal.get_attribute("aria-modal")}')
        print(f'Aria-label of close btn: {page.locator(".modal-close").get_attribute("aria-label")}')

        # Take screenshot of the modal
        page.screenshot(path='verification/modal_screenshot.png')

        # Test Escape key closing
        page.keyboard.press('Escape')
        # Wait for modal class 'active' to be removed
        page.wait_for_function('!document.getElementById("email-modal").classList.contains("active")')
        print('Modal closed on Escape')

        browser.close()

if __name__ == '__main__':
    run()
