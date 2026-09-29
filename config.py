import json
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv is optional; env vars still work
    pass

BASE_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def load_config():
    """Load API config from environment variables, then config.json."""
    config = {
        "api_base": "",
        "api_key": "",
        "model_name": "",
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except Exception:
            pass

    # Environment variables take precedence over the local config file,
    # so a checked-out repo never needs a committed key.
    config["api_base"] = os.environ.get(
        "OPENAI_API_BASE", config["api_base"] or "https://api.deepseek.com/v1"
    )
    config["api_key"] = os.environ.get("OPENAI_API_KEY", config["api_key"])
    config["model_name"] = os.environ.get(
        "OPENAI_MODEL_NAME", config["model_name"] or "deepseek-chat"
    )
    return config

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
