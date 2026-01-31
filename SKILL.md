---
name: aiberm-price-monitor
description: Aiberm API 价格监控与推荐工具。当用户询问模型价格、余额、用量或更便宜替代品时自动触发。支持价格查询、用量统计、余额汇总与模型推荐。
---

# Aiberm 价格监控技能

**Aiberm API 价格监控与推荐工具**

监控 Aiberm 模型价格变化、查询账户余额、推荐性价比最高的模型。

---

## 触发条件

当用户说以下关键词时，自动使用此技能：

- **价格查询**："查询 Aiberm 价格"、"查看模型价格"、"价格监控"、"claude 多少钱"
- **余额查询**："查询余额"、"我的余额"、"账户余额"、"还剩多少钱"
- **用量统计**："用量"、"消耗"、"使用情况"、"统计"、"最近用量"
- **模型推荐**："推荐便宜的模型"、"哪个模型性价比高"、"有没有更便宜的替代品"
- **价格对比**："为什么这个模型贵"、"anthropic 和 claude 有什么区别"

---

## 快速使用

### 1. 查询价格（最常用）

```bash
# 查询所有模型（按价格排序）
./run.sh prices

# 只查 Claude 系列
./run.sh prices claude

# 只查 GPT 系列  
./run.sh prices gpt

# 查特定模型
./run.sh prices opus
```

### 2. 查询余额

```bash
./run.sh balance
```

首次运行会自动打开浏览器登录一次，登录态保存在本地，后续无需再次登录。

输出内容包含：账户余额 + 用量最高模型 Top 3 + 对应价格 + 同类更便宜替代建议。

**输出字段说明**：
- 账户余额：当前可用余额、历史消耗
- 用量 Top 3：按消耗金额排序的前三模型
- 价格：输入/输出价格与平均成本
- 替代建议：同类模型中更便宜的备选项

**能力维度推荐（可选）**：
- 创建 `model_capabilities.json` 后，替代建议会优先选择“能力更接近且更便宜”的模型
- 模板文件：`model_capabilities.example.json`

### 3. 推荐性价比模型

```bash
./run.sh recommend
```

---

## 核心发现 - 模型命名规则

**Aiberm 有两套价格体系：**

| 模型名称格式 | 折扣 | 价格示例 |
|-------------|------|----------|
| `claude-opus-4-5-20251101` | 1.9折 (19%) | $0.071/token ✅ |
| `anthropic/claude-opus-4.5` | 原价 (100%) | $0.276/token ❌ |

**结论**：用不带 `anthropic/` 前缀的版本！便宜 4 倍！

**Claude 系列价格排序**（从便宜到贵）：
1. **claude-haiku-4-5-20251001**: $0.014/token
2. **claude-sonnet-4-5-20250929**: $0.043/token  
3. **claude-opus-4-5-20251101**: $0.071/token ✅ **推荐**
4. **anthropic/claude-opus-4.5**: $0.276/token ❌ 避免

---

## 配置文件

创建 `config.json`（可选，仅用于模型调用）:

```json
{
  "system_token": "你的系统访问令牌",
  "api_key": "你的API密钥（可选）"
}
```

⚠️ **重要**: `config.json` 已被 `.gitignore` 排除，不会提交到 Git，安全！

---

## 价格计算公式

```
实际价格 = 基准价格 × 模型倍率 × 分组折扣

基准价格（NewAPI 默认）：
- 输入：$0.15/百万token
- 输出：$0.6/百万token

示例（claude-opus-4-5-20251101-thinking）：
- 输入：$0.15 × 2.065 × 0.23 = $0.071/百万token
- 输出：$0.6 × 5 × 0.23 = $0.69/百万token
```

**分组折扣**：
- `default` 组：0.23（23% 的原价，即 7.7 折）

---

## 可用脚本

所有脚本位于 `scripts/` 目录：

| 脚本 | 功能 | 使用方式 |
|------|------|---------|
| `fetch_prices.py` | 完整版价格查询 | `python3 scripts/fetch_prices.py [关键词]` |
| `quick_fetch.py` | 轻量版（推荐） | `curl -s API | python3 scripts/quick_fetch.py [关键词]` |
| `skill_report.py` | 余额+用量+推荐汇总 | `python3 scripts/skill_report.py` |
| `recommend_models.py` | 模型推荐 | `python3 scripts/recommend_models.py` |
| `run.sh` | 统一启动脚本 | `./run.sh prices/balance/recommend` |

---

## 技术细节

### API 端点
- **价格查询**（公开）: `GET https://aiberm.com/api/pricing`
- **用户余额**（需认证）: `GET https://aiberm.com/api/user/self`
- **用量统计**（需认证）: `GET https://aiberm.com/api/data/self`

### 数据存储
- 价格历史自动保存在 `references/price_history.json`
- 保留最近 30 条记录

---

## 开源地址

https://github.com/sdyckjq-lab/aiberm-price-monitor

MIT License - 自由使用和修改

---

## 更新日志

- **2026-01-31**: 初始版本，支持价格查询、余额查询、模型推荐
