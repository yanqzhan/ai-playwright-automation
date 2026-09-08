import os
import zipfile
import base64
from io import BytesIO
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from PIL import Image
from openai import OpenAI

load_dotenv()

# ============== 模式自动切换：云端API / 本地Ollama ==============
USE_LOCAL_OLLAMA = os.getenv("USE_LOCAL_OLLAMA", "false").lower() == "true"

if USE_LOCAL_OLLAMA:
    # 本地 Ollama 模式配置
    LLM_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
    LLM_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "qwen2:7b")
    VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:7b")
else:
    # 云端大模型模式配置
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL")
    VISION_MODEL = os.getenv("VISION_MODEL")

# 全局统一初始化 LLM 客户端（OpenAI 兼容协议，Ollama 完美适配）
llm_client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

# 目录初始化
for dir_path in ["outputs/scripts", "outputs/traces", "outputs/reports"]:
    os.makedirs(dir_path, exist_ok=True)


def extract_dom_elements(page) -> str:
    """提取页面所有可交互元素的语义属性，优先返回稳定定位特征"""
    dom_content = page.content()
    soup = BeautifulSoup(dom_content, "lxml")
    
    elements_summary = []
    # 提取可交互元素：按钮、输入框、链接、下拉等
    for tag in ["button", "input", "a", "select", "textarea", "div[role]"]:
        for elem in soup.select(tag):
            role = elem.get("role", "")
            text = elem.get_text(strip=True)[:30]
            label = elem.get("aria-label", "")
            placeholder = elem.get("placeholder", "")
            name = elem.get("name", "")
            tag_name = elem.name
            
            # 只保留有语义信息的元素
            if any([text, label, placeholder, role]):
                elements_summary.append(
                    f"标签:{tag_name} | 文本:{text} | role:{role} | "
                    f"aria-label:{label} | placeholder:{placeholder} | name:{name}"
                )
    
    return "\n".join(elements_summary[:100])  # 限制数量避免token溢出


def screenshot_to_base64(page) -> str:
    """将页面截图转为base64，用于视觉模型识别"""
    screenshot_bytes = page.screenshot(full_page=True)
    return base64.b64encode(screenshot_bytes).decode("utf-8")


def parse_trace_file(trace_path: str) -> dict:
    """解析Playwright trace文件，提取错误信息、步骤、截图"""
    result = {"steps": [], "error": "", "screenshots": []}
    
    with zipfile.ZipFile(trace_path, "r") as zf:
        # 提取执行日志
        if "trace.trace" in zf.namelist():
            with zf.open("trace.trace") as f:
                trace_content = f.read().decode("utf-8", errors="ignore")
                result["raw_trace"] = trace_content[:5000]
        
        # 提取截图
        for file in zf.namelist():
            if file.endswith(".png") and "screenshot" in file:
                with zf.open(file) as f:
                    img = Image.open(BytesIO(f.read()))
                    result["screenshots"].append(img)
    
    return result


def save_script(script_code: str, script_name: str) -> str:
    """保存生成的脚本到本地"""
    file_path = f"outputs/scripts/{script_name}.py"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_code)
    return file_path
import os
import zipfile
import base64
from io import BytesIO
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from PIL import Image
from openai import OpenAI

load_dotenv()

# ============== 模式自动切换：云端API / 本地Ollama ==============
USE_LOCAL_OLLAMA = os.getenv("USE_LOCAL_OLLAMA", "false").lower() == "true"

if USE_LOCAL_OLLAMA:
    # 本地 Ollama 模式配置
    LLM_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
    LLM_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "qwen2:7b")
    VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:7b")
else:
    # 云端大模型模式配置
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL")
    VISION_MODEL = os.getenv("VISION_MODEL")

# 全局统一初始化 LLM 客户端（OpenAI 兼容协议，Ollama 完美适配）
llm_client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

# 目录初始化
for dir_path in ["outputs/scripts", "outputs/traces", "outputs/reports"]:
    os.makedirs(dir_path, exist_ok=True)


def extract_dom_elements(page) -> str:
    """提取页面所有可交互元素的语义属性，优先返回稳定定位特征"""
    dom_content = page.content()
    soup = BeautifulSoup(dom_content, "lxml")
    
    elements_summary = []
    # 提取可交互元素：按钮、输入框、链接、下拉等
    for tag in ["button", "input", "a", "select", "textarea", "div[role]"]:
        for elem in soup.select(tag):
            role = elem.get("role", "")
            text = elem.get_text(strip=True)[:30]
            label = elem.get("aria-label", "")
            placeholder = elem.get("placeholder", "")
            name = elem.get("name", "")
            tag_name = elem.name
            
            # 只保留有语义信息的元素
            if any([text, label, placeholder, role]):
                elements_summary.append(
                    f"标签:{tag_name} | 文本:{text} | role:{role} | "
                    f"aria-label:{label} | placeholder:{placeholder} | name:{name}"
                )
    
    return "\n".join(elements_summary[:100])  # 限制数量避免token溢出


def screenshot_to_base64(page) -> str:
    """将页面截图转为base64，用于视觉模型识别"""
    screenshot_bytes = page.screenshot(full_page=True)
    return base64.b64encode(screenshot_bytes).decode("utf-8")


def parse_trace_file(trace_path: str) -> dict:
    """解析Playwright trace文件，提取错误信息、步骤、截图"""
    result = {"steps": [], "error": "", "screenshots": []}
    
    with zipfile.ZipFile(trace_path, "r") as zf:
        # 提取执行日志
        if "trace.trace" in zf.namelist():
            with zf.open("trace.trace") as f:
                trace_content = f.read().decode("utf-8", errors="ignore")
                result["raw_trace"] = trace_content[:5000]
        
        # 提取截图
        for file in zf.namelist():
            if file.endswith(".png") and "screenshot" in file:
                with zf.open(file) as f:
                    img = Image.open(BytesIO(f.read()))
                    result["screenshots"].append(img)
    
    return result


def save_script(script_code: str, script_name: str) -> str:
    """保存生成的脚本到本地"""
    file_path = f"outputs/scripts/{script_name}.py"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(script_code)
    return file_path

