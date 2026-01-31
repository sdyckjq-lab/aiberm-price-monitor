#!/usr/bin/env python3
"""
Aiberm 控制台 API 工具
通过保存的浏览器登录态 (Playwright storage_state) 调用控制台接口
"""

import json
import time
from pathlib import Path

import requests

from constants import BALANCE_FILE, DATA_SELF_API, QUOTA_DIVISOR, USER_API


def load_auth_state(auth_file: Path):
    """读取 Playwright 登录态文件"""
    if not auth_file.exists():
        return None
    try:
        with open(auth_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None
    except IOError:
        return None


def get_session_cookie(auth_state, domain_keyword="aiberm.com"):
    """从 storage_state 中提取 session cookie"""
    if not auth_state:
        return None

    cookies = auth_state.get("cookies", [])
    for cookie in cookies:
        name = cookie.get("name")
        domain = cookie.get("domain", "")
        if name == "session" and domain_keyword in domain:
            return cookie.get("value")
    return None


def build_cookie_header(auth_state, domain_keyword="aiberm.com"):
    """构造完整 Cookie 头"""
    if not auth_state:
        return None

    cookies = auth_state.get("cookies", [])
    pairs = []
    for cookie in cookies:
        domain = cookie.get("domain", "")
        if domain_keyword in domain:
            name = cookie.get("name")
            value = cookie.get("value")
            if name and value is not None:
                pairs.append(f"{name}={value}")

    if not pairs:
        return None
    return "; ".join(pairs)


def build_headers(session_cookie=None, cookie_header=None):
    """构造请求头"""
    cookie_value = cookie_header or f"session={session_cookie}"
    return {
        "Cookie": cookie_value,
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }


def get_local_user_id(auth_state):
    """从 localStorage 获取用户 ID"""
    if not auth_state:
        return None

    origins = auth_state.get("origins", [])
    for origin in origins:
        if origin.get("origin") != "https://aiberm.com":
            continue
        for item in origin.get("localStorage", []):
            if item.get("name") == "user":
                try:
                    user = json.loads(item.get("value", "{}"))
                    return user.get("id")
                except json.JSONDecodeError:
                    return None
    return None


def build_base_headers(auth_state=None):
    """构造基础请求头"""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://aiberm.com/console",
        "Origin": "https://aiberm.com",
    }

    user_id = get_local_user_id(auth_state)
    if user_id is not None:
        headers["New-Api-User"] = str(user_id)

    return headers


def build_headers_from_auth_state(auth_state):
    """使用登录态构造请求头"""
    cookie_header = build_cookie_header(auth_state)
    if not cookie_header:
        return None
    return build_headers(cookie_header=cookie_header)


def build_session_from_auth_state(auth_state, domain_keyword="aiberm.com"):
    """使用登录态构造 requests 会话"""
    if not auth_state:
        return None

    session = requests.Session()
    cookies = auth_state.get("cookies", [])
    for cookie in cookies:
        domain = cookie.get("domain", "")
        if domain_keyword in domain:
            name = cookie.get("name")
            value = cookie.get("value")
            path = cookie.get("path", "/")
            if name and value is not None:
                session.cookies.set(name, value, domain=domain, path=path)

    return session


