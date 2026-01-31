#!/bin/bash
# Aiberm 价格监控工具启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv/bin/activate"

show_help() {
    echo "Aiberm 价格监控工具"
    echo ""
    echo "用法:"
    echo "  ./run.sh prices [关键词]     # 查询价格"
    echo "  ./run.sh balance             # 查询余额"
    echo "  ./run.sh recommend           # 推荐性价比模型"
    echo "  ./run.sh help                # 显示帮助"
    echo ""
    echo "示例:"
    echo "  ./run.sh prices              # 查询所有模型"
    echo "  ./run.sh prices claude       # 只查 Claude"
    echo "  ./run.sh prices gpt          # 只查 GPT"
    echo "  ./run.sh prices haiku        # 查 Haiku"
}

case "${1:-help}" in
    prices)
        FILTER="${2:-}"
        echo "🔄 正在查询价格${FILTER:+ (筛选: $FILTER)}..."
        if [ -f "$VENV_PATH" ]; then
            source "$VENV_PATH"
            python3 "$SCRIPT_DIR/scripts/fetch_prices.py" $FILTER
        else
            curl -s "https://aiberm.com/api/pricing" | python3 "$SCRIPT_DIR/scripts/quick_fetch.py" $FILTER
        fi
        ;;
    balance)
        echo "🔄 正在查询余额..."
        if [ -f "$VENV_PATH" ]; then
            source "$VENV_PATH"
            python3 "$SCRIPT_DIR/scripts/check_balance.py"
        else
            echo "❌ 虚拟环境不存在，请先创建 venv"
        fi
        ;;
    recommend)
        echo "🔄 正在生成推荐..."
        if [ -f "$VENV_PATH" ]; then
            source "$VENV_PATH"
            python3 "$SCRIPT_DIR/scripts/recommend_models.py"
        else
            echo "❌ 虚拟环境不存在，请先创建 venv"
        fi
        ;;
    help|--help|-h|*)
        show_help
        ;;
esac
