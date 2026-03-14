# FocusFlow - 专业工时追踪与项目管理工具

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com)

**FocusFlow** 是一款面向专业动画师/剪辑师的跨平台生产力工时统计工具。它能够在后台静默记录用户在 After Effects、Premiere Pro 等软件上的实际工作时长，并根据文件路径自动归档至用户自定义的项目中，最终生成可视化报表。

## ✨ 核心特性

- ⏱️ **自动追踪** - 后台静默记录，无需手动操作
- 🎯 **智能分配** - 基于路径关键词自动归类到项目
- 🌳 **多级项目** - 支持无限层级的项目树结构
- 📊 **实时统计** - 可视化展示工时投入
- 💻 **跨平台** - 支持 macOS、Linux、Windows
- 🗄️ **数据归档** - 自动归档历史数据，保持高性能
- 🔔 **系统托盘** - 便捷的系统托盘菜单控制

## 🚀 快速开始

### 安装依赖

```bash
# 克隆项目
cd /path/to/FocusFlow

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 启动程序

```bash
# macOS/Linux
# 方法 1：直接执行脚本（推荐）
bash scripts/start.sh

# 方法 2：赋予执行权限后执行
chmod +x scripts/start.sh
./scripts/start.sh

# Windows
python scripts\start.bat
```

启动脚本会自动：
1. 检查并启动后台采集服务
2. 启动 GUI 界面
3. 自动处理多实例共享服务

### 停止程序

1. **关闭 GUI** - 通过系统托盘菜单选择"退出程序"
2. **停止后台服务**（可选）：
   ```bash
   # macOS/Linux
   pkill -f "service_daemon.py"
   
   # Windows
   taskkill /F /FI "WINDOWTITLE eq *service_daemon.py*"
   ```

## 📁 项目结构

```
FocusFlow/
├── core/                      # 核心模块
│   ├── database.py           # 数据库管理、配置管理
│   ├── project_tree.py       # 项目树形结构
│   └── export.py             # 数据导出功能
├── modules/                   # 功能模块
│   ├── app_detector.py       # 活动窗口检测
│   └── rule_engine.py        # 规则引擎
├── gui/                       # 图形界面
│   ├── dashboard_v2.py       # 主界面 (PySide6)
│   ├── data_management.py    # 数据管理对话框
│   └── time_axis.py          # 时间轴组件
├── service_daemon.py         # 后台采集服务
├── scripts/                   # 启动脚本
│   ├── start.sh              # macOS/Linux
│   └── start.bat             # Windows
├── tests/                     # 测试文件
│   ├── test_archive.py       # 归档功能测试
│   ├── test_performance.py   # 性能测试
│   └── test_archive_tool.py  # 归档工具测试
├── docs/                      # 文档目录
│   ├── 启动说明.md
│   ├── 功能说明/
│   │   ├── 多级子项目.md
│   │   └── 数据归档.md
│   └── 开发指南/
│       └── 项目交接说明.md
├── data/                      # 数据文件
│   └── tracker.db            # SQLite 数据库
├── requirements.txt           # 依赖列表
└── README.md                  # 项目说明
```

## 🛠️ 技术栈

- **语言**: Python 3.12+
- **GUI 框架**: PySide6 (Qt for Python)
- **数据库**: SQLite3
- **数据处理**: Pandas, Matplotlib
- **系统监控**: 
  - macOS: Quartz (Core Graphics)
  - Windows: psutil (计划)

## 📋 核心功能

### 1. 后台采集引擎

**位置**: `service_daemon.py`

- 每秒检测当前活跃窗口（应用名称、文件路径）
- 检测系统闲置状态（默认 30 秒无操作）
- 将活动记录写入数据库
- 独立运行，不受 GUI 影响

### 2. GUI 主界面

**位置**: `gui/dashboard_v2.py`

- 项目树形结构展示与管理
- 实时状态追踪（当前应用、文件、项目）
- 时间统计面板（累积、今日、本次连续）
- 数据可视化（柱状图、饼图）
- 系统托盘集成

### 3. 项目管理系统

- **多级子项目**: 支持无限层级父子关系
- **智能分配**: 路径关键词自动匹配
- **手动分配**: 精确绑定文件到项目
- **项目归档**: 叶子节点归档/恢复

### 4. 数据归档

- 自动归档上月数据（每月 1 号）
- 主表保留最近 30 天数据
- 智能查询（自动从主表和归档表获取）
- 保持数据库高性能

## 📖 详细文档

- **[启动说明](docs/启动说明.md)** - 详细的启动和故障排查指南
- **[多级子项目功能](docs/功能说明/多级子项目.md)** - 项目树使用指南
- **[数据归档使用指南](docs/功能说明/数据归档.md)** - 归档功能详解
- **[项目交接说明](docs/开发指南/项目交接说明.md)** - 完整的开发文档

## 🧪 测试

```bash
# 运行归档功能测试
python tests/test_archive.py

# 运行性能测试
python tests/test_performance.py

# 运行交互式测试工具
python tests/test_archive_tool.py
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FOCUSFLOW_INTERVAL_SECONDS` | 采集间隔（秒） | 1 |
| `FOCUSFLOW_DEBUG` | 调试模式 | 0 |
| `FOCUSFLOW_IDLE_SOURCE` | 闲置检测源 | combined |
| `FOCUSFLOW_IDLE_MODE` | 闲置检测模式 | strict |

### 系统配置（数据库）

配置存储在 `system_config` 表：

- `floating_position_x/y`: 悬浮窗位置
- `floating_visible`: 悬浮窗可见性
- `idle_threshold`: 闲置阈值（秒）

## 🔧 开发指南

### 代码风格

- 遵循 PEP 8 规范
- 使用类型注解
- 函数添加文档字符串
- 关键逻辑添加注释

### 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

## 📅 开发路线

### 已完成
- ✅ 静默采集与智能归档
- ✅ 多级子项目支持
- ✅ 实时追踪与悬浮窗
- ✅ 数据归档功能
- ✅ 系统托盘集成

### 计划中
- 🔄 Windows 兼容性支持
- 📦 PyInstaller 打包
- 📊 报表导出（CSV/Excel）
- 🎨 图表可视化增强
- ⚙️ 黑/白名单机制
- 🚀 开机自启（LaunchAgent/注册表）
- 🎬 渲染状态检测

## ❓ 常见问题

### Q: 后台服务无法启动
**A**: 检查虚拟环境是否激活，依赖是否安装，终端是否有权限。

### Q: GUI 界面卡顿
**A**: 数据量过大时建议运行数据归档，保持主表轻量。

### Q: 项目匹配不准确
**A**: 检查 `project_map` 规则设置，确保关键词唯一性。

### Q: 归档后数据会丢失吗？
**A**: 不会！数据只是从主表移动到归档表，查询完全透明。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**最后更新**: 2026-03-14  
**版本**: v2.0  
**维护者**: FocusFlow Team

**给开发者的说明**: 数据库位于 `data/tracker.db`，核心逻辑在 `core/` 和 `modules/` 目录下。请保持采集器 (`service_daemon.py`) 轻量级，避免阻塞主循环。
