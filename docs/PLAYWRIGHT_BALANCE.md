# 一次登录后自动查询方案

本方案使用 Playwright 仅在首次登录时保存登录态，后续全部通过 API 自动获取余额与用量。

## 🎯 方案原理

通过浏览器登录一次，保存 Cookie 登录态。

**优点**：
- ✅ 不需要 system_token
- ✅ 登录一次即可长期自动查询
- ✅ 通过 API 获取准确数据

**缺点**：
- ❌ 首次运行需要安装浏览器

---

## 📦 安装依赖

```bash
cd "/Users/kangjiaqi/Documents/AiBerm Api/价格skill"

# 安装依赖
python3 -m pip install -r requirements.txt

# 安装浏览器（首次运行需要）
python3 -m playwright install chromium
```

---

## ⚙️ 配置

无需配置账号密码。首次运行会打开浏览器，请手动登录一次。

---

## 🚀 使用方法

```bash
# 方式 1：首次登录保存登录态
python3 scripts/fetch_balance_auto.py

# 方式 2：直接查询余额与用量（推荐）
./run.sh balance
```

---

## 📊 输出示例

```
============================================================
Aiberm 余额抓取工具 (Playwright)
============================================================

🔄 正在访问 Aiberm 网站...
✅ 登录态已保存
🔄 通过 API 查询余额与用量...
✅ 查询成功

✅ 抓取完成！

📁 登录态文件：
  - .auth_state.json
```

---

## 🔧 故障排查

### 问题 1：API 返回 401

**现象**：提示 "余额查询失败，可能登录态已过期"

**解决**：
1. 重新运行 `python3 scripts/fetch_balance_auto.py`
2. 完成登录后再次运行 `./run.sh balance`

### 问题 2：用量为空

**现象**：显示 "未获取到用量数据"

**解决**：
1. 确认账号近期有调用记录
2. 稍后重试（控制台统计可能有延迟）

---

## 📝 技术细节

### 使用技术
- **Playwright**：微软开源的浏览器自动化工具
- **Chromium**：无头浏览器（不显示窗口）
- **CSS 选择器**：定位页面元素

### 文件说明
- `fetch_balance_auto.py`：首次登录并保存登录态
- `.auth_state.json`：登录态文件
- `references/balance_scrape_debug.json`：页面抓取调试输出

### 安全性
- 登录态保存在本地 `.auth_state.json`
- `config.json` 已被 `.gitignore` 排除，不会提交到 Git

---

## 🆚 方案对比

| 方案 | 需要 system_token | 需要网站密码 | 稳定性 | 难度 |
|------|------------------|-------------|--------|------|
| 官方 API | ✅ 需要 | ❌ 不需要 | ⭐⭐⭐⭐⭐ | 简单 |
| 一次登录+API | ❌ 不需要 | ✅ 需要 | ⭐⭐⭐⭐ | 中等 |

**推荐**：
- 有 system_token → 用官方 API
- 没有 system_token → 用 Playwright 或本地估算

---

## 🎓 进阶：自定义选择器

如果网站改版，需要修改脚本中的 CSS 选择器：

```python
# 在脚本中找到这些选择器列表，根据实际情况修改
login_selectors = [
    "text=登录",           # 尝试文本匹配
    "[href*='login']",     # 尝试 href 属性
    "button:has-text('登录')",  # 尝试按钮文本
]
```

使用浏览器开发者工具（F12）查看元素的具体选择器。

---

## 📞 需要帮助？

1. 查看调试截图（`debug_*.png`）
2. 检查 `debug_page.html` 页面源码
3. 联系 Aiberm 支持：support@aiberm.com

---

**注意**：此方案为备选，官方推荐使用 system_token 调用 API 查询余额。
