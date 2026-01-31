#!/bin/bash
# Aiberm 价格查询脚本（Shell 版本）

PRICING_API="https://aiberm.com/api/pricing"
BASE_INPUT=0.15
BASE_OUTPUT=0.6

FILTER="${1:-}"

echo "🔄 正在获取价格数据..."
DATA=$(curl -s "$PRICING_API")

if [ -z "$DATA" ]; then
    echo "❌ 请求失败"
    exit 1
fi

echo ""
echo "📊 Aiberm 模型价格查询"
echo "⏰ 查询时间: $(date '+%Y-%m-%d %H:%M:%S')"

GROUP_RATIO=$(echo "$DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['group_ratio']['default'])")
MODEL_COUNT=$(echo "$DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d['data']))")

echo "💰 用户分组折扣: $GROUP_RATIO (default 组)"
echo "📦 模型总数: $MODEL_COUNT"
echo "========================================================================"

if [ -n "$FILTER" ]; then
    echo ""
    echo "🔍 筛选关键词: $FILTER"
fi

echo "$DATA" | python3 << 'PYTHON_SCRIPT'
import sys
import json
import os

data = json.load(sys.stdin)
models = data['data']
group_ratio = data['group_ratio']['default']
filter_word = os.environ.get('FILTER', '').lower()

base_input = 0.15
base_output = 0.6

if filter_word:
    models = [m for m in models if filter_word in m.get('model_name', '').lower()]

print(f"\n📝 找到 {len(models)} 个模型")
print("-" * 72)

for model in models:
    name = model.get('model_name', '')
    quota_type = model.get('quota_type', 0)
    
    if quota_type == 1:
        price = model.get('model_price', 0) * group_ratio
        print(f"\n🖼️  {name}")
        print(f"   类型: 图片生成")
        print(f"   价格: ${price:.6f}/张")
    else:
        model_ratio = model.get('model_ratio', 0)
        completion_ratio = model.get('completion_ratio', 1)
        
        input_price = base_input * model_ratio * group_ratio
        output_price = base_output * completion_ratio * group_ratio
        
        print(f"\n🔹 {name}")
        print(f"   输入: ${input_price:.6f}/百万token")
        print(f"   输出: ${output_price:.6f}/百万token")
        print(f"   倍率: 输入 {model_ratio}x, 输出 {completion_ratio}x")
        
        types = ', '.join(model.get('supported_endpoint_types', []))
        if types:
            print(f"   接口: {types}")
PYTHON_SCRIPT

# 保存价格历史
HISTORY_DIR="$(dirname "$0")/../references"
HISTORY_FILE="$HISTORY_DIR/price_history.json"

mkdir -p "$HISTORY_DIR"

if [ -f "$HISTORY_FILE" ]; then
    HISTORY=$(cat "$HISTORY_FILE")
else
    HISTORY="[]"
fi

NEW_RECORD=$(cat << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S)Z",
  "data": $DATA
}
EOF
)

echo "$HISTORY" | python3 -c "
import sys, json
history = json.load(sys.stdin)
new_record = json.loads('''$NEW_RECORD''')
history.append(new_record)
history = history[-30:]
print(json.dumps(history, ensure_ascii=False, indent=2))
" > "$HISTORY_FILE"

echo ""
echo "✅ 价格已保存到历史记录"
