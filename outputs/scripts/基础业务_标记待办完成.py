import asyncio
from playwright.sync_api import sync_playwright, expect

def test_mark_todo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 打开页面并等待初始加载完成
            page.goto("https://demo.playwright.dev/todomvc/")
            page.wait_for_selector("#todo-input")

            input_box = page.get_by_placeholder("What needs to be done?")
            
            if not input_box.is_enabled():
                raise Exception("输入框不可用，无法继续操作。")

            # 填写待办事项并提交
            input_box.fill("测试标记功能")
            page.keyboard.press('Enter')

            # 等待新任务项出现（确保提交成功）
            page.wait_for_selector(".todo-list li", timeout=5000) 

            checkbox = page.get_by_role("checkbox").first
            
            if not checkbox.is_enabled():
                raise Exception("复选框不可用，无法点击。")

            # 标记为完成并验证状态
            checkbox.click()
            
            expect(checkbox).to_be_checked()

        except Exception as e:
            print(f"发生错误：{e}")
            browser.close()
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_mark_todo()