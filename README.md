# MIB文件解析器

这是一个基于Flask的Web应用程序，用于解析SNMP MIB (Management Information Base) 文件并在前端以树形结构展示。

## 功能特点

- 📁 支持拖拽上传MIB文件
- 🌳 **可点击的**树形结构展示MIB对象
- 🏗️ **正确的父子关系**层次结构组织
- 📊 解析OBJECT-TYPE、OBJECT IDENTIFIER、MODULE-IDENTITY等
- 🔍 显示语法、访问权限、状态等详细信息
- 🔢 **数字OID显示**：自动计算并显示完整的数字OID（如 1.3.6.1.4.1.99999.1.1.1）
- ✨ 平滑的展开/折叠动画
- 🎨 现代化的Web界面
- 📱 响应式设计

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

### 1. 访问MIB解析器
- 打开浏览器访问 `http://localhost:5000`
- 点击导航栏中的 "🌳 MIB解析器" 链接

### 2. 上传MIB文件
- 点击上传区域选择文件，或直接拖拽文件到上传区域
- 支持的文件格式：`.mib`, `.txt`, `.my`
- 文件上传后将自动开始解析

### 3. 查看解析结果
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
│   └── mib_parser.py     # MIB解析模块
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
│   ├── index.html        # 首页
│   └── mib_parser.html   # MIB解析器页面
├── uploads/              # 上传文件目录
├── requirements.txt       # Python依赖包
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
- **MIB解析**: 自定义解析器（基于正则表达式）
- **UI框架**: 原生CSS + JavaScript

## 贡献

欢迎提交问题和拉取请求来改进这个项目。

## 许可证

MIT License
