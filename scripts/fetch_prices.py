#!/usr/bin/env python3
"""
Aiberm 价格查询脚本
获取所有模型的当前价格信息
"""

import requests
import json
import sys
from datetime import datetime
from pathlib import Path

# 导入常量配置
from constants import (
    PRICING_API,
    HISTORY_FILE,
    BASE_INPUT_PRICE,
    BASE_OUTPUT_PRICE,
    MAX_HISTORY_RECORDS,
)


def fetch_current_prices():
    """获取当前所有模型的价格"""
    try:
        response = requests.get(PRICING_API, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            print("❌ API 返回失败")
            return None

        return data
    except requests.Timeout:
        print("❌ 请求超时，请检查网络连接")
        return None
    except requests.ConnectionError:
        print("❌ 连接失败，请检查网络连接")
        return None
    except requests.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None
    except json.JSONDecodeError:
        print("❌ API 返回数据解析失败")
        return None


def calculate_real_price(model_data):
    """计算模型的实际价格（美元/百万token）"""
    quota_type = model_data.get("quota_type", 0)

    if quota_type == 1:  # 图片生成按次计费
        return {
            "type": "image",
            "price_per_image": model_data.get("model_price", 0),
            "input_price": None,
            "output_price": None,
        }

    # 文本模型按 token 计费
    model_ratio = model_data.get("model_ratio", 0)
    completion_ratio = model_data.get("completion_ratio", 1)

    input_price = BASE_INPUT_PRICE * model_ratio
    output_price = BASE_OUTPUT_PRICE * completion_ratio

    return {
        "type": "text",
        "input_price": round(input_price, 6),
        "output_price": round(output_price, 6),
        "price_per_image": None,
    }


def format_model_info(model_data, group_ratio):
    """格式化单个模型的信息"""
    model_name = model_data.get("model_name", "")
    original_name = model_data.get("original_model_name", model_name)
    prices = calculate_real_price(model_data)

    # 计算用户实际价格（乘以分组折扣）
    if prices["type"] == "text":
        user_input = prices["input_price"] * group_ratio
        user_output = prices["output_price"] * group_ratio

        return {
            "model_name": model_name,
            "original_name": original_name if original_name != model_name else None,
            "type": "text",
            "base_input_price": prices["input_price"],
            "base_output_price": prices["output_price"],
            "user_input_price": round(user_input, 6),
            "user_output_price": round(user_output, 6),
            "model_ratio": model_data.get("model_ratio"),
            "completion_ratio": model_data.get("completion_ratio"),
            "supported_types": model_data.get("supported_endpoint_types", []),
        }
    else:
        user_price = prices["price_per_image"] * group_ratio

        return {
            "model_name": model_name,
            "original_name": original_name if original_name != model_name else None,
            "type": "image",
            "base_price_per_image": prices["price_per_image"],
            "user_price_per_image": round(user_price, 6),
            "supported_types": model_data.get("supported_endpoint_types", []),
        }


def save_to_history(pricing_data):
    """保存价格数据到历史记录"""
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        # 读取现有历史
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  读取历史记录失败，将创建新记录: {e}")
                history = []

        # 添加新记录
        record = {"timestamp": datetime.now().isoformat(), "data": pricing_data}
        history.append(record)

        # 只保留最近 N 条记录
        history = history[-MAX_HISTORY_RECORDS:]

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        print(f"✅ 价格已保存到历史记录（共 {len(history)} 条）")
    except IOError as e:
        print(f"❌ 保存历史记录失败: {e}")


def display_prices(pricing_data, filter_model=None):
    """显示价格信息"""
    models = pricing_data.get("data", [])
    group_ratios = pricing_data.get("group_ratio", {})
    default_ratio = group_ratios.get("default", 0.23)

    print(f"\n📊 Aiberm 模型价格查询")
    print(f"⏰ 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"💰 用户分组折扣: {default_ratio} (default 组)")
    print(f"📦 模型总数: {len(models)}")
    print("=" * 80)

    # 筛选模型
    if filter_model:
        models = [
            m for m in models if filter_model.lower() in m.get("model_name", "").lower()
        ]
        if not models:
            print(f"\n❌ 未找到包含 '{filter_model}' 的模型")
            return

    # 分类显示
    text_models = []
    image_models = []

    for model_data in models:
        info = format_model_info(model_data, default_ratio)
        if info["type"] == "text":
            text_models.append(info)
        else:
            image_models.append(info)

    # 显示文本模型
    if text_models:
        print(f"\n📝 文本模型 ({len(text_models)} 个)")
        print("-" * 80)
        for info in text_models:
            print(f"\n🔹 {info['model_name']}")
            if info["original_name"]:
                print(f"   原始名称: {info['original_name']}")
            print(
                f"   输入价格: ${info['user_input_price']}/百万token (基准: ${info['base_input_price']})"
            )
            print(
                f"   输出价格: ${info['user_output_price']}/百万token (基准: ${info['base_output_price']})"
            )
            print(
                f"   倍率: 输入 {info['model_ratio']}x, 输出 {info['completion_ratio']}x"
            )
            print(f"   支持接口: {', '.join(info['supported_types'])}")

    # 显示图片模型
    if image_models:
        print(f"\n🖼️  图片生成模型 ({len(image_models)} 个)")
        print("-" * 80)
        for info in image_models:
            print(f"\n🔹 {info['model_name']}")
            if info["original_name"]:
                print(f"   原始名称: {info['original_name']}")
            print(
                f"   生成价格: ${info['user_price_per_image']}/张 (基准: ${info['base_price_per_image']})"
            )
            print(f"   支持接口: {', '.join(info['supported_types'])}")


def main():
    """主函数"""
    filter_model = sys.argv[1] if len(sys.argv) > 1 else None

    print("🔄 正在获取价格数据...")
    pricing_data = fetch_current_prices()

    if not pricing_data:
        sys.exit(1)

    # 显示价格
    display_prices(pricing_data, filter_model)

    # 保存历史
    save_to_history(pricing_data)


if __name__ == "__main__":
    main()