def fetch_user_self(session_cookie=None, auth_state=None, timeout=10):
    """获取用户信息与余额"""
    try:
        if auth_state is not None:
            session = build_session_from_auth_state(auth_state)
            if not session:
                return None
            response = session.get(
                USER_API,
                headers=build_base_headers(auth_state=auth_state),
                timeout=timeout,
            )
        else:
            headers = build_headers(session_cookie=session_cookie)
            response = requests.get(USER_API, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            return None
        return data.get("data", {})
    except requests.RequestException:
        return None
    except json.JSONDecodeError:
        return None


def fetch_usage_data(
    session_cookie=None,
    start_timestamp=None,
    end_timestamp=None,
    default_time="day",
    timeout=10,
    auth_state=None,
):
    """获取使用统计数据"""
    if start_timestamp is None or end_timestamp is None:
        return None
    params = {
        "start_timestamp": int(start_timestamp),
        "end_timestamp": int(end_timestamp),
        "default_time": default_time,
    }
    try:
        if auth_state is not None:
            session = build_session_from_auth_state(auth_state)
            if not session:
                return None
            response = session.get(
                DATA_SELF_API,
                headers=build_base_headers(auth_state=auth_state),
                params=params,
                timeout=timeout,
            )
        else:
            headers = build_headers(session_cookie=session_cookie)
            response = requests.get(
                DATA_SELF_API,
                headers=headers,
                params=params,
                timeout=timeout,
            )
        response.raise_for_status()
        data = response.json()
        if not data.get("success"):
            return None
        return data.get("data", [])
    except requests.RequestException:
        return None
    except json.JSONDecodeError:
        return None


def summarize_usage(records):
    """统计使用数据"""
    total_quota = 0
    total_tokens = 0
    total_count = 0
    by_model = {}

    for record in records or []:
        quota = record.get("quota", 0) or 0
        token_used = record.get("token_used", 0) or 0
        count = record.get("count", 0) or 0
        model_name = record.get("model_name", "unknown")

        total_quota += quota
        total_tokens += token_used
        total_count += count

        model_stats = by_model.setdefault(
            model_name, {"quota": 0, "token_used": 0, "count": 0}
        )
        model_stats["quota"] += quota
        model_stats["token_used"] += token_used
        model_stats["count"] += count

    top_models = sorted(
        by_model.items(), key=lambda item: item[1]["quota"], reverse=True
    )[:5]

    return {
        "total_quota": total_quota,
        "total_tokens": total_tokens,
        "total_count": total_count,
        "top_models": top_models,
    }


def build_snapshot(user_data, usage_records, start_timestamp, end_timestamp):
    """组装余额/用量快照"""
    quota = user_data.get("quota")
    used_quota = user_data.get("used_quota", 0)
    remaining_amount = quota / QUOTA_DIVISOR if quota is not None else None
    used_amount = used_quota / QUOTA_DIVISOR if used_quota is not None else None

    usage_summary = summarize_usage(usage_records)

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": {
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "group": user_data.get("group"),
            "request_count": user_data.get("request_count"),
        },
        "balance": {
            "quota": quota,
            "used_quota": used_quota,
            "remaining_amount": remaining_amount,
            "used_amount": used_amount,
        },
        "usage_window": {
            "start_timestamp": int(start_timestamp),
            "end_timestamp": int(end_timestamp),
        },
        "usage_summary": {
            "total_quota": usage_summary["total_quota"],
            "total_tokens": usage_summary["total_tokens"],
            "total_count": usage_summary["total_count"],
            "top_models": usage_summary["top_models"],
        },
    }


def save_snapshot(snapshot, output_file: Path = BALANCE_FILE):
    """保存快照到文件"""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
    except IOError:
        return False
    return True


def format_snapshot(snapshot):
    """格式化输出内容"""
    user = snapshot.get("user", {})
    balance = snapshot.get("balance", {})
    usage = snapshot.get("usage_summary", {})

    remaining_amount = balance.get("remaining_amount")
    used_amount = balance.get("used_amount")

    lines = []
    lines.append("\n💰 Aiberm 账户余额")
    lines.append(f"⏰ 查询时间: {snapshot.get('timestamp')}")
    lines.append("=" * 60)
    lines.append(f"\n👤 用户信息")
    lines.append(f"   用户名: {user.get('username', 'N/A')}")
    lines.append(f"   邮箱: {user.get('email', 'N/A')}")
    lines.append(f"   用户组: {user.get('group', 'default')}")
    lines.append(f"   请求次数: {user.get('request_count', 0)}")

    lines.append(f"\n💵 配额信息")
    if remaining_amount is not None:
        lines.append(f"   剩余余额: ${remaining_amount:.2f}")
    else:
        lines.append("   剩余余额: N/A")
    if used_amount is not None:
        lines.append(f"   历史消耗: ${used_amount:.2f}")
    else:
        lines.append("   历史消耗: N/A")

    lines.append("\n📊 使用统计 (时间段内)")
    lines.append(f"   统计请求数: {usage.get('total_count', 0)}")
    lines.append(f"   统计 Tokens: {usage.get('total_tokens', 0)}")
    if usage.get("total_quota") is not None:
        lines.append(f"   统计消耗: ${usage.get('total_quota', 0) / QUOTA_DIVISOR:.2f}")

    top_models = usage.get("top_models", [])
    if top_models:
        lines.append("\n🏆 消耗排行 (Top 5)")
        for name, stats in top_models:
            quota = stats.get("quota", 0)
            count = stats.get("count", 0)
            lines.append(f"   {name}: ${quota / QUOTA_DIVISOR:.2f} / {count} 次")

    return lines
