# 🚀 部署指南

## 📋 环境要求

- Python 3.8+
- pip (Python包管理器)

## 🔧 快速部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd flask_web
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 启动应用
```bash
python3 src/app.py
```

应用将在 http://localhost:5000 启动

## 📁 项目结构说明

```
flask_web/
├── src/                    # 源代码
│   ├── app.py             # Flask主应用
│   └── demo.py           # 演示脚本
├── tests/                 # 测试代码
├── test_data/            # 测试数据
├── docs/                 # 文档
├── examples/             # 示例
├── templates/            # HTML模板
├── uploads/              # 临时上传目录
├── requirements.txt      # Python依赖
└── .gitignore          # Git忽略文件
```

## 🧪 运行测试

```bash
# 激活虚拟环境后
python3 tests/test_mib_parser.py
python3 tests/test_multi_mib.py
python3 tests/test_zip_upload.py
```

## 🌐 生产环境部署

### 使用Gunicorn (推荐)

```bash
# 安装Gunicorn
pip install gunicorn

# 启动应用
gunicorn --bind 0.0.0.0:8000 src.app:app
```

### 使用Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]
```

## 🔒 安全注意事项

1. **不要提交venv目录** - 已在.gitignore中排除
2. **使用环境变量** - 敏感配置应通过环境变量设置
3. **限制上传文件大小** - 已在应用中配置为16MB
4. **验证上传文件类型** - 只允许.mib, .txt, .my, .zip文件

## 🐛 常见问题

### Q: 为什么venv目录不在Git中？
A: 虚拟环境包含系统特定的路径和配置，应该在每个部署环境中重新创建。

### Q: 如何更新依赖？
A: 修改requirements.txt后，在新环境中运行：
```bash
pip install -r requirements.txt --upgrade
```

### Q: 应用无法启动怎么办？
A: 检查以下几点：
1. Python版本是否为3.8+
2. 是否激活了虚拟环境
3. 依赖是否正确安装
4. 端口5000是否被占用

## 📞 支持

如有问题，请查看：
1. 应用日志输出
2. 测试用例运行结果
3. 项目文档：`docs/`目录
