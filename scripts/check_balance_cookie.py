#!/usr/bin/env python3
"""
通过浏览器登录态调用控制台 API 获取余额/用量
"""

import sys
import time
from pathlib import Path

from aiberm_console_api import (
    build_snapshot,
    fetch_usage_data,
    fetch_user_self,
    format_snapshot,
    load_auth_state,
    save_snapshot,
)
from constants import BALANCE_FILE


AUTH_FILE = Path(__file__).parent.parent / ".auth_state.json"


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
    start_ts = end_ts - 7 * 24 * 60 * 60
    usage_records = fetch_usage_data(
        auth_state=auth_state,
        start_timestamp=start_ts,
        end_timestamp=end_ts,
        default_time="day",
    )

    snapshot = build_snapshot(user_data, usage_records or [], start_ts, end_ts)
    save_snapshot(snapshot, BALANCE_FILE)

    for line in format_snapshot(snapshot):
        print(line)


if __name__ == "__main__":
    main()
