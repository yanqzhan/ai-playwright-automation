import traceback
from .utils import parse_trace_file, LLM_MODEL, llm_client


def run_test_script(script_path: str, enable_trace: bool = True) -> dict:
    """执行测试脚本，录制trace，捕获结果"""
    trace_path = script_path.replace("scripts", "traces").replace(".py", "_trace.zip")
    
    # 给脚本注入trace录制逻辑
    with open(script_path, "r", encoding="utf-8") as f:
        original_code = f.read()
    
    # 注入trace代码
    trace_inject = f"""
import os
context.tracing.start(screenshots=True, snapshots=True, sources=True)
try:
    pass
finally:
    os.makedirs(os.path.dirname("{trace_path}"), exist_ok=True)
    context.tracing.stop(path="{trace_path}")
"""
    # 简单替换实现（实际项目建议用AST修改）
    modified_code = original_code.replace(
        "page = context.new_page()",
        f"page = context.new_page()\n    {trace_inject}"
    )
    
    # 执行脚本
    result = {"success": False, "error": "", "trace_path": trace_path}
    try:
        exec(modified_code, {})
        result["success"] = True
    except Exception as e:
        result["error"] = traceback.format_exc()
    
    return result


def analyze_failure(trace_path: str, error_msg: str) -> dict:
    """AI分析失败原因，给出修复建议"""
    trace_info = parse_trace_file(trace_path)
    
    system_prompt = """
你是自动化测试故障分析专家。请根据错误日志和trace信息，判断失败原因并给出修复建议。
请按以下格式输出：
失败类型：[产品Bug/网络抖动/时序问题/选择器失效/断言不匹配]
原因分析：
修复建议：
"""
    
    user_content = f"""
错误信息:
{error_msg}

Trace摘要:
{trace_info.get("raw_trace", "")[:3000]}

请分析失败原因并给出解决方案。
"""
    
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.3
    )
    
    analysis = response.choices[0].message.content.strip()
    
    # 结构化解析
    result = {"raw_analysis": analysis}
    for line in analysis.split("\n"):
        if line.startswith("失败类型："):
            result["failure_type"] = line.replace("失败类型：", "").strip()
        elif line.startswith("原因分析："):
            result["reason"] = line.replace("原因分析：", "").strip()
        elif line.startswith("修复建议："):
            result["suggestion"] = line.replace("修复建议：", "").strip()
    
    return result


def detect_flaky(script_path: str, retry_times: int = 3) -> dict:
    """检测不稳定用例（flaky）"""
    results = []
    for i in range(retry_times):
        res = run_test_script(script_path, enable_trace=False)
        results.append(res["success"])
    
    success_count = sum(results)
    is_flaky = success_count > 0 and success_count < retry_times
    
    return {
        "is_flaky": is_flaky,
        "success_rate": f"{success_count}/{retry_times}",
        "results": results
    }

