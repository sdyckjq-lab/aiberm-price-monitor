# 分享到 GitHub 指南

## 1. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名：`aiberm-price-monitor`
3. 描述：`Aiberm API 价格监控工具 - 查询模型价格、监控变动、推荐性价比模型`
4. 选择 Public
5. 不要勾选 "Add a README"
6. 点击 Create repository

## 2. 上传代码

```bash
# 进入目录
cd "/Users/kangjiaqi/Documents/AiBerm Api/价格skill"

# 初始化 Git
git init

# 添加所有文件（除了 config.json 会被 .gitignore 忽略）
git add .

# 提交
git commit -m "Initial commit: Aiberm price monitor skill"

# 连接远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/aiberm-price-monitor.git

# 推送
git push -u origin main
```

## 3. 验证配置

确保 `.gitignore` 包含：
```
config.json
venv/
__pycache__/
```

## 4. 完善仓库

在 GitHub 上：
1. 编辑 README.md 添加使用说明
2. 添加 Topics: `aiberm`, `price-monitor`, `ai-models`, `claude`
3. 设置仓库描述

## 5. 分享给他人

别人使用时只需：
```bash
git clone https://github.com/YOUR_USERNAME/aiberm-price-monitor.git
cd aiberm-price-monitor
echo '{"system_token": "xxx"}' > config.json
./run.sh prices claude
```

---

**注意**: 不要上传包含真实令牌的 config.json！
