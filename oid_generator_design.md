# MIB表OID生成器设计文档

## 1. 功能概述

MIB表OID生成器允许用户根据已上传的设备类型中的MIB表，智能生成对应的OID。该功能需要支持标准MIB表和华为光网络设备的特殊表。

## 2. 系统架构

### 2.1 核心组件

1. **OIDGenerator类** - 核心OID生成逻辑
2. **MIB表解析器** - 从MIB文件中提取表结构
3. **华为设备特殊表处理器** - 处理华为光网络设备的特殊表结构
4. **模板系统** - 提供预定义的OID生成模板

### 2.2 数据流程

```
用户选择设备类型 → 获取MIB文件列表 → 解析MIB文件提取表结构 → 
用户配置表类型和索引 → 生成OID → 格式化输出结果
```

## 3. API设计

### 3.1 获取设备类型的MIB表

```
GET /api/device-types/{device_id}/mib-tables
```

响应格式：
```json
{
  "success": true,
  "data": {
    "tables": [
      {
        "name": "tcpConnTable",
        "oid": "1.3.6.1.2.1.6.13",
        "description": "TCP连接表",
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
    ]
  }
}
```

### 3.2 生成OID

```
POST /api/oid-generator/generate
```

请求格式：
```json
{
  "device_id": "dc908",
  "table_name": "tcpConnTable",
  "index_values": ["192.168.1.1", "80"],
  "selected_columns": ["tcpConnState", "tcpConnLocalPort"],
  "output_format": "snmpget",
  "target_ip": "192.168.1.100",
  "community": "public",
  "snmp_version": "2c"
}
```

响应格式：
```json
{
  "success": true,
  "data": {
    "generated_oids": [
      {
        "column_name": "tcpConnState",
        "oid": "1.3.6.1.2.1.6.13.1.4.192.168.1.1.80",
        "command": "snmpget -v2c -c public 192.168.1.100 1.3.6.1.2.1.6.13.1.4.192.168.1.1.80"
      }
    ]
  }
}
```

### 3.3 获取预定义模板

```
GET /api/oid-generator/templates
```

### 3.4 获取华为设备特殊表配置

```
GET /api/oid-generator/huawei-tables
```

## 4. 核心算法

### 4.1 OID生成算法

```python
def generate_oid(base_oid, column_oid, index_values):
    """
    生成完整的OID
    
    参数:
        base_oid: 表的基础OID
        column_oid: 列的OID编号
        index_values: 索引值列表
    
    返回:
        完整的OID字符串
    """
    # 处理索引值
    processed_indices = []
    for index in index_values:
        if '.' in index:  # IP地址
            processed_indices.append(index.replace('.', '.'))
        else:  # 数字
            processed_indices.append(index)
    
    # 构建OID
    oid_parts = [base_oid, str(column_oid)] + processed_indices
    return '.'.join(oid_parts)
```

### 4.2 华为设备特殊表处理

华为光网络设备有特殊的表结构，如性能表：

```python
HUAWEI_SPECIAL_TABLES = {
    "performance": {
        "ots-port": {
            "base_oid": "1.3.6.1.4.1.2011.2.25.3.40.50.82",
            "description": "OTS端口性能表",
            "columns": [
                "ots-portPer15MCurMonValue",
                "ots-portPer15MCurVldty",
                "ots-portPer15MCurDateTime"
            ],
            "index_columns": ["ots-portPer15MCurEid"]
        }
    }
}
```

## 5. 模板系统

### 5.1 预定义模板

```python
OID_TEMPLATES = {
    "interface_basic": {
        "name": "基础接口信息",
        "table_type": "interface",
        "columns": ["ifDescr", "ifType", "ifAdminStatus", "ifOperStatus"],
        "output_format": "snmpget"
    },
    "huawei_performance": {
        "name": "华为设备性能监控",
        "table_type": "huawei_performance",
        "columns": ["ots-portPer15MCurMonValue", "ots-portPer15MCurVldty"],
        "output_format": "snmpget"
    }
}
```

## 6. 输出格式支持

### 6.1 纯OID
```
1.3.6.1.2.1.6.13.1.4.192.168.1.1.80
```

### 6.2 SNMP命令
```
snmpget -v2c -c public 192.168.1.100 1.3.6.1.2.1.6.13.1.4.192.168.1.1.80
```

### 6.3 表格格式
```
tcpConnState[192.168.1.1.80]    1.3.6.1.2.1.6.13.1.4.192.168.1.1.80
```

## 7. 实现细节

### 7.1 MIB表解析

从MIB文件中提取表结构需要：
1. 识别OBJECT-TYPE定义
2. 解析表和列的OID关系
3. 提取索引列信息
4. 识别表类型（标准表、华为特殊表等）

### 7.2 索引值处理

不同类型的索引值需要特殊处理：
1. IP地址：保持点分十进制格式
2. 数字：直接使用
3. 字符串：转换为适当的OID格式

### 7.3 错误处理

1. 无效的设备类型或表名
2. 错误的索引值格式
3. 不存在的列名
4. MIB文件解析失败

## 8. 测试用例

### 8.1 标准MIB表测试

- 测试TCP连接表OID生成
- 测试接口表OID生成
- 测试IP地址表OID生成

### 8.2 华为设备特殊表测试

- 测试OTS端口性能表OID生成
- 测试单板性能表OID生成
- 测试15分钟和24小时性能表

### 8.3 边出格式测试

- 测试不同输出格式的正确性
- 测试SNMP命令的生成
- 测试表格格式的生成

## 9. 性能考虑

1. MIB文件解析结果缓存
2. 大量OID生成的批处理
3. 异步处理长时间操作

## 10. 扩展性

1. 支持自定义表类型
2. 支持自定义输出格式
3. 支持更多设备厂商的特殊表