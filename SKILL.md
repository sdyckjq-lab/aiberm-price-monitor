# aiberm-price-monitor

**Aiberm API 价格监控与推荐工具**

监控 Aiberm 模型价格变化、查询账户余额、推荐性价比最高的模型。

---

## 功能特性

### 1. 价格查询 (`fetch_prices.py`)
- 实时获取所有模型的当前价格
- 自动保存价格历史（最近 30 条记录）
- 区分文本模型和图片生成模型
- 支持按模型名筛选

### 2. 余额查询 (`check_balance.py`)
- 查询账户余额和使用情况
- 余额预警（低于 ¥5 时提醒）
- 显示配额使用率和请求统计

### 3. 模型推荐 (`recommend_models.py`)
- 按类别推荐性价比模型（Claude、GPT、Gemini、DeepSeek 等）
- 显示整体性价比 TOP 10
- 为指定模型寻找更便宜的替代品

---

## 快速开始

### 配置系统令牌

1. 创建配置文件：
```bash
cd "/Users/kangjiaqi/Documents/AiBerm Api/价格skill"
nano config.json
```

2. 填入配置（从 Aiberm 网站获取）：
```json
{
  "system_token": "你的系统访问令牌",
  "api_key": "你的API密钥（可选）"
}
```

**获取系统令牌**：
- 登录 https://aiberm.com
- 进入「个人设置 → 安全设置 → 系统访问令牌」
- 复制令牌并填入 `config.json`

---

## 使用方法

### 价格查询

```bash
cd "/Users/kangjiaqi/Documents/AiBerm Api/价格skill"

# 查询所有模型（按价格排序）
curl -s "https://aiberm.com/api/pricing" | python3 scripts/quick_fetch.py

# 只查询包含 "claude" 的模型（按价格排序）
curl -s "https://aiberm.com/api/pricing" | python3 scripts/quick_fetch.py claude

# 只查询包含 "gpt" 的模型
curl -s "https://aiberm.com/api/pricing" | python3 scripts/quick_fetch.py gpt

# 查询特定模型
curl -s "https://aiberm.com/api/pricing" | python3 scripts/quick_fetch.py opus
```

**输出示例**：
```
📊 Aiberm 价格查询 - 2026-01-31 13:14
💰 分组折扣: 0.23
📦 模型数: 12
🔍 筛选: claude

----------------------------------------------------------------------

🔹 claude-haiku-4-5-20251001
   输入: $0.014248/百万token (倍率 0.413x)
   输出: $0.690000/百万token (倍率 5x)
   接口: anthropic, openai

🔹 claude-opus-4-5-20251101
   输入: $0.071243/百万token (倍率 2.065x)
   输出: $0.690000/百万token (倍率 5x)
   接口: anthropic, openai

🔹 anthropic/claude-opus-4.5
   输入: $0.276000/百万token (倍率 8x)
   输出: $0.690000/百万token (倍率 5x)
   接口: anthropic, openai

✅ 已保存到历史记录 (共 2 条)
```

### 余额查询

⚠️ **注意**：余额查询需要使用 **系统访问令牌**（与 API Key 不同）

```bash
cd "/Users/kangjiaqi/Documents/AiBerm Api/价格skill"

# 配置你的系统令牌
echo '{"system_token": "你的系统令牌"}' > config.json

# 查询余额
python3 scripts/check_balance.py
```

**输出示例**：
```
💰 Aiberm 账户余额
⏰ 查询时间: 2026-01-31 11:55:06

👤 用户信息
   用户名: user123
   邮箱: user@example.com
   用户组: default

💵 配额信息
   总配额: ¥100.00
   已使用: ¥23.50
   剩余: ¥76.50
   使用率: 23.5%
```

**常见问题**：
- 如果提示 "New-Api-User not provided"，说明令牌格式不对
- 系统令牌需要包含特定的 JWT 格式，不是简单的字符串

💵 配额信息
   总配额: ¥100.00
   已使用: ¥23.50
   剩余: ¥76.50
   使用率: 23.5%
```

### 模型推荐

```bash
# 显示整体性价比 TOP 10
python scripts/recommend_models.py

