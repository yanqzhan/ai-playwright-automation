from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True可改为无头模式测试
        page = browser.new_page()
        
        try:
            page.goto("https://demo.playwright.dev/todomvc/")
            
            input_field = page.get_by_placeholder("What needs to done?")
            assert input_field.is_visible(), "输入框未找到"

            # 添加3条任务
            for i in range(1, 4):
                task_text = f"Task {i}"
                input_field.fill(task_text)
                page.press('textarea', 'Enter')  # 按回车提交或page.click(input_field.locator("button[type='submit']"))

            checkboxes = page.get_by_role("checkbox").all()
            
            # 标记前2条任务为完成
            for i in range(2):
                try:
                    checkbox = checkboxes[i]
                    if not checkbox.is_checked():
                        checkbox.click(timeout=500)
                except PlaywrightTimeout as e:
                    print(f"第{i+1}个复选框操作超时：{e}")

            # 点击清除完成按钮
            clear_button = page.get_by_text("Clear completed")
            if clear_button.is_enabled():
                clear_button.click()

            # 验证所有任务未被标记为完成
            remaining_checkboxes = checkboxes.all()
            for checkbox in remaining_checkboxes:
                assert not checkbox.is_checked(), "仍有已完成的任务存在"
            
            print("测试通过：所有已完成任务已被清空")
        
        except Exception as e:
            print(f"发生错误：{e}")
            raise

if __name__ == "__main__":
    run_test()