from playwright.sync_api import sync_playwright, expect
import pytest


def test_add_todo_item():
    """添加待办事项并验证成功"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 使用有头模式便于调试，可改为headless=True优化性能
        page = browser.new_page()

        try:
            # 打开目标页面
            page.goto("https://demo.playwright.dev/todomvc/")
            
            # 等待输入框加载完成（自动隐式等待）
            input_box = page.get_by_placeholder("What needs to be done?")
            expect(input_box).to_be_visible()

            # 填写待办内容并提交
            input_box.fill("学习 Playwright 自动化")
            page.keyboard.press('Enter')

            # 验证新增任务项存在（等待列表更新）
            task_locator = page.locator('.todo-list li').filter(has_text="学习 Playwright 自动化")
            expect(task_locator).to_be_visible()

        except Exception as e:
            print(f"测试执行失败：{e}")
            raise AssertionError("待办事项添加或验证过程出现异常", str(e)) from None
        
        finally:
            browser.close()


if __name__ == "__main__":
    test_add_todo_item()