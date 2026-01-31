# AGENTS.md
# 供自动化编码代理快速上手本仓库

## 项目概览
- 语言: Python 3.7+ 为主, Bash 为辅
- 入口脚本: `run.sh`
- 目标: 查询 Aiberm 模型价格/余额, 输出推荐
- 安全: `config.json` 含敏感信息, 必须保持不入库

## 目录结构速览
- `scripts/` 主要业务脚本
- `references/` 数据落盘 (价格历史、余额等)
- `config.example.json` 配置模板
- `config.json` 真实配置 (已在 `.gitignore` 中忽略)
- `run.sh` 统一入口

## 构建/运行命令
### 直接运行 (推荐)
- 价格查询: `./run.sh prices [关键词]`
- 余额查看: `./run.sh balance`
- 模型推荐: `./run.sh recommend`
- 帮助: `./run.sh help`

### Python 直跑 (无需 run.sh)
- 完整价格查询: `python3 scripts/fetch_prices.py [关键词]`
- 轻量价格查询: `curl -s https://aiberm.com/api/pricing | python3 scripts/quick_fetch.py [关键词]`
- 余额查询 (API): `python3 scripts/check_balance.py`
- 模型推荐: `python3 scripts/recommend_models.py`

## 环境依赖
- 安装依赖: `pip3 install -r requirements.txt`
- 依赖: `requests`, `playwright`
- 可选: 如果需要 Playwright 浏览器环境, 需额外安装浏览器驱动

## Build / Lint / Test
### Build
- 本仓库无编译构建步骤

### Lint / 格式化
- 未提供 lint/格式化脚本或配置
- README 提示代码风格为 Black, 但仓库未内置配置
- 若你本地安装了 Black, 可自行运行: `python3 -m black scripts`

### Test (含单测)
- 未发现测试框架或测试目录
- 当前没有单测命令或“单测”运行方式
- 若未来新增测试, 建议采用 `pytest` 并统一入口

## 配置与安全
- `config.json` 为真实配置, **禁止提交**
- 创建方式: `cp config.example.json config.json`
- 校验忽略: `git check-ignore -v config.json`
- 若泄露密钥, 参考 `SECURITY.md`

## 代码风格与约定
### 基本格式
- 缩进: 4 空格, 不使用 Tab
- 空行: 函数/模块之间通常 2 行
- 行宽: 未显式限制, 约 80-100 字符
- 字符串: 双引号优先
- 文档字符串: 三引号, 中文说明为主

### 导入规范
- 先标准库, 后第三方, 再本地模块
- 多行导入使用括号分行, 每项一行
- 不使用 `from x import *`

### 命名规范
- 常量: 全大写 + 下划线, 统一放 `scripts/constants.py`
- 函数: 小写 + 下划线 (snake_case)
- 变量: 小写 + 下划线
- 文件: 小写 + 下划线

### 路径与 IO
- 使用 `pathlib.Path` 处理路径
- 历史数据保存在 `references/`
- 读取/写入 JSON 使用 `utf-8` 编码

### 错误处理
- 网络请求: 设置超时, 捕获具体异常类型
- 错误输出: 统一打印人类可读信息 (常见前缀: ❌/⚠️/✅)
- 出错时多返回 `None` 或 `sys.exit(1)`

### 结构习惯
- 入口脚本常有 `main()` 函数
- 业务常量集中于 `scripts/constants.py`
- 历史记录只保留最近 30 条

## Playwright 相关脚本
- `scripts/fetch_balance_auto.py` 首次登录后保存登录态
- 会生成 `.auth_state.json` / `.login_confirm` / `debug_*.png`
- 这些文件默认已在 `.gitignore` 中

## Git 约定
- 避免提交: `config.json`, `venv/`, `__pycache__/`
- `references/` 数据是否提交按需决定 (当前未忽略)

## Cursor / Copilot 规则
- 未发现 `.cursor/rules/`, `.cursorrules`, 或 `.github/copilot-instructions.md`
- 如果后续添加, 请同步更新本文件

## 常见任务提示
- 修改价格计算: `scripts/constants.py`
- 调整历史记录数量: `MAX_HISTORY_RECORDS`
- 新增模型分类: `MODEL_CATEGORIES`
- 余额 API 查询: `scripts/check_balance.py`

## 贡献建议 (保持一致性)
- 仅做必要改动, 避免无关重构
- 新功能优先复用现有常量与工具函数
- 输出信息保持中文 + emoji 风格
- 任何新增配置文件, 先确认是否需要纳入 `.gitignore`
