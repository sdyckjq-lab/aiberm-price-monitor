#!/usr/bin/env python3
"""
Aiberm 模型推荐脚本
基于价格和性能推荐性价比模型
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 导入常量配置
from constants import (
    HISTORY_FILE,
    BASE_INPUT_PRICE,
    BASE_OUTPUT_PRICE,
    MODEL_CATEGORIES,
)


def load_latest_prices():
    """加载最新的价格数据"""
    if not HISTORY_FILE.exists():
        print("❌ 价格历史文件不存在，请先运行 fetch_prices.py")
        return None

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except json.JSONDecodeError:
        print("❌ 价格历史文件格式错误")
        return None
    except IOError as e:
        print(f"❌ 读取价格历史失败: {e}")
        return None

    if not history:
        print("❌ 价格历史为空")
        return None

    return history[-1]  # 返回最新记录


def categorize_models(models_data):
    """将模型按类别分组"""
    categorized = {cat: [] for cat in MODEL_CATEGORIES.keys()}
    categorized["other"] = []

    for model in models_data:
        model_name = model.get("model_name", "").lower()
        matched = False

        for category, info in MODEL_CATEGORIES.items():
            if any(keyword in model_name for keyword in info["models"]):
                categorized[category].append(model)
                matched = True
                break

        if not matched:
            categorized["other"].append(model)

    return categorized


def calculate_cost_per_million(model_data, group_ratio):
    """计算百万 token 的平均成本（输入输出各半）"""
    quota_type = model_data.get("quota_type", 0)

    if quota_type == 1:  # 图片生成不参与文本模型比较
        return None

    model_ratio = model_data.get("model_ratio", 0)
    completion_ratio = model_data.get("completion_ratio", 1)

    # 实际价格
    input_price = BASE_INPUT_PRICE * model_ratio * group_ratio
    output_price = BASE_OUTPUT_PRICE * completion_ratio * group_ratio

    # 假设输入输出各 50 万 token
    avg_cost = (input_price + output_price) / 2

    return round(avg_cost, 6)


def recommend_by_category(categorized, group_ratio):
    """按类别推荐性价比最高的模型"""
    print(f"\n🎯 按类别推荐性价比模型")
    print("=" * 80)

    for category, info in MODEL_CATEGORIES.items():
        models = categorized.get(category, [])
        if not models:
            continue

        # 计算每个模型的性价比
        model_costs = []
        for model in models:
            cost = calculate_cost_per_million(model, group_ratio)
            if cost is not None:
                model_costs.append(
                    {
                        "name": model.get("model_name"),
                        "cost": cost,
                        "model_ratio": model.get("model_ratio"),
                        "completion_ratio": model.get("completion_ratio"),
                    }
                )

        if not model_costs:
            continue

        # 按成本排序
        model_costs.sort(key=lambda x: x["cost"])

        print(f"\n📁 {info['name']} - {info['desc']}")
        print(f"   共 {len(model_costs)} 个模型")

        # 显示前 3 个最便宜的
        top_3 = model_costs[:3]
        for i, model in enumerate(top_3, 1):
            icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"\n   {icon} {model['name']}")
            print(f"      平均成本: ${model['cost']}/百万token")
            print(
                f"      倍率: 输入 {model['model_ratio']}x, 输出 {model['completion_ratio']}x"
            )


def recommend_overall(all_models, group_ratio):
    """推荐整体性价比最高的模型"""
    print(f"\n🏆 整体性价比 TOP 10")
    print("=" * 80)

    # 计算所有模型成本
    model_costs = []
    for model in all_models:
        cost = calculate_cost_per_million(model, group_ratio)
        if cost is not None:
            model_costs.append(
                {
                    "name": model.get("model_name"),
                    "cost": cost,
                    "model_ratio": model.get("model_ratio"),
                    "completion_ratio": model.get("completion_ratio"),
                    "supported_types": model.get("supported_endpoint_types", []),
                }
            )

    # 按成本排序
    model_costs.sort(key=lambda x: x["cost"])

    # 显示前 10
    for i, model in enumerate(model_costs[:10], 1):
        print(f"\n{i:2d}. {model['name']}")
        print(f"    平均成本: ${model['cost']}/百万token")
        print(
            f"    倍率: 输入 {model['model_ratio']}x, 输出 {model['completion_ratio']}x"
        )
        print(f"    接口: {', '.join(model['supported_types'])}")


def find_alternatives(model_name, all_models, group_ratio):
    """为指定模型寻找更便宜的替代品"""
    # 查找目标模型
    target = None
    for model in all_models:
        if model.get("model_name") == model_name:
            target = model
            break

    if not target:
        print(f"❌ 未找到模型: {model_name}")
        return

    target_cost = calculate_cost_per_million(target, group_ratio)
    if target_cost is None:
        print("❌ 该模型为图片生成模型，无法比较文本成本")
        return

    print(f"\n🔍 寻找 {model_name} 的替代品")
    print("=" * 80)
    print(f"📊 目标模型成本: ${target_cost}/百万token")

    # 查找更便宜的模型
    alternatives = []
    for model in all_models:
        if model.get("model_name") == model_name:
            continue

        cost = calculate_cost_per_million(model, group_ratio)
        if cost is not None and cost < target_cost:
            alternatives.append(
                {
                    "name": model.get("model_name"),
                    "cost": cost,
                    "savings": target_cost - cost,
                    "savings_percent": ((target_cost - cost) / target_cost) * 100,
                }
            )

    if not alternatives:
        print("\n✅ 该模型已经是最便宜的选择！")
        return

    # 按节省金额排序
    alternatives.sort(key=lambda x: x["savings"], reverse=True)

    print(f"\n💡 找到 {len(alternatives)} 个更便宜的替代品:")
    for i, alt in enumerate(alternatives[:10], 1):
        print(f"\n{i:2d}. {alt['name']}")
        print(f"    成本: ${alt['cost']}/百万token")
        print(f"    节省: ${alt['savings']}/百万token ({alt['savings_percent']:.1f}%)")


def main():
    """主函数"""
    # 加载最新价格
    latest = load_latest_prices()
    if not latest:
        return

    pricing_data = latest.get("data", {})
    models = pricing_data.get("data", [])
    group_ratio = pricing_data.get("group_ratio", {}).get("default", 0.23)

    timestamp = latest.get("timestamp", "")
    print(f"\n📊 基于 {timestamp[:19]} 的价格数据")
    print(f"💰 用户分组折扣: {group_ratio}")

    # 分类模型
    categorized = categorize_models(models)

    # 根据参数执行不同操作
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "--category":
            recommend_by_category(categorized, group_ratio)
        elif command == "--alternative" and len(sys.argv) > 2:
            model_name = sys.argv[2]
            find_alternatives(model_name, models, group_ratio)
        else:
            print("用法:")
            print("  python recommend_models.py              # 显示整体 TOP 10")
            print("  python recommend_models.py --category   # 按类别推荐")
            print("  python recommend_models.py --alternative <模型名>  # 寻找替代品")
    else:
        recommend_overall(models, group_ratio)


if __name__ == "__main__":
    main()
