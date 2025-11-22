# 网络工具集

这是一个基于Flask的Web应用程序，提供专业的网络管理和开发工具集合，包含MIB文件解析器和SNMP OID计算器等工具。

## 🛠️ 开发工具

本项目基于以下现代化开发工具链构建：

- **IDE**: Visual Studio Code
- **AI助手**: Cline (VSCode扩展)
- **AI模型**: GLM-4.6 (智谱AI)
- **开发方式**: AI辅助开发，结合人工优化

## 🌟 功能特点

### 🌐 国际化支持
- 🌍 **多语言支持**：中文和英文界面切换
- 🔄 **实时切换**：支持URL参数和链接切换
- 💾 **会话记忆**：语言偏好自动保存
- 🎯 **智能检测**：首次访问根据浏览器语言自动选择
- 📱 **全站支持**：所有页面和功能都支持多语言

### 🌳 MIB文件解析器
- 📁 支持拖拽上传MIB文件
- 🌳 **可点击的**树形结构展示MIB对象
- 🏗️ **正确的父子关系**层次结构组织
- 📊 解析OBJECT-TYPE、OBJECT IDENTIFIER、MODULE-IDENTITY等
- 🔍 显示语法、访问权限、状态等详细信息
- 🔢 **数字OID显示**：自动计算并显示完整的数字OID（如 1.3.6.1.4.1.99999.1.1.1）
- ✨ 平滑的展开/折叠动画
- 🎨 现代化的Web界面
- 📱 响应式设计

### 🧮 SNMP命令生成器
- 🎯 支持MIB Table (snmpwalk) 和叶子节点 (snmpget) 查询
- 🔐 完整的SNMPv1/v2c/v3支持
- 🏢 **华为传送设备支持**：SNMPv3模式下自动添加context参数(-n privacy)
- ⚙️ 智能参数配置和验证
- 📋 一键复制生成的命令
- 🎨 直观的用户界面
- 📝 详细的使用示例和帮助文本
- 🔗 **命令参数帮助链接**：快速访问Net-SNMP官方文档

### 🔢 MIB OID生成器
- 🎯 智能OID路径计算和生成
- 🌳 支持从MIB文件自动提取OID结构
- 📊 实时显示完整的数字OID路径
- 🔍 支持OID格式验证和纠错
- 📋 一键复制生成的OID
- 🎨 现代化的用户界面设计
- 📱 完全响应式布局
- ✨ 支持批量OID生成和导出

### 🏠 统一导航界面
- 🎨 现代化的工具集展示页面
- 🔄 流畅的页面导航体验
- 📱 完全响应式设计
- ✨ 优雅的动画效果

## 🆕 最新改进

### 1. 可点击的树形节点
- ✅ 修复了节点点击展开/折叠功能
- ✅ 整个节点项都可以点击
- ✅ 添加了平滑的展开/折叠动画
- ✅ 箭头图标显示当前状态（▶/▼）

### 2. 正确的父子关系层次结构
- ✅ 重新设计了MIB解析逻辑
- ✅ 根据OID路径自动构建父子关系
- ✅ 实现了真正的树形层次结构，而非平铺显示
- ✅ 智能的对象组织和分组

### 3. 数字OID计算和显示
- ✅ 自动计算完整的数字OID路径
- ✅ 支持标准SNMP OID根节点（如 enterprises = 1.3.6.1.4.1）
- ✅ 绿色高亮显示，便于识别和复制
- ✅ 与符号OID同时显示，便于对比

## 安装和运行

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd flask_web
```

### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或在Windows: venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行应用
```bash
cd src && python app.py
```

应用将在 http://localhost:5000 启动

## 使用方法

### 1. 访问应用
- 打开浏览器访问 `http://localhost:5000`
- 将显示网络工具集导航页面

### 2. 使用MIB文件解析器
- 在导航页面点击"MIB文件解析器"
- 点击上传区域选择文件，或直接拖拽文件到上传区域
- 支持的文件格式：`.mib`, `.txt`, `.my`
- 文件上传后将自动开始解析

