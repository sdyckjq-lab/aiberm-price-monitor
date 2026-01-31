#!/usr/bin/env python3
"""
Aiberm 余额自动抓取脚本（手动确认模式）
- 跳出浏览器窗口，用户手动登录
- 用户确认登录完成后，脚本自动抓取
- 登录态自动保存，后续直接抓取
"""

import asyncio
import json
import sys
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

from aiberm_console_api import (
    build_snapshot,
    fetch_usage_data,
    fetch_user_self,
    format_snapshot,
    get_session_cookie,
    load_auth_state,
    save_snapshot,
)

# 路径配置
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
AUTH_FILE = PROJECT_DIR / ".auth_state.json"
BALANCE_FILE = PROJECT_DIR / "references" / "balance.json"
SCRAPE_FILE = PROJECT_DIR / "references" / "balance_scrape_debug.json"
CONFIRM_FILE = PROJECT_DIR / ".login_confirm"


def sanitize_balance_info(balance_data):
    """脱敏抓取调试信息"""
    if not balance_data:
        return {}

    def mask_email(text):
        import re

        return re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+", "***@***", text)

    texts = []
    for text in balance_data.get("balance_texts", [])[:5]:
        text = mask_email(str(text))
        texts.append(text[:200])

    return {
        "timestamp": balance_data.get("timestamp"),
        "balance": balance_data.get("balance"),
        "balance_texts": texts,
        "url": balance_data.get("url"),
    }


