#!/bin/bash

# MIB 统一测试框架运行脚本

echo "🚀 MIB 统一测试框架"
echo "===================="

# 检查虚拟环境
if [ ! -d "../venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source ../venv/bin/activate

# 检查 Flask 应用是否运行
echo "🔍 检查 Flask 应用状态..."
if curl -s http://127.0.0.1:5000 > /dev/null 2>&1; then
    echo "✅ Flask 应用正在运行"
    FLASK_RUNNING=true
else
    echo "⚠️  Flask 应用未运行，Web API 测试将跳过"
    echo "💡 提示: 在另一个终端运行 'cd src && python app.py' 来启动 Flask 应用"
    FLASK_RUNNING=false
fi

# 运行测试
echo ""
echo "🧪 运行统一测试..."
echo "===================="
python test_mib_unified.py

# 显示结果
echo ""
echo "📊 测试完成！"
echo "===================="
echo "📄 详细报告: tests/mib_unified_test_report.json"

if [ "$FLASK_RUNNING" = false ]; then
    echo ""
    echo "💡 要运行完整的测试套件（包括 Web API），请："
    echo "   1. 在终端1运行: cd src && python app.py"
    echo "   2. 在终端2运行: cd tests && ./run_tests.sh"
fi
