import streamlit as st
import os
from core.script_generator import generate_playwright_script, generate_boundary_cases
from core.execution_engine import run_test_script, analyze_failure, detect_flaky
from core.semantic_assertion import semantic_expect
from core.intelligent_locator import smart_click
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="AI + Playwright 智能自动化平台", layout="wide")
st.title("🤖 AI + Playwright 智能自动化测试平台")

# 侧边栏导航
tab = st.sidebar.radio("功能模块", [
    "📝 脚本生成工作台",
    "▶️ 测试执行中心",
    "🔍 故障分析",
    "💬 语义断言",
    "🧩 低代码模式"
])

# ------------------- 脚本生成工作台 -------------------
if tab == "📝 脚本生成工作台":
    st.header("自然语言生成测试脚本")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        target_url = st.text_input("目标页面URL", "https://example.com")
        user_prompt = st.text_area("操作需求（自然语言）", "登录系统，新建一条工单，填写标题和内容后提交")
        script_name = st.text_input("脚本名称", "auto_workorder")
        generate_btn = st.button("🚀 生成脚本", type="primary")
    
    with col2:
        st.subheader("生成的脚本代码")
        if generate_btn and target_url and user_prompt:
            with st.spinner("正在分析页面并生成脚本..."):
                script_code = generate_playwright_script(target_url, user_prompt, script_name)
                st.code(script_code, language="python")
                
                # 边界用例生成
                st.subheader("自动生成的边界用例")
                boundary_cases = generate_boundary_cases(target_url, user_prompt)
                for i, case in enumerate(boundary_cases):
                    st.write(f"{i+1}. {case}")
        else:
            st.info("请输入URL和操作需求后点击生成")

# ------------------- 测试执行中心 -------------------
elif tab == "▶️ 测试执行中心":
    st.header("测试执行与管理")
    
    script_files = os.listdir("outputs/scripts")
    if not script_files:
        st.info("暂无生成的脚本，请先去脚本生成工作台创建")
    else:
        selected_script = st.selectbox("选择要执行的脚本", script_files)
        script_path = f"outputs/scripts/{selected_script}"
        
        col1, col2 = st.columns(2)
        with col1:
            run_btn = st.button("▶️ 执行脚本", type="primary")
        with col2:
            flaky_btn = st.button("🔄 稳定性检测(3次重试)")
        
        if run_btn:
            with st.spinner("正在执行脚本..."):
                result = run_test_script(script_path)
                if result["success"]:
                    st.success("✅ 脚本执行成功")
                else:
                    st.error("❌ 脚本执行失败")
                    st.text_area("错误信息", result["error"], height=200)
                    st.session_state["last_trace"] = result["trace_path"]
                    st.session_state["last_error"] = result["error"]
        
        if flaky_btn:
            with st.spinner("正在进行稳定性检测..."):
                flaky_result = detect_flaky(script_path)
                if flaky_result["is_flaky"]:
                    st.warning(f"⚠️ 检测为不稳定用例，成功率：{flaky_result['success_rate']}")
                else:
                    st.success(f"✅ 用例稳定，成功率：{flaky_result['success_rate']}")

# ------------------- 故障分析 -------------------
elif tab == "🔍 故障分析":
    st.header("AI 故障智能分析")
    
    if "last_trace" in st.session_state and os.path.exists(st.session_state["last_trace"]):
        st.info("检测到上次执行的失败记录，自动分析中...")
        if st.button("开始AI分析"):
            with st.spinner("正在分析失败原因..."):
                analysis = analyze_failure(st.session_state["last_trace"], st.session_state["last_error"])
                st.subheader("分析结果")
                st.write(f"**失败类型**：{analysis.get('failure_type', '未知')}")
                st.write(f"**原因分析**：{analysis.get('reason', '')}")
                st.write(f"**修复建议**：{analysis.get('suggestion', '')}")
                
                with st.expander("查看完整分析"):
                    st.text(analysis["raw_analysis"])
    else:
        uploaded_file = st.file_uploader("上传trace.zip文件", type="zip")
        error_text = st.text_area("粘贴错误信息")
        if uploaded_file and error_text and st.button("分析"):
            # 保存上传的trace并分析
            trace_path = f"outputs/traces/{uploaded_file.name}"
            with open(trace_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            analysis = analyze_failure(trace_path, error_text)
            st.json(analysis)

# ------------------- 语义断言 -------------------
elif tab == "💬 语义断言":
    st.header("智能语义断言")
    
    test_url = st.text_input("测试页面URL", "https://example.com")
    assertion_desc = st.text_input("断言描述（自然语言）", "页面显示欢迎信息")
    
    if st.button("验证断言"):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(test_url)
            result = semantic_expect(page, assertion_desc)
            browser.close()
            
            if result["passed"]:
                st.success("✅ 断言通过")
            else:
                st.error("❌ 断言不通过")
            st.write(f"判断依据：{result['reason']}")

# ------------------- 低代码模式 -------------------
elif tab == "🧩 低代码模式":
    st.header("低代码自然语言操作")
    st.caption("无需写代码，用自然语言直接操作浏览器")
    
    target_url = st.text_input("打开页面", "https://example.com")
    steps = st.text_area("操作步骤（每行一步）", """
点击登录按钮
输入用户名admin
输入密码123456
点击提交
""")
    
    if st.button("▶️ 开始执行"):
        step_list = [s.strip() for s in steps.split("\n") if s.strip()]
        progress_bar = st.progress(0)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(target_url)
            
            for i, step in enumerate(step_list):
                st.write(f"执行步骤 {i+1}: {step}")
                try:
                    # 简单的自然语言动作解析
                    if "点击" in step:
                        element = step.replace("点击", "").strip()
                        smart_click(page, element)
                    elif "输入" in step:
                        parts = step.replace("输入", "").split()
                        if len(parts) >= 2:
                            field, value = parts[0], parts[1]
                            page.get_by_label(field).fill(value)
                    page.wait_for_timeout(500)
                except Exception as e:
                    st.error(f"步骤失败: {str(e)}")
                    break
                progress_bar.progress((i+1)/len(step_list))
            
            st.success("操作执行完成")
            st.button("关闭浏览器", on_click=browser.close)

