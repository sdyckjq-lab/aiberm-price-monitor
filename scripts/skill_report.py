#!/usr/bin/env python3
"""
Skill 汇总输出:
- 账户余额
- 使用量最高的模型 Top 3
- 价格信息
- 同类更便宜模型推荐
"""

from pathlib import Path
import json
import sys
import time

import requests

from aiberm_console_api import fetch_usage_data, fetch_user_self, load_auth_state
from constants import (
    BASE_INPUT_PRICE,
    BASE_OUTPUT_PRICE,
    MODEL_CATEGORIES,
    PRICING_API,
    QUOTA_DIVISOR,
)


AUTH_FILE = Path(__file__).parent.parent / ".auth_state.json"
CAPABILITY_FILE = Path(__file__).parent.parent / "model_capabilities.json"


def fetch_pricing_data(timeout=10):
    """获取价格数据"""
    try:
        response = requests.get(PRICING_API, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            return None
        return data
    except requests.RequestException:
        return None
    except ValueError:
        return None


def compute_text_price(model, group_ratio):
    """计算文本模型成本"""
    model_ratio = model.get("model_ratio", 0)
    completion_ratio = model.get("completion_ratio", 1)
    input_price = BASE_INPUT_PRICE * model_ratio * group_ratio
    output_price = BASE_OUTPUT_PRICE * completion_ratio * group_ratio
    avg_cost = (input_price + output_price) / 2
    return {
        "input_price": input_price,
        "output_price": output_price,
        "avg_cost": avg_cost,
    }


def build_price_map(pricing_data):
    """构建模型价格索引"""
    models = pricing_data.get("data", [])
    group_ratio = pricing_data.get("group_ratio", {}).get("default", 0.23)
    price_map = {}

    for model in models:
        if model.get("quota_type", 0) == 1:
            continue
        model_name = model.get("model_name")
        if not model_name:
            continue
        price_map[model_name] = compute_text_price(model, group_ratio)

    return price_map, group_ratio


def aggregate_usage(records):
    """聚合使用数据"""
    by_model = {}

    for record in records or []:
        model_name = record.get("model_name", "unknown")
        stats = by_model.setdefault(
            model_name, {"quota": 0, "token_used": 0, "count": 0}
        )
        stats["quota"] += record.get("quota", 0) or 0
        stats["token_used"] += record.get("token_used", 0) or 0
        stats["count"] += record.get("count", 0) or 0

    ranked = sorted(by_model.items(), key=lambda item: item[1]["quota"], reverse=True)
    return ranked


def detect_category(model_name):
    """按关键词匹配模型分类"""
    name = (model_name or "").lower()
    for category, info in MODEL_CATEGORIES.items():
        if any(keyword in name for keyword in info["models"]):
            return category
    return "other"


def load_capabilities():
    """加载模型能力配置"""
    if not CAPABILITY_FILE.exists():
        return {}
    try:
        with open(CAPABILITY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def normalize_score(value, min_value=0.0, max_value=10.0):
    """归一化评分"""
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    value = max(min_value, min(max_value, value))
    return (value - min_value) / (max_value - min_value)


def context_similarity(target_ctx, candidate_ctx):
    """上下文长度相似度"""
    if not target_ctx or not candidate_ctx:
        return None
    try:
        target_ctx = float(target_ctx)
        candidate_ctx = float(candidate_ctx)
    except (TypeError, ValueError):
        return None
    if target_ctx <= 0 or candidate_ctx <= 0:
        return None
    return min(target_ctx, candidate_ctx) / max(target_ctx, candidate_ctx)


def capability_similarity(target, candidate, weights=None):
    """能力相似度评分"""
    weights = weights or {"context": 0.5, "reasoning": 0.3, "speed": 0.2}

    ctx_score = context_similarity(
        target.get("context_length"), candidate.get("context_length")
    )
    reasoning_score = normalize_score(target.get("reasoning_score"))
    candidate_reasoning = normalize_score(candidate.get("reasoning_score"))
    speed_score = normalize_score(target.get("speed_score"))
    candidate_speed = normalize_score(candidate.get("speed_score"))

    if ctx_score is None or reasoning_score is None or candidate_reasoning is None:
        return None
    if speed_score is None or candidate_speed is None:
        return None

    reasoning_sim = 1 - abs(reasoning_score - candidate_reasoning)
    speed_sim = 1 - abs(speed_score - candidate_speed)

    return (
        ctx_score * weights["context"]
        + reasoning_sim * weights["reasoning"]
        + speed_sim * weights["speed"]
    )


def find_alternatives(target_name, price_map, capabilities):
    """找能力相近且更便宜的模型"""
    target_price = price_map.get(target_name)
    if not target_price:
        return [], "none"

    target_cap = capabilities.get(target_name)
    if target_cap:
        scored = []
        for model_name, price in price_map.items():
            if model_name == target_name:
                continue
            if price["avg_cost"] >= target_price["avg_cost"]:
                continue
            candidate_cap = capabilities.get(model_name)
            if not candidate_cap:
                continue
            similarity = capability_similarity(target_cap, candidate_cap)
            if similarity is None or similarity < 0.75:
                continue
            scored.append((model_name, price, similarity))

        scored.sort(key=lambda item: (-item[2], item[1]["avg_cost"]))
        if scored:
            return [(name, price) for name, price, _ in scored[:3]], "capability"

    target_category = detect_category(target_name)
    target_cost = target_price["avg_cost"]

    alternatives = []
    for model_name, price in price_map.items():
        if model_name == target_name:
            continue
        if detect_category(model_name) != target_category:
            continue
        if price["avg_cost"] < target_cost:
            alternatives.append((model_name, price))

    alternatives.sort(key=lambda item: item[1]["avg_cost"])
    return alternatives[:3], "category" if alternatives else "none"


def format_money(value):
    if value is None:
        return "N/A"
    return f"${value:.2f}"


def main():
    """主函数"""
    auth_state = load_auth_state(AUTH_FILE)
    if not auth_state:
        print("❌ 未找到登录态，请先运行: python3 scripts/fetch_balance_auto.py")
        sys.exit(1)

    user_data = fetch_user_self(auth_state=auth_state)
    if not user_data:
        print("❌ 余额查询失败，可能登录态已过期")
        sys.exit(1)

    end_ts = int(time.time())
    start_ts = end_ts - 30 * 24 * 60 * 60
    usage_records = fetch_usage_data(
        auth_state=auth_state,
        start_timestamp=start_ts,
        end_timestamp=end_ts,
        default_time="day",
    )

    pricing_data = fetch_pricing_data()
    price_map = {}
    group_ratio = 0.23
    if pricing_data:
        price_map, group_ratio = build_price_map(pricing_data)

    remaining_amount = user_data.get("quota")
    used_amount = user_data.get("used_quota", 0)
    remaining_amount = (
        remaining_amount / QUOTA_DIVISOR if remaining_amount is not None else None
    )
    used_amount = used_amount / QUOTA_DIVISOR if used_amount is not None else None

    print("\n💰 Aiberm 账户余额")
    print(f"⏰ 查询时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 用户名: {user_data.get('username', 'N/A')}")
    print(f"💵 剩余余额: {format_money(remaining_amount)}")
    print(f"📊 历史消耗: {format_money(used_amount)}")
    print(f"💰 分组折扣: {group_ratio}")

    if not usage_records:
        print("\n⚠️  未获取到用量数据")
        return

    capabilities = load_capabilities()

    ranked = aggregate_usage(usage_records)
    top_three = ranked[:3]

    print("\n🏆 使用量最高的模型 (Top 3)")
    print("=" * 60)

    for idx, (model_name, stats) in enumerate(top_three, 1):
        quota_amount = stats.get("quota", 0) / QUOTA_DIVISOR
        token_used = stats.get("token_used", 0)
        count = stats.get("count", 0)

        print(f"\n{idx}. {model_name}")
        print(f"   使用消耗: ${quota_amount:.2f} / {count} 次 / {token_used} tokens")

        price_info = price_map.get(model_name)
        if price_info:
            print(
                f"   价格: 输入 ${price_info['input_price']:.4f}/百万token, 输出 ${price_info['output_price']:.4f}/百万token"
            )
            print(f"   平均成本: ${price_info['avg_cost']:.4f}/百万token")
        elif not pricing_data:
            print("   价格: 暂不可用 (价格接口未返回)")
        else:
            print("   价格: 未找到该模型价格")

        alternatives, mode = find_alternatives(model_name, price_map, capabilities)
        if alternatives:
            if mode == "capability":
                label = "   更便宜替代(能力相近)"
            else:
                label = "   更便宜替代"
            print(f"{label}:")
            for alt_name, alt_price in alternatives:
                print(f"     - {alt_name}: ${alt_price['avg_cost']:.4f}/百万token")
        else:
            print("   更便宜替代: 暂无")


if __name__ == "__main__":
    main()
