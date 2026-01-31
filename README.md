# 🚀 Aiberm 价格监控技能 - 快速入门

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ⚠️ 安全警告（重要！）

**使用本工具前，请确保：**

1. **config.json 不会被提交到 Git**
   - `.gitignore` 已配置排除 `config.json`
   - 运行 `git status` 确认 config.json 不在跟踪列表中
   - 详见 [SECURITY.md](SECURITY.md)

2. **保护你的 API 密钥**
   - 系统令牌（system_token）是敏感信息
   - 不要截图或分享包含 config.json 的内容
   - 如意外泄露，立即到 Aiberm 网站撤销并重新生成

---

## 1. 这是做什么的？

监控 Aiberm API 的模型价格，帮你找到最便宜的模型，查看账户余额。

## 2. 快速使用

```bash
# 进入目录
cd "/Users/kangjiaqi/Documents/AiBerm Api/价格skill"

# 查询所有模型（按价格排序）
./run.sh prices

# 只查 Claude 系列
./run.sh prices claude

# 只查 GPT 系列  
./run.sh prices gpt

# 查询余额（需要配置系统令牌）
./run.sh balance

# 查看帮助
./run.sh help
```

## 3. 关键发现 - 模型命名规则

**Aiberm 有两套价格体系：**

| 模型名称格式 | 折扣 | 价格示例 |
|-------------|------|----------|
| `claude-opus-4-5-20251101` | 1.9折 (19%) | $0.071/token ✅ |
| `anthropic/claude-opus-4.5` | 原价 (100%) | $0.276/token ❌ |

**结论**：用不带 `anthropic/` 前缀的版本！便宜 4 倍！

**你当前使用的模型**：`claude-opus-4-5-20251101-thinking` - 正确的选择 ✅

## 4. Claude 系列价格排序（从便宜到贵）

1. **claude-haiku-4-5-20251001**: $0.014/token - 最便宜
2. **claude-sonnet-4-5-20250929**: $0.043/token
3. **claude-opus-4-5-20251101**: $0.071/token - 你用这个
4. **anthropic/claude-opus-4.5**: $0.276/token - 原价

## 5. 配置文件

### 5.1 创建配置文件

```bash
# 复制示例配置文件
cp config.example.json config.json

# 编辑 config.json 填入你的真实令牌
# 使用你喜欢的编辑器，如 nano、vim 或 VS Code
```

### 5.2 配置文件内容

```json
{
  "system_token": "你的系统访问令牌",
  "api_key": "你的API密钥（可选）"
}
```

### 5.3 获取系统令牌

1. 登录 https://aiberm.com
2. 进入：个人设置 → 安全设置 → 系统访问令牌
3. 复制令牌并填入 config.json

### 5.4 安全验证

创建 config.json 后，运行以下命令确保安全：

```bash
# 验证 config.json 是否被 Git 忽略
git check-ignore -v config.json
# 应显示: .gitignore:2:config.json

# 检查 Git 状态
git status
# config.json 不应出现在未跟踪文件列表中
```

## 6. 技术说明

- **价格数据来源**: `https://aiberm.com/api/pricing`（公开 API，无需认证）
- **价格计算**: `基准价 × 模型倍率 × 分组折扣`
  - 基准输入: $0.15/百万token
  - 基准输出: $0.6/百万token
  - 你的分组折扣: 0.23 (23%)
- **历史记录**: 自动保存在 `references/price_history.json`（最近30条）

## 7. 文件结构

```
价格skill/
├── run.sh                 # 启动脚本（用这个）
├── config.json            # ⚠️ 你的配置（本地创建，不提交）
├── config.example.json    # 配置示例（可提交）
├── .gitignore            # Git 忽略规则（保护 config.json）
├── SECURITY.md           # 安全指南
├── SKILL.md              # 完整文档
├── scripts/
│   ├── fetch_prices.py    # 完整版（需要 venv）
│   ├── quick_fetch.py     # 轻量版（直接用）
│   ├── check_balance.py   # 余额查询
│   └── recommend_models.py # 推荐算法
├── references/
│   └── price_history.json # 价格历史
└── venv/                  # Python 虚拟环境
```

## 8. 后续优化建议

1. **定时提醒**: 可以设置 cron job 每天自动检查价格
2. **价格变动检测**: 对比历史记录，发现价格变动时提醒
3. **用量统计**: 结合使用量计算每日花费
4. **余额预警**: 余额低于阈值时自动提醒

## 9. 分享给别人

可以把这个 skill 分享到 GitHub：
- `.gitignore` 已配置，不会泄露 `config.json`
- 别人需要自行创建配置文件
- 系统令牌是敏感信息，不要泄露

---

**当前状态**: ✅ 已完成基础功能  
**安全状态**: ✅ 已配置密钥保护  
**最后更新**: 2026-01-31
