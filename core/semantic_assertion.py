from playwright.sync_api import Page
from .utils import LLM_MODEL, llm_client


def semantic_expect(page: Page, assertion_desc: str) -> dict:
    """
    语义断言：不用硬编码文本，用自然语言描述断言
    例如："页面显示操作成功提示"、"列表中新增了一条数据"
    """
    # 提取页面可见文本
    page_text = page.inner_text("body")[:3000]
    
    system_prompt = """
你是语义断言判断引擎。请根据页面文本内容，判断用户的断言描述是否成立。
输出格式：
是否通过：是/否
判断依据：
"""
    
    user_content = f"""
页面全部可见文本:
{page_text}

断言描述: {assertion_desc}

请判断该断言是否成立。
"""
    
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0
    )
    
    result_text = response.choices[0].message.content.strip()
    result = {"raw_result": result_text, "passed": False, "reason": ""}
    
    for line in result_text.split("\n"):
        if line.startswith("是否通过："):
            result["passed"] = "是" in line
        elif line.startswith("判断依据："):
            result["reason"] = line.replace("判断依据：", "").strip()
    
    return result

