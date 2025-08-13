# Battle 630 投票统计系统

## 项目概述

这是一个用于爬取和分析 [Battle 630 - 循迹](https://www.battleverse.cn/battle/630) 创意对战平台数据的系统。系统能够自动获取投票数据，计算得分，并提供可视化的网页界面来展示结果。

## 功能特性

- 🕷️ **自动数据爬取**: 从Battle API获取实时投票数据
- 📊 **智能得分计算**: 根据投票规则自动计算每个作品的得分
- 🎨 **现代化界面**: 响应式设计的可视化仪表板
- 🔍 **搜索过滤**: 支持按用户名、作品ID或投票者搜索
- 📥 **数据导出**: 支持Excel和JSON格式下载
- 📱 **移动端适配**: 完全响应式设计，支持各种设备

## 文件结构

```
pb 积分/
├── scrape_battle_630.py          # Python爬虫脚本
├── battle_dashboard.html         # 可视化网页界面
├── requirements.txt              # Python依赖包列表
├── battle_630_analysis.md       # 技术分析文档
├── README.md                    # 项目说明文档
├── venv/                        # Python虚拟环境
└── 生成的数据文件/
    ├── battle_630_results_*.xlsx    # Excel结果文件
    └── battle_630_data_*.json       # JSON数据备份
```

## 快速开始

### 1. 环境准备

确保你的系统已安装Python 3.7+，然后：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖包
pip install -r requirements.txt
```

### 2. 运行爬虫脚本

```bash
python scrape_battle_630.py
```

脚本将自动：
- 从Battle API获取数据
- 计算每个作品的票数和得分
- 生成Excel文件和JSON备份
- 在控制台显示统计摘要

### 3. 查看可视化界面

```bash
# 在浏览器中打开
open battle_dashboard.html      # macOS
# 或
start battle_dashboard.html     # Windows
# 或直接双击HTML文件
```

## 数据说明

### 投票规则
- 每轮总分为100分
- 分数按票数比例分配：`得分 = 票数 × (100 ÷ 总票数)`

### 数据字段
- **作品ID**: 每个作品的唯一标识
- **用户名**: 作品创作者
- **票数**: 该作品获得的投票数量
- **得分**: 根据投票规则计算的得分
- **投票者**: 为作品投票的用户列表
- **创建时间**: 作品提交时间
- **作品链接**: 作品文件链接

## 技术架构

### 后端 (Python)
- **requests**: HTTP请求库，用于API调用
- **pandas**: 数据处理和分析
- **openpyxl**: Excel文件生成

### 前端 (HTML/CSS/JavaScript)
- **响应式设计**: 使用CSS Grid和Flexbox
- **现代化UI**: 渐变背景、阴影效果、动画过渡
- **交互功能**: 搜索过滤、分页、数据导出

### API接口
- **端点**: `https://server.battleverse.cn/index/fight/item.do`
- **方法**: POST
- **参数**: `{"fightId": 630}`

## 使用场景

1. **比赛结果统计**: 快速了解比赛结果和排名
2. **数据分析**: 分析投票模式和用户参与度
3. **报告生成**: 导出数据用于进一步分析或报告
4. **实时监控**: 定期运行脚本获取最新数据

## 注意事项

- 脚本需要网络连接来访问Battle API
- 生成的Excel文件包含两个工作表：投票统计和汇总信息
- 网页界面会自动加载本地JSON数据文件
- 建议定期运行脚本以获取最新数据

## 故障排除

### 常见问题

1. **ModuleNotFoundError**: 确保已安装所有依赖包
2. **网络连接失败**: 检查网络连接和API端点可访问性
3. **数据加载失败**: 确保JSON文件存在于HTML文件同目录下

### 获取帮助

如果遇到问题，请检查：
- Python版本兼容性
- 网络连接状态
- 依赖包是否正确安装
- 文件权限设置

## 更新日志

- **v1.0.0**: 初始版本，包含基本爬虫和可视化界面
- 支持数据爬取、得分计算、Excel导出
- 现代化响应式网页界面
- 搜索过滤和数据下载功能

## 许可证

本项目仅供学习和研究使用，请遵守相关网站的使用条款和API规范。 

## 部署（最简单路线）

推荐：GitHub Pages（前端）+ Render（后端）

1) 后端（Render）
- 登录 Render，New → Web Service，连接本仓库
- Root Directory: 仓库根目录
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn -w 2 -b 0.0.0.0:$PORT server:app`（Render 会注入 `$PORT`）
- 端口：5000（Render 自动映射），部署完成后获得后端 URL，如 `https://your-service.onrender.com`

2) 前端（GitHub Pages）
- 在仓库 Settings → Pages 启用 Pages，Source 选择 `main` 分支 `/` 根目录
- 配置 `battle_dashboard.html` 的 API 地址：
  - 临时：在浏览器控制台执行 `window.API_BASE = 'https://your-service.onrender.com'` 后刷新
  - 永久：在 HTML `<head>` 的脚本中把 `window.API_BASE` 赋值为你的后端地址

3) 使用
- 打开 GitHub Pages 地址，输入链接或 fightId，点击“抓取”

可选：本地开发
```
pip install -r requirements.txt
python server.py
```