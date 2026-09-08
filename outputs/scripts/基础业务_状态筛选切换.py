from playwright.sync_api import sync_playwright, expect
import sys

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 导航到目标页面并等待加载完成
            page.goto("https://demo.playwright.dev/todomvc/")
            
            input_field = None
            for _ in range(3):  # 最多尝试3次获取输入框
                try:
                    input_field = page.get_by_placeholder("What needs to be done?")
                    break
                except Exception as e:
                    print(f"Warning: Input field not found, retrying... {e}")
            
            if not expect(input_field).to_be_visible(timeout=5000):
                raise RuntimeError("Input field could not be located after retries.")

            # 添加两个任务
            tasks = ["任务 1", "任务 2"]
            for task in tasks:
                input_field.fill(task)
                page.keyboard.press('Enter')
                
                if expect(page.get_by_text(task)).to_be_visible(timeout=5000):
                    print(f"Task '{task}' added successfully.")
                else:
                    raise RuntimeError(f"Failed to add task: {task}")

            # 标记第一个任务为完成状态
            first_task_checkbox = page.locator('.todo-list li').first.get_by_role("checkbox")
            if expect(first_task_checkbox).to_be_visible(timeout=5000):
                print("First checkbox found, marking as complete.")
                first_task_checkbox.click()
            else:
                raise RuntimeError("Checkbox for the first task not located.")

            # 点击Completed筛选按钮
            completed_filter = page.get_by_text("Completed")
            if expect(completed_filter).to_be_visible(timeout=5000):
                print("Clicked Completed filter button.")
                completed_filter.click()
                
                # 等待页面更新并验证结果
                await page.wait_for_timeout(100)
                list_items = page.locator('.todo-list li')
                
                if expect(list_items).to_have_count(count=1, timeout=5000):
                    print("Only one completed task remains in the filtered view.")
                    
                    # 验证剩余任务内容正确性
                    remaining_task_text = list_items.first.get_by_text()
                    if "任务 1" not in str(remaining_task_text):
                        raise AssertionError(f"Incorrect task content: {remaining_task_text}")
                else:
                    current_count = len(list_items)
                    print(f"Warning: Expected only 1 item, found {current_count} items.")

            browser.close()
            
        except Exception as e:
            if 'browser' in locals():
                browser.close()
            sys.exit(1)

if __name__ == "__main__":
    main()