### 3. 使用SNMP命令生成器
- 在导航页面点击"SNMP命令生成器"
- 选择查询类型（MIB Table或叶子节点）
- 输入OID或MIB名称
- 配置SNMP参数（版本、community等）
- **华为传送设备**：如果目标设备是华为传送设备且使用SNMPv3，勾选"华为传送设备"选项自动添加context参数
- 点击"生成命令"获取可执行的SNMP命令
- **命令参数帮助**：点击"命令参数帮助"链接查看详细的SNMP命令参数说明

### 4. 使用MIB OID生成器
- 在导航页面点击"MIB OID生成器"
- 上传MIB文件或输入OID路径
- 系统将自动解析并生成完整的数字OID
- 支持批量生成和格式验证
- 可一键复制生成的OID结果

### 5. 语言切换功能
- **URL参数切换**：直接访问 `http://localhost:5000/?lang=en`（英文）或 `http://localhost:5000/?lang=zh`（中文）
- **页面链接切换**：点击页面右上角的"中文"/"English"链接
- **自动语言检测**：首次访问时根据浏览器语言自动选择界面语言
- **会话记忆**：语言偏好会在整个会话期间保持，无需重复设置

### 6. 查看MIB解析结果
- 解析完成后将显示**层次化的**树形结构
- **点击任意节点**可展开/折叠子项（不仅仅是箭头）
- 每个节点显示名称、类型、OID和详细信息
- **自动组织**父子关系并显示数字OID，如：
  ```
  📦 Module: sampleMIB
  └── 🏷️ sampleObjects { sampleMIB 1 } [1.3.6.1.4.1.99999.1]
      ├── 🏷️ sampleSystemInfo { sampleObjects 1 } [1.3.6.1.4.1.99999.1.1]
      │   ├── 🔧 sampleSystemName { sampleSystemInfo 1 } [1.3.6.1.4.1.99999.1.1.1]
      │   └── 🔧 sampleSystemVersion { sampleSystemInfo 2 } [1.3.6.1.4.1.99999.1.1.2]
      └── 🔧 sampleConfigTable { sampleObjects 2 } [1.3.6.1.4.1.99999.1.2]
          └── 🔧 sampleConfigEntry { sampleConfigTable 1 } [1.3.6.1.4.1.99999.1.2.1]
  ```

### 7. 华为传送设备SNMP配置示例
- **SNMPv3 + 华为传送设备**：
  ```
  snmpget -v3 -u "admin" -a SHA -A "auth123" -x AES -X "priv123" -l authPriv -n privacy 192.168.1.1 sysDescr.0
  ```
- **普通SNMPv3**：
  ```
  snmpget -v3 -u "admin" -a SHA -A "auth123" -x AES -X "priv123" -l authPriv 192.168.1.1 sysDescr.0
  ```
- **SNMPv2c**：
  ```
  snmpget -v2c -c "public" 192.168.1.1 sysDescr.0
  ```

## 支持的MIB元素

- **MODULE-IDENTITY**: MIB模块定义
- **OBJECT-TYPE**: MIB对象定义
- **OBJECT IDENTIFIER**: 对象标识符
- **SYNTAX**: 对象语法类型
- **MAX-ACCESS**: 访问权限
- **STATUS**: 对象状态

## 示例文件

项目包含一个示例MIB文件 `sample_mibs/SAMPLE-MIB.mib`，您可以用它来测试解析功能。

## 测试

运行测试脚本：
```bash
python test_mib_parser.py
```

## 项目结构

