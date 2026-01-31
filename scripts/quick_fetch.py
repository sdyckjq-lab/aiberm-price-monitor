#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_INPUT = 0.15
BASE_OUTPUT = 0.6
GROUP_RATIO = 0.23


def main():
    filter_keyword = sys.argv[1].lower() if len(sys.argv) > 1 else ""
    data = json.load(sys.stdin)

    if not data.get("success"):
        print("API 返回失败")
        return

    models = data.get("data", [])
    group_ratio = data.get("group_ratio", {}).get("default", 0.23)

    # 筛选模型
    if filter_keyword:
        models = [
            m for m in models if filter_keyword in m.get("model_name", "").lower()
        ]

    print(f"📊 Aiberm 价格查询 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"💰 分组折扣: {group_ratio}")
    print(f"📦 模型数: {len(models)}")
    if filter_keyword:
        print(f"🔍 筛选: {filter_keyword}")
    print()

    if not models:
        print("❌ 未找到匹配的模型")
        return

    # 按输入价格排序
    def get_cost(m):
        ratio = m.get("model_ratio", 0)
        return BASE_INPUT * ratio * group_ratio

    models.sort(key=get_cost)

    # 显示模型
    print("-" * 70)
    for m in models:
        name = m["model_name"]
        ratio = m.get("model_ratio", 0)
        comp = m.get("completion_ratio", 1)
        quota_type = m.get("quota_type", 0)

        print(f"\n🔹 {name}")

        if quota_type == 1:
            price = m.get("model_price", 0) * group_ratio
            print(f"   类型: 图片生成")
            print(f"   价格: ${price:.6f}/张")
        else:
            in_price = BASE_INPUT * ratio * group_ratio
            out_price = BASE_OUTPUT * comp * group_ratio
            print(f"   输入: ${in_price:.6f}/百万token (倍率 {ratio}x)")
            print(f"   输出: ${out_price:.6f}/百万token (倍率 {comp}x)")

            types = ", ".join(m.get("supported_endpoint_types", []))
            if types:
                print(f"   接口: {types}")

    # 保存历史
    history_file = Path(__file__).parent.parent / "references" / "price_history.json"
    history_file.parent.mkdir(parents=True, exist_ok=True)

    history = []
    if history_file.exists():
        with open(history_file, "r") as f:
            history = json.load(f)

    history.append({"timestamp": datetime.now().isoformat(), "data": data})
    history = history[-30:]

    with open(history_file, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"\n\n✅ 已保存到历史记录 (共 {len(history)} 条)")


if __name__ == "__main__":
    main()
