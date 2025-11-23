# MIB表OID生成器实现计划

## 1. 实现阶段划分

### 阶段1：核心功能实现
- 创建 `src/oid_generator.py` 模块
- 实现OIDGenerator类和核心算法
- 在 `src/routes.py` 中添加API端点
- 基础功能测试

### 阶段2：前端界面开发
- 完善 `templates/mib_oid_generator.html` 模板
- 实现JavaScript交互逻辑
- 添加表单验证和错误处理
- 前后端集成测试

### 阶段3：华为设备支持
- 实现华为特殊表处理逻辑
- 添加华为设备预设配置
- 测试华为设备MIB文件
- 优化华为表OID生成算法

### 阶段4：模板系统和高级功能
- 实现预定义模板系统
- 添加快速配置功能
- 支持批量OID生成
- 性能优化和缓存

### 阶段5：测试和部署
- 编写全面的测试用例
- 集成测试和用户验收测试
- 文档更新
- 部署准备

## 2. 详细实现步骤

### 2.1 核心模块实现 (src/oid_generator.py)

```python
# 主要类和方法设计：

class OIDGenerator:
    def __init__(self, mib_manager, mib_parser):
        self.mib_manager = mib_manager
        self.mib_parser = mib_parser
        self.huawei_tables = self._load_huawei_table_configs()
        self.templates = self._load_templates()
    
    def get_device_mib_tables(self, device_id):
        """获取设备类型的所有MIB表"""
        pass
    
    def generate_oid(self, device_id, table_name, index_values, selected_columns, **kwargs):
        """生成OID的核心方法"""
        pass
    
    def format_output(self, oids, output_format, **kwargs):
        """格式化输出结果"""
        pass
    
    def _load_huawei_table_configs(self):
        """加载华为设备特殊表配置"""
        pass
    
    def _load_templates(self):
        """加载预定义模板"""
        pass
```

### 2.2 API端点实现 (src/routes.py)

```python
# 需要添加的API端点：

@oid_generator_bp.route('/api/device-types/<device_id>/mib-tables', methods=['GET'])
def get_device_mib_tables(device_id):
    """获取设备类型的MIB表列表"""
    pass

@oid_generator_bp.route('/api/oid-generator/generate', methods=['POST'])
def generate_oids():
    """生成OID"""
    pass

@oid_generator_bp.route('/api/oid-generator/templates', methods=['GET'])
def get_templates():
    """获取预定义模板"""
    pass

@oid_generator_bp.route('/api/oid-generator/huawei-tables', methods=['GET'])
def get_huawei_tables():
    """获取华为设备特殊表配置"""
    pass
```

### 2.3 前端界面实现 (templates/mib_oid_generator.html)

主要功能模块：
1. 设备类型选择器
2. MIB表选择器
3. 索引值配置面板
4. 列选择器
5. 输出格式选择
6. 结果显示区域

JavaScript功能：
1. 动态加载MIB表
2. 表类型切换逻辑
3. 索引值验证
4. OID生成请求
5. 结果格式化显示

### 2.4 华为设备特殊支持

华为设备表类型：
1. OTS端口性能表
2. 单板性能表
3. 15分钟性能表
4. 24小时性能表

特殊处理逻辑：
1. 复杂索引结构处理
2. 性能表特殊OID格式
3. 设备类型特定配置

## 3. 数据结构设计

### 3.1 MIB表信息结构

```json
{
  "name": "tcpConnTable",
  "oid": "1.3.6.1.2.1.6.13",
  "description": "TCP连接表",
  "type": "standard",
  "columns": [
    {
      "name": "tcpConnState",
      "oid": "1",
      "description": "连接状态",
      "syntax": "INTEGER"
    }
  ],
  "index_columns": [
    {
      "name": "tcpConnLocalAddress",
      "oid": "2",
      "type": "IpAddress",
      "description": "本地地址"
    }
  ]
}
```

### 3.2 华为特殊表配置

```json
{
  "ots-port": {
    "base_oid": "1.3.6.1.4.1.2011.2.25.3.40.50.82",
    "description": "OTS端口性能表",
    "columns": [
      "ots-portPer15MCurMonValue",
      "ots-portPer15MCurVldty"
    ],
    "index_columns": ["ots-portPer15MCurEid"],
    "device_types": ["dc908", "osn1800", "osn9800"]
  }
}
```

## 4. 测试策略

### 4.1 单元测试
- OIDGenerator类方法测试
- MIB表解析测试
- OID生成算法测试
- 输出格式化测试

### 4.2 集成测试
- API端点测试
- 前后端交互测试
- 完整工作流测试

### 4.3 用户验收测试
- 标准MIB表OID生成
- 华为设备特殊表OID生成
- 模板系统功能
- 错误处理和边界情况

## 5. 性能优化

### 5.1 缓存策略
- MIB文件解析结果缓存
- 设备类型表信息缓存
- 模板配置缓存

### 5.2 批处理优化
- 大量OID生成的批处理
- 异步处理长时间操作
- 内存使用优化

## 6. 错误处理和验证

### 6.1 输入验证
- 设备类型存在性验证
- 表名存在性验证
- 索引值格式验证
- 列名存在性验证

### 6.2 错误响应
- 标准化错误响应格式
- 详细错误信息
- 用户友好的错误提示

## 7. 部署和配置

### 7.1 配置文件
- 华为设备表配置文件
- 模板配置文件
- 应用配置更新

### 7.2 数据库更新
- 如需要，更新数据库结构
- 迁移现有数据

## 8. 文档和培训

### 8.1 用户文档
- 功能使用说明
- 常见问题解答
- 最佳实践指南

### 8.2 开发文档
- API文档
- 代码注释
- 架构说明

## 9. 时间估算

- 阶段1：核心功能实现 - 3-4天
- 阶段2：前端界面开发 - 2-3天
- 阶段3：华为设备支持 - 2-3天
- 阶段4：模板系统和高级功能 - 2-3天
- 阶段5：测试和部署 - 2-3天

总计：11-16天

## 10. 风险评估

### 10.1 技术风险
- MIB文件解析复杂性
- 华为设备特殊表兼容性
- 性能瓶颈

### 10.2 缓解措施
- 充分的测试覆盖
- 渐进式实现
- 性能监控和优化