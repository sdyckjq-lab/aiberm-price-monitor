# 安全指南

## API 密钥保护

### 重要提醒

1. **永远不要提交真实密钥到 Git**
   - `config.json` 已被 `.gitignore` 排除，不会进入版本控制
   - 创建 `config.json` 前，确保它不会被意外提交

2. **密钥泄露应急处理**
   如果不小心提交了包含真实密钥的 config.json：
   ```bash
   # 1. 立即撤销密钥（登录 Aiberm 网站重新生成）
   # 2. 从 Git 历史中彻底删除（困难，建议直接废弃仓库重建）
   # 3. 创建新的 config.json 并确保被 .gitignore 排除
   ```

3. **安全实践**
   - 仅复制 `config.example.json` 为 `config.json`
   - 在 `config.json` 中填入你的真实密钥
   - 定期检查 `git status` 确保 config.json 未被跟踪

## 配置文件说明

| 文件 | 用途 | 是否提交到 Git |
|------|------|----------------|
| `config.example.json` | 配置模板（占位符） | ✅ 是 |
| `config.json` | 真实配置（含密钥） | ❌ 否（已被 .gitignore 排除） |

## 验证安全设置

运行以下命令检查：

```bash
# 检查 config.json 是否被 Git 跟踪
git check-ignore -v config.json
# 应输出 .gitignore 的规则

# 检查 Git 状态
git status
# config.json 不应出现在未跟踪文件列表中
```

## 报告安全问题

如发现安全漏洞，请立即：
1. 撤销相关 API 密钥
2. 检查 Git 历史是否泄露
3. 重新生成所有受影响的密钥
