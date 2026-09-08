from playwright.sync_api import sync_playwright, expect

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        try:
            # Navigate to the TodoMVC demo app and wait for load completion
            page.goto("https://demo.playwright.dev/todomvc/")
            
            # Locate input field by placeholder text
            input_field = page.get_by_placeholder("What needs to be done?")
            
            # Enter task name and submit via keyboard event (Enter key)
            input_field.fill("测试删除功能")
            input_field.press('Enter')

            # Wait for new task item to appear in the list
            task_item = page.locator('.todo-list li').filter(has_text="测试删除功能").first
            
            # Hover over the task item to reveal delete button
            task_item.hover()
            
            # Locate and click the delete link/button (adjust selector based on actual DOM structure)
            try:
                delete_button = task_item.get_by_role("link", name="delete") or \
                               page.locator('.todo-list li').filter(has_text="测试删除功能").get_by_test_id('destroy') or \
                               page.locator(".destroy").first
                
                # Click the delete button with timeout for visibility check
                expect(delete_button).to_be_visible(timeout=500)
                delete_button.click()

            except Exception as e:
                print(f"删除按钮未找到或不可见，错误信息：{e}")
                raise AssertionError("