import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def test_empty_todo_item():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to the target URL
            page.goto('https://demo.playwright.dev/todomvc/')
            
            # Wait for initial content load (implicit wait via Playwright's auto-waiting)
            input_field = page.get_by_placeholder("What needs to be done?")
            
            if not input_field.is_visible():
                raise Exception("Input field is not visible on the page.")
                
            # Press Enter without typing anything
            input_field.press('Enter')
            
            # Wait for DOM updates (implicit wait)
            items = page.locator('li').all()
            
            if len(items) > 0:
                raise AssertionError(f"Expected no todo items, but found {len(items)}")
                
        except PlaywrightTimeout as e:
            print(f"Operation timed out after default timeout period.")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    test_empty_todo_item()