def save_balance(balance_data):
    """保存抓取调试信息"""
    safe_data = sanitize_balance_info(balance_data)
    SCRAPE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SCRAPE_FILE, "w", encoding="utf-8") as f:
        json.dump(safe_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 抓取调试已保存: {SCRAPE_FILE}")


def fetch_balance_via_api():
    """使用控制台 API 获取余额/用量"""
    auth_state = load_auth_state(AUTH_FILE)
    if not auth_state:
        print("❌ 未找到登录态，无法调用 API")
        return False

    user_data = fetch_user_self(auth_state=auth_state)
    if not user_data:
        print("❌ API 余额查询失败，可能登录态已过期")
        return False

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

    return True


def check_confirm():
    """检查是否有确认文件（用户标记登录完成）"""
    return CONFIRM_FILE.exists()


def create_confirm():
    """创建确认文件"""
    with open(CONFIRM_FILE, "w") as f:
        f.write("logged_in")


def remove_confirm():
    """删除确认文件"""
    if CONFIRM_FILE.exists():
        CONFIRM_FILE.unlink()


async def manual_login():
    """打开浏览器让用户手动登录"""
    print("=" * 60)
    print("🌐 正在打开浏览器")
    print("=" * 60)
    print()
    print("📱 请按以下步骤操作：")
    print()
    print("  1️⃣  在打开的浏览器中点击「登录」按钮")
    print("  2️⃣  输入你的 Aiberm 账号密码")
    print("  3️⃣  进入「控制台」或「个人中心」页面")
    print("  4️⃣  确认能看到余额信息")
    print()
    print("💡 完成后：")
    print(f"     在终端执行: touch {CONFIRM_FILE}")
    print("     或在另一个终端窗口运行: echo 'done' > .login_confirm")
    print()
    print("⏳ 脚本将等待 2 分钟...")
    print()

    # 删除旧的确认文件
    remove_confirm()

    async with async_playwright() as p:
        # 启动浏览器（有头模式，显示窗口）
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 打开 Aiberm 网站
        await page.goto("https://aiberm.com")

        print("✅ 浏览器已打开！")
        print()
        print("📝 现在请在浏览器中完成登录...")
        print()

        # 等待用户确认（通过创建确认文件）
        waited = 0
        max_wait = 120  # 最多等待 2 分钟

        while waited < max_wait:
            if check_confirm():
                print("✅ 检测到登录完成确认")
                break

            await asyncio.sleep(1)
            waited += 1

            if waited % 10 == 0:
                remaining = max_wait - waited
                print(f"  ...已等待 {waited} 秒，还剩 {remaining} 秒")
                print(f"     请执行: touch {CONFIRM_FILE}")

        if not check_confirm():
            print("\n⚠️  等待超时，假设已登录...")

        # 删除确认文件
        remove_confirm()

        # 保存登录态
        await context.storage_state(path=str(AUTH_FILE))
        print(f"\n✅ 登录态已保存: {AUTH_FILE}")

        # 验证登录态有效
        auth_state = load_auth_state(AUTH_FILE)
        if not auth_state or not fetch_user_self(auth_state=auth_state):
            print("⚠️  登录态验证失败，请确认已登录控制台")
            if AUTH_FILE.exists():
                AUTH_FILE.unlink()
                print("已删除无效登录态，请重试")
            await browser.close()
            return False

        await browser.close()
        return True


async def auto_fetch():
    """使用已保存的登录态自动抓取"""
    print("🔄 使用已保存的登录态抓取余额...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 加载登录态
        context = await browser.new_context(storage_state=str(AUTH_FILE))
        page = await context.new_page()

        try:
            # 直接访问余额页面
            print("🔄 访问余额页面...")
            await page.goto("https://aiberm.com/console/topup")
            await asyncio.sleep(3)

            # 刷新登录态（更新 session Cookie）
            await context.storage_state(path=str(AUTH_FILE))
            print(f"✅ 登录态已刷新: {AUTH_FILE}")

            print(f"✅ 当前页面: {page.url}")

            # 截图保存
            await page.screenshot(path=str(PROJECT_DIR / "debug_balance.png"))
            print("✅ 截图已保存: debug_balance.png")

            # 提取余额信息
            print("🔄 提取余额信息...")
            balance_info = {
                "timestamp": str(asyncio.get_event_loop().time()),
                "balance": None,
                "balance_texts": [],
                "url": page.url,
            }

            # 获取页面文本
            page_text = await page.evaluate("() => document.body.innerText")

            # 查找余额关键词
            import re

            # 方法1: 查找包含"余额"、"剩余"等的整行文本
            lines = page_text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 查找余额相关文本
                if any(
                    keyword in line
                    for keyword in ["余额", "剩余", "可用额度", "quota", "balance"]
                ):
                    if len(line) < 200:
                        balance_info["balance_texts"].append(line)
                        print(f"💰 {line}")

                        # 尝试提取金额
                        amounts = re.findall(r"[¥$]\s*[\d,]+(?:\.\d{2})?", line)
                        if amounts and not balance_info["balance"]:
                            balance_info["balance"] = amounts[0]

            # 方法2: 直接查找金额格式（¥ 或 $ 开头）
            if not balance_info["balance"]:
                amounts = re.findall(r"[¥$]\s*[\d,]+(?:\.\d{2})?", page_text)

                # 过滤出可能是余额的金额（通常在 0.01 - 1000 之间）
                for amount in amounts:
                    try:
                        num = float(
                            amount.replace("¥", "").replace("$", "").replace(",", "")
                        )
                        if 0.01 <= num <= 1000:
                            balance_info["balance"] = amount
                            print(f"💰 发现金额: {amount}")
                            break
                    except:
                        pass

            # 保存结果
            if balance_info["balance"] or balance_info["balance_texts"]:
                save_balance(balance_info)
                print(f"\n✅ 抓取成功！")
                if balance_info["balance"]:
                    print(f"📊 账户余额: {balance_info['balance']}")
            else:
                print("\n⚠️ 未找到明确的余额信息")
                print("💡 请查看 debug_balance.png 确认余额显示位置")
                print("💡 可能需要调整余额选择器")

            return balance_info

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            import traceback

            traceback.print_exc()

            # 登录态可能过期
            if AUTH_FILE.exists():
                print("\n🔄 可能是登录态过期，已删除")
                AUTH_FILE.unlink()
                print("   请重新运行脚本并登录")

        finally:
            await browser.close()


async def main():
    """主函数"""
    print()
    print("=" * 60)
    print("Aiberm 余额自动抓取工具")
    print("=" * 60)
    print()

    # 检查是否有登录态
    if not AUTH_FILE.exists():
        print("ℹ️  首次使用，需要手动登录\n")
        await manual_login()
        print()
    else:
        print("✅ 检测到已保存的登录态\n")

    # 抓取余额
    print("=" * 60)
    print("🔄 开始抓取余额...")
    print("=" * 60)
    print()

    api_ok = fetch_balance_via_api()
    result = None

    if not api_ok:
        result = await auto_fetch()

    print()
    print("=" * 60)

    if result:
        if result.get("balance"):
            print(f"💰 账户余额: {result['balance']}")

        if result.get("balance_texts"):
            print("📋 余额相关信息:")
            for text in result["balance_texts"][:3]:
                print(f"  • {text}")

    print()
    print("✅ 完成！")
    print("  • 登录态保存位置: .auth_state.json")
    print("  • API 快照位置: references/balance.json")
    print("  • 抓取调试位置: references/balance_scrape_debug.json")
    print("  • 截图保存位置: debug_balance.png")
    print("=" * 60)
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
