import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    """加载 API 配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # 默认返回空配置或从环境变量读取
    return {
        "api_base": os.environ.get("OPENAI_API_BASE", "https://api.deepseek.com/v1"),
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "model_name": os.environ.get("OPENAI_MODEL_NAME", "deepseek-chat")
    }

def save_config(api_base, api_key, model_name):
    """保存 API 配置"""
    config = {
        "api_base": api_base,
        "api_key": api_key,
        "model_name": model_name
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    return config
