import re
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from .utils import screenshot_to_base64, VISION_MODEL, llm_client


def smart_click(page: Page, element_desc: str, max_retries: int = 2) -> bool:
    """
    智能点击：DOM定位优先，失败自动切换视觉定位
    element_desc: 元素的自然语言描述，比如"登录按钮"、"提交工单的按钮"
    """
    for attempt in range(max_retries + 1):
        try:
            # 第一轮：DOM语义定位
            if attempt == 0:
                locators = [
                    page.get_by_role("button", name=element_desc),
                    page.get_by_text(element_desc, exact=False),
                    page.get_by_label(element_desc)
                ]
                for locator in locators:
                    try:
                        locator.wait_for(timeout=2000)
                        locator.click()
                        return True
                    except PlaywrightTimeoutError:
                        continue
            
            # 第二轮及以后：视觉定位兜底
            else:
                base64_img = screenshot_to_base64(page)
                response = llm_client.chat.completions.create(
                    model=VISION_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"请在图中找到【{element_desc}】的位置，只返回中心点坐标，格式为 x,y 两个数字，不要其他文字"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_img}"}}
                            ]
                        }
                    ],
                    temperature=0
                )
                
                coord_text = response.choices[0].message.content.strip()
                try:
                    x, y = map(float, coord_text.split(","))
                    page.mouse.click(x, y)
                    return True
                except Exception:
                    continue
                    
        except Exception as e:
            if attempt == max_retries:
                raise RuntimeError(f"元素定位失败，描述：{element_desc}，错误：{str(e)}")
    return False


def auto_handle_popup(page: Page, timeout: int = 3000) -> bool:
    """自动识别并处理弹窗、Toast、Loading"""
    try:
        page.wait_for_selector("[role='dialog']", timeout=timeout)
        close_btn = page.get_by_role("button", name=re.compile("关闭|确定|确认|OK", re.IGNORECASE))
        if close_btn.count() > 0:
            close_btn.first.click()
            return True
    except PlaywrightTimeoutError:
        pass
    
    try:
        page.wait_for_selector(".loading, [role='progressbar']", state="hidden", timeout=timeout)
    except PlaywrightTimeoutError:
        pass
    
    return False

