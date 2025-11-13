# MIB 文件解析测试框架

本目录包含了用于测试 Flask 应用多 MIB 文件解析功能的统一测试框架。

## 📁 文件结构

```
tests/
├── README.md                           # 本文档
├── test_mib_unified.py                 # 统一测试框架 (主要使用)
├── run_tests.sh                        # 便捷运行脚本
├── mib_unified_test_report.json       # 最新测试报告
├── mib_comprehensive_test_report.json # 之前的测试报告
└── 多MIB文件解析测试报告.md              # 中文测试报告
```

## 🚀 快速开始

### 运行统一测试框架（推荐）

```bash
# 方法1: 使用便捷脚本
cd tests && ./run_tests.sh

# 方法2: 手动运行
# 确保 Flask 应用正在运行
cd src && python app.py

# 在新终端中运行统一测试
cd tests && python test_mib_unified.py
```

## 📋 测试覆盖范围

### 🔧 核心功能测试
- ✅ 单文件解析功能
- ✅ 多文件解析功能  
- ✅ MIB-II 标准文件支持
- ✅ OID 计算准确性
- ✅ 层次结构构建
- ✅ 跨文件依赖处理
- ✅ 树形结构验证

### 🌐 Web API 测试
- ✅ 单文件上传接口
- ✅ 多文件上传接口
- ✅ ZIP 文件上传接口
- ✅ 错误响应处理
- ✅ 文件格式验证

### ⚡ 性能测试
- ✅ 单文件解析速度
- ✅ 多文件解析速度
- ✅ 内存使用监控
- ✅ 大文件处理能力

### 🛡️ 错误处理测试
- ✅ 文件不存在处理
- ✅ 空文件处理
- ✅ 格式错误处理
- ✅ 网络错误处理

## 📊 测试报告

测试完成后，会生成详细的 JSON 报告：

```json
{
  "timestamp": "测试时间戳",
  "test_environment": {
    "python_version": "Python 版本",
    "framework": "测试框架名称",
    "test_date": "测试日期时间",
    "working_directory": "工作目录"
  },
  "summary": {
    "total_tests": "总测试数",
    "passed_tests": "通过测试数",
    "failed_tests": "失败测试数",
    "success_rate": "成功率百分比"
  },
  "detailed_results": {
    "测试名称": {
      "test": "测试名称",
      "success": true/false,
      "details": "详细信息",
      "data": "测试数据",
      "timestamp": "测试时间戳"
    }
  }
}
```

## 🧪 测试数据

测试框架使用以下测试数据：

- **示例 MIB 文件**: `../test_data/sample_mibs/`
  - SAMPLE-MIB.mib
  - RELATED-MIB.mib  
  - CHILD-MIB.mib

- **MIB-II 标准文件**: `../test_data/mib2_files/`
  - IF-MIB.txt
  - IP-MIB.txt
  - TCP-MIB.txt
  - UDP-MIB.txt

- **ZIP 压缩文件**: `../test_data/`
  - MIB.zip
  - test_mibs.zip
  - mib2_files.zip

## 🎯 测试场景

### 1. 基础解析测试
验证 MIB 解析器的基本功能：
- 正确识别 OBJECT-TYPE 定义
- 正确提取 SYNTAX、ACCESS、STATUS
- 正确解析 OID 路径
- 正确计算数字 OID

### 2. 多文件集成测试
验证多文件同时解析：
- 文件合并逻辑
- 跨文件依赖处理
- 模块信息提取
- 冲突解决机制

### 3. 标准兼容性测试
验证对标准 MIB-II 的支持：
- 正确识别 MIB-II 树结构
- 按标准组分类
- 标准 OID 计算
- 层次关系构建

### 4. 性能压力测试
验证解析性能：
- 大文件处理能力
- 内存使用效率
- 响应时间测量
- 并发处理能力

### 5. 错误恢复测试
验证错误处理：
- 异常情况处理
- 错误信息准确性
- 系统稳定性
- 资源清理

### 6. 树形结构验证
验证层次结构的正确性：
- 节点层次关系
- 重复节点检测
- 树深度计算
- 结构完整性

## 📈 使用建议

### 开发阶段
1. **运行统一测试**: 确保所有功能正常
2. **查看详细报告**: 分析性能和错误
3. **修复问题**: 根据报告修复发现的问题
4. **回归测试**: 确保修复不引入新问题

### 生产部署前
1. **完整测试套件**: 运行所有测试确保 100% 通过
2. **性能基准**: 确保性能满足要求
3. **压力测试**: 测试极限情况
4. **兼容性验证**: 确保与各种 MIB 文件兼容

## 🐛 故障排除

### 常见问题

1. **Flask 应用未启动**
   ```bash
   cd src && python app.py
   ```

2. **测试文件不存在**
   ```bash
   # 确保在项目根目录运行
   ls test_data/
   ```

3. **权限问题**
   ```bash
   # 确保有读写权限
   chmod +x tests/*.py
   ```

4. **依赖缺失**
   ```bash
   # 激活虚拟环境
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **网络连接问题**
   ```bash
   # 检查 Flask 应用是否在 5000 端口运行
   curl http://127.0.0.1:5000
   ```

## 📝 测试框架特性

### 统一测试框架优势
- **完整覆盖**: 整合了所有分散的测试功能
- **详细报告**: 提供完整的 JSON 格式测试报告
- **性能分析**: 包含详细的性能测试和分析
- **错误处理**: 全面的错误场景测试
- **易于维护**: 统一的代码结构和接口

### 与旧版本对比
- **功能整合**: 将 5 个分散的测试脚本合并为 1 个
- **报告改进**: 更详细和结构化的测试报告
- **错误处理**: 更完善的异常捕获和错误信息
- **性能测试**: 增强的性能分析功能
- **简化结构**: 移除了冗余的归档目录，保持简洁

## 📞 支持

如有问题或建议，请：
1. 查看最新测试报告: `tests/mib_unified_test_report.json`
2. 检查 Flask 应用日志
3. 运行单个测试进行调试: `cd tests && python test_mib_unified.py`
4. 提交 Issue 或 Pull Request

---

*最后更新: 2025年11月13日*
