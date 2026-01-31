#!/usr/bin/env python3
"""
Aiberm 价格监控工具 - 常量配置模块
集中管理所有常量，避免重复定义
"""

from pathlib import Path

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent
REFERENCES_DIR = PROJECT_ROOT / "references"
CONFIG_FILE = PROJECT_ROOT / "config.json"
HISTORY_FILE = REFERENCES_DIR / "price_history.json"

# API 配置
BASE_URL = "https://aiberm.com"
PRICING_API = f"{BASE_URL}/api/pricing"
USER_API = f"{BASE_URL}/api/user/self"

# 基准价格配置（NewAPI 默认）
# 输入 $0.15/百万token，输出 $0.6/百万token
BASE_INPUT_PRICE = 0.15  # 美元/百万token
BASE_OUTPUT_PRICE = 0.6  # 美元/百万token

# 默认分组折扣
DEFAULT_GROUP_RATIO = 0.23

# 历史记录保留数量
MAX_HISTORY_RECORDS = 30

# 余额预警阈值（单位：分）
BALANCE_WARNING_LOW = 500  # 少于5元警告
BALANCE_WARNING_CRITICAL = 100  # 少于1元严重警告

# 模型分类配置
MODEL_CATEGORIES = {
    "claude": {
        "name": "Claude 系列",
        "models": ["claude-opus", "claude-sonnet", "claude-haiku"],
        "desc": "Anthropic 的高质量推理模型",
    },
    "gpt": {
        "name": "GPT 系列",
        "models": ["gpt-5", "gpt-4"],
        "desc": "OpenAI 的通用对话模型",
    },
    "gemini": {
        "name": "Gemini 系列",
        "models": ["gemini-3", "gemini-2.5"],
        "desc": "Google 的多模态模型",
    },
    "deepseek": {
        "name": "DeepSeek 系列",
        "models": ["deepseek-r1", "deepseek-v3"],
        "desc": "中文优化的开源模型",
    },
    "kimi": {
        "name": "Kimi 系列",
        "models": ["kimi-k2.5"],
        "desc": "月之暗面的长文本模型",
    },
    "grok": {
        "name": "Grok 系列",
        "models": ["grok-4", "grok-code"],
        "desc": "xAI 的快速推理模型",
    },
}