# 按类别推荐（Claude、GPT、Gemini 等）
python scripts/recommend_models.py --category

# 为指定模型寻找替代品
python scripts/recommend_models.py --alternative claude-opus-4-5-20251101
```

**输出示例**：
```
🏆 整体性价比 TOP 10
────────────────────────────────────────

 1. openai/gpt-5-nano
    平均成本: $0.028075/百万token
    倍率: 输入 0.031x, 输出 8x
    接口: openai

 2. openai/gpt-4o-mini
    平均成本: $0.03956/百万token
    倍率: 输入 0.075x, 输出 4x
    接口: openai
```

---

## 触发关键词（在 Claude 对话中使用）

当你对 Claude 说以下关键词时，我会自动调用此 skill：

- **价格查询**：
  - "查询 Aiberm 价格"
  - "查看模型价格"
  - "价格监控"
  - "claude 多少钱"

- **余额查询**：
  - "查询余额"
  - "我的余额"
  - "账户余额"
  - "还剩多少钱"

- **模型推荐**：
  - "推荐便宜的模型"
  - "哪个模型性价比高"
  - "有没有更便宜的替代品"
  - "帮我找个便宜的 claude"

---

## 价格计算公式

Aiberm 基于 NewAPI 项目，价格计算公式为：

```
实际价格 = 基准价格 × 模型倍率 × 分组折扣

基准价格（NewAPI 默认）：
- 输入：$0.15/百万token
- 输出：$0.6/百万token

示例（claude-opus-4-5-20251101-thinking）：
- 输入：$0.15 × 2.065 × 0.23 = $0.071095/百万token
- 输出：$0.6 × 5 × 0.23 = $0.69/百万token
```

**分组折扣**：
- `default` 组：0.23（23% 的原价，即 7.7 折）
- `vip` 组：1.0（原价）

---

## 数据存储

```
价格skill/
├── config.json                 # 用户配置（不提交到 Git）
└── references/
    └── price_history.json      # 价格历史（最近 30 条）
```

**price_history.json 结构**：
```json
[
  {
    "timestamp": "2026-01-31T11:55:06",
    "data": {
      "data": [...],
      "group_ratio": { "default": 0.23 }
    }
  }
]
```

---

## API 参考

### 公开 API（无需认证）
- **价格查询**：`GET https://aiberm.com/api/pricing`

### 需要系统令牌的 API
- **用户余额**：`GET https://aiberm.com/api/user/self`
  - Header: `Authorization: Bearer {system_token}`

### API Key vs 系统令牌

| 功能 | API Key | 系统令牌 |
|------|---------|---------|
| 调用 AI 模型 | ✅ | ❌ |
| 查询余额 | ❌ | ✅ |
| 查看使用记录 | ❌ | ✅ |
| 账户管理 | ❌ | ✅ |

---

## 注意事项

### 安全
- **不要将 `config.json` 提交到 Git**
- 系统令牌具有账户管理权限，妥善保管
- 建议定期更换系统令牌

### GitHub 分享
- 本 skill 已配置 `.gitignore`，排除敏感配置
- 可安全分享到 GitHub
- 其他用户需自行创建 `config.json`

### 价格变动
- Aiberm 价格可能随时调整
- 建议定期运行 `fetch_prices.py` 更新数据
- 历史记录仅保留最近 30 条

---

## 常见问题

**Q: 为什么余额查询失败？**  
A: 检查 `config.json` 中的 `system_token` 是否正确，API Key 无法用于查询余额。

**Q: 价格数据多久更新一次？**  
A: 每次运行 `fetch_prices.py` 时实时获取，不会自动定时更新。

**Q: 如何找到最便宜的 Claude 模型？**  
A: 运行 `python scripts/recommend_models.py --category`，查看 Claude 类别的推荐。

**Q: 可以添加价格预警吗？**  
A: 当前版本需手动运行脚本。可以结合 cron job 实现自动监控（未来版本功能）。

---

## 依赖

```bash
pip install requests
```

Python 3.7+ 即可运行。

---

## 许可

MIT License - 自由使用和修改

---

**作者**: Claude × 你的协作  
**最后更新**: 2026-01-31
