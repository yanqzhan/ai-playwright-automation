from playwright.sync_api import sync_playwright
from .utils import extract_dom_elements, LLM_MODEL, save_script, llm_client


def generate_playwright_script(url: str, user_prompt: str, script_name: str = "auto_test") -> str:
    """自然语言 + 页面DOM 自动生成完整Playwright脚本"""
    # 1. 打开页面提取元素
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        dom_elements = extract_dom_elements(page)
        browser.close()
    
    # 2. 构造Prompt，要求生成稳定、规范的Python脚本
    system_prompt = """
你是专业的Playwright自动化测试脚本生成专家。请根据用户需求和页面元素列表，生成完整可运行的Python Playwright代码。
要求：
1. 优先使用 get_by_role()、get_by_text()、get_by_label() 等稳定定位器，禁止使用脆弱的xpath和随机id
2. 自动加入合理的等待逻辑，不要使用硬等待
3. 代码结构清晰，包含浏览器启动、页面跳转、操作步骤、基础断言
4. 只输出代码，不要多余解释，代码开头加上必要的import
5. 异常捕获和错误处理要完善
"""
    
    user_content = f"""
目标页面URL: {url}
页面可交互元素列表:
{dom_elements}

用户需求: {user_prompt}

请生成完整的Playwright Python脚本。
"""
    
    # 3. 调用大模型生成代码
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2
    )
    
    script_code = response.choices[0].message.content.strip()
    # 清理代码块标记
    script_code = script_code.replace("```python", "").replace("```", "").strip()
    
    # 4. 保存脚本
    save_script(script_code, script_name)
    return script_code


def generate_boundary_cases(url: str, base_prompt: str) -> list:
    """基于业务页面自动生成边界用例脚本"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        dom_elements = extract_dom_elements(page)
        browser.close()
    
    system_prompt = """
基于页面表单元素，生成3组边界测试用例描述：
1. 空输入场景
2. 超长文本/非法格式场景
3. 特殊字符场景
只输出用例描述列表，每行一个用例
"""
    
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"页面元素:\n{dom_elements}\n基础场景:{base_prompt}"}
        ]
    )
    
    cases = [line.strip() for line in response.choices[0].message.content.strip().split("\n") if line.strip()]
    return cases

