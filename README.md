# 🚀 Aiberm 价格监控技能 - 快速入门

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

创建 `config.json` 来配置你的系统令牌：

```json
{
  "system_token": "你的系统令牌",
  "api_key": "你的API密钥（可选）"
}
```

获取系统令牌：
- 登录 https://aiberm.com
- 个人设置 → 安全设置 → 系统访问令牌
- 复制填入 config.json

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
├── config.json            # 你的配置（已创建）
├── config.example.json    # 配置示例
├── SKILL.md               # 完整文档
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
**最后更新**: 2026-01-31
