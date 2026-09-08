import sys
from playwright.sync_api import sync_playwright, expect

def main():
    try:
        with sync_playwright() as p:
            # 启动浏览器，设置 headless=False 以便观察（如需 CI 可改为 True）
            browser = p.chromium.launch(headless=True) 
            page = browser.new_page()
            
            url = "https://demo.playwright.dev/todomvc/"
            
            try:
                print(f"正在访问页面：{url}")
                # 导航到目标页面，等待 DOM 加载完成（Playwright 默认有超时机制）
                page.goto(url, wait_until="networkidle")

                # 使用稳定的 placeholder 定位器获取输入框
                input_field = page.get_by_placeholder("What needs to be done?")
                
                test_content = "测试 @#$😀"
                print(f"正在输入内容：{test_content}")
                
                # 填充文本并模拟回车提交（TodoMVC 通常支持按 Enter 添加）
                input_field.fill(test_content)
                input_field.press("Enter")

                # 等待新任务项出现在列表中，避免竞态条件
                page.wait_for_selector("#todo-list li", timeout=5000, state="attached")

                # 验证内容是否显示在待办事项列表中（通过检查列表容器内的文本）
                todo_list = page.locator("ul#todo-list").first
                
                try:
                    expect(todo_list).to_contain_text(test_content)
                    print(f"✅ 验证成功：任务 '{test_content}' 已正常添加并显示。")
                    
                    # 额外断言：检查输入框是否为空（提交后通常清空）
                    input_field.clear() 
                except Exception as e:
                    raise AssertionError(f"内容未正确显示在列表中，可能原因：DOM 结构变化或渲染问题。\n错误详情：{e}")

            finally:
                browser.close()
                
    except TimeoutError as te:
        print(f"❌ 超时错误：操作未在预期时间内完成。")
        sys.exit(1)
    except Exception as e:
        # 捕获其他通用异常，确保脚本优雅退出并打印堆栈信息（可选）
        print(f"⚠️ 发生未预期的运行时错误：{e}")

if __name__ == "__main__":
    main()