```
flask_web/
├── src/                    # 源代码目录
│   ├── app.py             # 主应用文件
│   ├── config.py          # 配置文件
│   ├── routes.py          # 路由模块
│   ├── file_handler.py    # 文件处理模块
│   ├── mib_parser.py     # MIB解析模块
│   └── i18n/             # 国际化模块
│       └── __init__.py   # Babel国际化配置
├── locales/               # 翻译文件目录
│   ├── zh/               # 中文翻译
│   │   └── LC_MESSAGES/
│   │       ├── messages.po # 翻译源文件
│   │       └── messages.mo # 编译后的翻译文件
│   └── en/               # 英文翻译
│       └── LC_MESSAGES/
│           ├── messages.po # 翻译源文件
│           └── messages.mo # 编译后的翻译文件
├── tests/                 # 测试文件
│   ├── test_mib_parser.py # MIB解析器测试
│   ├── test_multi_mib.py  # 多文件上传测试
│   └── test_zip_upload.py # ZIP文件上传测试
├── test_data/            # 测试数据
│   ├── sample_mibs/      # 示例MIB文件
│   └── test_mibs.zip    # 测试ZIP包
├── examples/             # 示例
│   └── browser_test.html # 浏览器测试页面
├── templates/            # 模板文件
│   ├── index.html        # 网络工具集导航页面（主页）
│   ├── mib_parser.html   # MIB解析器页面
│   ├── oid_calculator.html # SNMP命令生成器页面
│   └── mib_oid_generator.html # MIB OID生成器页面
├── uploads/              # 上传文件目录
├── requirements.txt       # Python依赖包
├── babel.cfg            # Babel配置文件
├── README.md             # 项目说明文档
├── DEPLOYMENT.md         # 部署说明
└── venv/                 # Python虚拟环境
```

## API接口

### POST /upload-mib
上传并解析MIB文件

**请求参数:**
- `mib_file`: 上传的MIB文件

**响应格式:**
```json
{
  "success": true,
  "module": "模块名称",
  "tree": [
    {
      "text": "对象名称",
      "type": "object|identifier|module",
      "oid": "OID值",
      "syntax": "语法类型",
      "children": []
    }
  ]
}
```

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5, CSS3, JavaScript
- **国际化**: Flask-Babel (支持多语言切换)
- **MIB解析**: 自定义解析器（基于正则表达式）
- **UI框架**: 原生CSS + JavaScript

## 贡献

欢迎提交问题和拉取请求来改进这个项目。

## 🚀 部署指南

### 快速部署

本项目支持多种生产环境部署方式，详细配置请参考 [DEPLOYMENT.md](DEPLOYMENT.md) 和 [deployment/README.md](deployment/README.md)

#### 1. Docker部署（推荐）
```bash
# 克隆项目
git clone git@github.com:leezii/SimpleMIBTree.git
cd SimpleMIBTree

# Docker一键部署
cd deployment/docker
chmod +x deploy.sh
./deploy.sh
```

#### 2. Heroku云部署
```bash
# 安装Heroku CLI后
cd deployment/heroku
chmod +x deploy.sh
./deploy.sh
```

#### 3. Systemd服务部署
```bash
# 适用于Linux服务器
cd deployment/systemd
chmod +x deploy.sh
# 修改deploy.sh中的APP_PATH变量
./deploy.sh
```

#### 4. 传统Nginx + Gunicorn部署
```bash
# 手动配置
pip install gunicorn
# 复制配置文件并修改路径
sudo cp deployment/nginx/flask-web /etc/nginx/sites-available/
sudo cp deployment/systemd/flask-web.service /etc/systemd/system/
sudo cp deployment/systemd/gunicorn.conf.py /path/to/app/
# 启动服务
sudo systemctl start flask-web
sudo systemctl restart nginx
```

### 部署配置文件

所有部署配置文件已按类型归档到 `deployment/` 目录：

```
deployment/
├── docker/          # Docker容器化部署
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── deploy.sh
├── nginx/           # Nginx反向代理配置
│   └── flask-web
├── heroku/          # Heroku云平台部署
│   ├── Procfile
│   └── deploy.sh
├── systemd/         # Systemd服务部署
│   ├── flask-web.service
│   ├── gunicorn.conf.py
│   └── deploy.sh
└── README.md        # 部署详细说明
```

### 生产环境访问

部署完成后，应用将通过以下方式访问：
- **Docker**: http://localhost (端口80)
- **Heroku**: https://your-app-name.herokuapp.com
- **Systemd**: http://your-domain.com
- **Nginx**: http://your-domain.com

### 环境要求

- **Python**: 3.8+
- **内存**: 最低512MB
- **存储**: 最低1GB
- **系统**: Linux/Ubuntu/CentOS (推荐)

## 许可证

MIT License
