#!/usr/bin/env python3
"""
Aiberm 余额查询脚本
查询账户余额和使用情况
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# API 配置
BASE_URL = "https://aiberm.com"
USER_API = f"{BASE_URL}/api/user/self"
CONFIG_FILE = Path(__file__).parent.parent / "config.json"


def load_config():
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        print("❌ 配置文件不存在，请先创建 config.json")
        print(f"   路径: {CONFIG_FILE}")
        print("\n配置示例:")
        print(
            json.dumps(
                {"system_token": "你的系统访问令牌", "api_key": "你的API密钥（可选）"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return None

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_user_balance(system_token):
    """查询用户余额"""
    headers = {
        "Authorization": f"Bearer {system_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(USER_API, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            print(f"❌ API 返回失败: {data.get('message', '未知错误')}")
            return None

        return data.get("data", {})
    except requests.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None


def format_quota(quota):
    """格式化配额显示（分转换为元）"""
    if quota is None:
        return "N/A"
    return f"¥{quota / 100:.2f}"


def display_balance(user_data):
    """显示余额信息"""
    print(f"\n💰 Aiberm 账户余额")
    print(f"⏰ 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 基本信息
    print(f"\n👤 用户信息")
    print(f"   用户名: {user_data.get('username', 'N/A')}")
    print(f"   邮箱: {user_data.get('email', 'N/A')}")
    print(f"   用户组: {user_data.get('group', 'default')}")

    # 余额信息
    quota = user_data.get("quota")
    used_quota = user_data.get("used_quota", 0)
    remaining = quota - used_quota if quota is not None else None

    print(f"\n💵 配额信息")
    print(f"   总配额: {format_quota(quota)}")
    print(f"   已使用: {format_quota(used_quota)}")
    print(f"   剩余: {format_quota(remaining)}")

    if quota is not None and quota > 0:
        usage_percent = (used_quota / quota) * 100
        print(f"   使用率: {usage_percent:.1f}%")

        # 余额预警
        if remaining is not None:
            if remaining < 100:  # 少于1元
                print("\n⚠️  余额不足 ¥1，请及时充值！")
            elif remaining < 500:  # 少于5元
                print("\n⚠️  余额较低，建议充值")

    # 请求统计
    request_count = user_data.get("request_count")
    if request_count is not None:
        print(f"\n📊 使用统计")
        print(f"   总请求次数: {request_count:,}")


def main():
    """主函数"""
    print("🔄 正在加载配置...")
    config = load_config()

    if not config:
        return

    system_token = config.get("system_token")
    if not system_token:
        print("❌ 配置文件中缺少 system_token")
        return

    print("🔄 正在查询余额...")
    user_data = get_user_balance(system_token)

    if not user_data:
        return

    display_balance(user_data)


if __name__ == "__main__":
    main()
