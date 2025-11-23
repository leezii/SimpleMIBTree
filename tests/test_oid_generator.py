"""
OID生成器测试用例
"""

import pytest
import json
from src.oid_generator import OIDGenerator, TableColumn, IndexColumn, MibTable
from src.mib_manager import get_mib_manager
from src.mib_parser import get_mib_parser
from src.app import create_app

@pytest.fixture(scope='module')
def app_context():
    """创建Flask应用上下文"""
    app = create_app()
    with app.app_context():
        yield app


class TestOIDGenerator:
    """OID生成器测试类"""
    
    @pytest.fixture
    def oid_generator(self, app_context):
        """创建OID生成器实例"""
        mib_manager = get_mib_manager()
        mib_parser = get_mib_parser()
        return OIDGenerator(mib_manager, mib_parser)
    
    def test_get_device_mib_tables(self, oid_generator):
        """测试获取设备MIB表"""
        result = oid_generator.get_device_mib_tables('dc908')
        
        assert result['success'] is True
        assert 'tables' in result['data']
        assert len(result['data']['tables']) > 0
        
        # 检查华为特殊表
        table_names = [table['name'] for table in result['data']['tables']]
        assert 'ots-port' in table_names
        assert 'board' in table_names
        assert 'pm-24h' in table_names
    
    def test_generate_huawei_ots_oid(self, oid_generator):
        """测试生成华为OTS端口OID"""
        result = oid_generator.generate_oid(
            device_id='dc908',
            table_name='ots-port',
            index_values=['1-1-1-OTS1'],
            selected_columns=['ots-portPer15MCurMonValue', 'ots-portPer15MCurVldty'],
            output_format='oid'
        )
        
        assert result['success'] is True
        assert 'generated_oids' in result['data']
        assert len(result['data']['generated_oids']) == 2
        
        # 检查生成的OID格式
        oids = [oid['oid'] for oid in result['data']['generated_oids']]
        assert all(oid.startswith('1.3.6.1.4.1.2011.2.25.3.40.50.82') for oid in oids)
    
    def test_generate_snmpget_commands(self, oid_generator):
        """测试生成SNMP get命令"""
        result = oid_generator.generate_oid(
            device_id='dc908',
            table_name='board',
            index_values=['1-1-1'],
            selected_columns=['boardPer15MCurMonValue'],
            output_format='snmpget',
            target_ip='192.168.1.100',
            community='public',
            snmp_version='2c'
        )
        
        assert result['success'] is True
        assert len(result['data']['generated_oids']) == 1
        
        generated = result['data']['generated_oids'][0]
        assert 'command' in generated
        assert 'snmpget -v2c -c public 192.168.1.100' in generated['command']
    
    def test_get_templates(self, oid_generator):
        """测试获取模板"""
        result = oid_generator.get_templates()
        
        assert result['success'] is True
        assert 'templates' in result['data']
        
        templates = result['data']['templates']
        assert 'huawei_ots_performance' in templates
        assert 'huawei_board_performance' in templates
        assert 'interface_basic' in templates
        assert 'tcp_connections' in templates
    
    def test_get_huawei_tables(self, oid_generator):
        """测试获取华为表配置"""
        result = oid_generator.get_huawei_tables()
        
        assert result['success'] is True
        assert 'huawei_tables' in result['data']
        
        huawei_tables = result['data']['huawei_tables']
        assert 'ots-port' in huawei_tables
        assert 'board' in huawei_tables
        assert 'pm-24h' in huawei_tables
    
    def test_invalid_device_type(self, oid_generator):
        """测试无效设备类型"""
        result = oid_generator.get_device_mib_tables('invalid_device')
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_invalid_table_name(self, oid_generator):
        """测试无效表名"""
        result = oid_generator.generate_oid(
            device_id='dc908',
            table_name='invalid_table',
            index_values=['test'],
            selected_columns=['test_column']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_invalid_index_values(self, oid_generator):
        """测试无效索引值"""
        result = oid_generator.generate_oid(
            device_id='dc908',
            table_name='ots-port',
            index_values=[],  # 空索引值
            selected_columns=['ots-portPer15MCurMonValue']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_invalid_columns(self, oid_generator):
        """测试无效列名"""
        result = oid_generator.generate_oid(
            device_id='dc908',
            table_name='ots-port',
            index_values=['1-1-1-OTS1'],
            selected_columns=['invalid_column']
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_table_column_processing(self):
        """测试表列处理"""
        # 创建测试表
        table = MibTable(
            name='test_table',
            oid='1.3.6.1.4.1.9999.1',
            description='测试表',
            type='standard',
            columns=[
                TableColumn(name='testColumn1', oid='1', description='测试列1', syntax='INTEGER'),
                TableColumn(name='testColumn2', oid='2', description='测试列2', syntax='DisplayString')
            ],
            index_columns=[
                IndexColumn(name='testIndex', oid='1', type='INTEGER', description='测试索引')
            ]
        )
        
        # 测试转换为字典
        oid_generator = OIDGenerator(None, None)
        table_dict = oid_generator._table_to_dict(table)
        
        assert table_dict['name'] == 'test_table'
        assert table_dict['oid'] == '1.3.6.1.4.1.9999.1'
        assert len(table_dict['columns']) == 2
        assert len(table_dict['index_columns']) == 1
        
        # 测试从字典转换回来
        restored_table = oid_generator._dict_to_table(table_dict)
        assert restored_table.name == table.name
        assert restored_table.oid == table.oid
        assert len(restored_table.columns) == len(table.columns)
    
    def test_index_value_processing(self):
        """测试索引值处理"""
        oid_generator = OIDGenerator(None, None)
        
        # 测试不同类型的索引值
        index_columns = [
            IndexColumn(name='ipIndex', oid='1', type='IpAddress', description='IP索引'),
            IndexColumn(name='intIndex', oid='2', type='INTEGER', description='整数索引'),
            IndexColumn(name='strIndex', oid='3', type='DisplayString', description='字符串索引')
        ]
        
        index_values = ['192.168.1.1', '100', 'test']
        processed = oid_generator._process_index_values(index_values, index_columns)
        
        assert len(processed) == 3
        assert processed[0] == '192.168.1.1'  # IP地址保持原样
        assert processed[1] == '100'  # 数字转换为字符串
        assert '.'.join(processed[2].split('.')) == '.'.join(str(ord(c)) for c in 'test')  # 字符串转换为ASCII码


class TestOIDGeneratorIntegration:
    """OID生成器集成测试"""
    
    def test_full_workflow(self, app_context):
        """测试完整工作流程"""
        # 创建OID生成器
        mib_manager = get_mib_manager()
        mib_parser = get_mib_parser()
        oid_generator = OIDGenerator(mib_manager, mib_parser)
        
        # 1. 获取设备类型列表
        device_result = oid_generator.get_device_mib_tables('dc908')
        assert device_result['success'] is True
        
        # 2. 选择表并生成OID
        oid_result = oid_generator.generate_oid(
            device_id='dc908',
            table_name='ots-port',
            index_values=['1-1-1-OTS1'],
            selected_columns=['ots-portPer15MCurMonValue'],
            output_format='snmpget',
            target_ip='192.168.1.100',
            community='public',
            snmp_version='2c'
        )
        assert oid_result['success'] is True
        
        # 3. 验证生成的命令
        generated = oid_result['data']['generated_oids'][0]
        assert 'snmpget' in generated['command']
        assert '192.168.1.100' in generated['command']
        assert 'public' in generated['command']
        assert generated['oid'].startswith('1.3.6.1.4.1.2011.2.25.3.40.50.82')
    
    def test_template_usage(self, app_context):
        """测试模板使用"""
        mib_manager = get_mib_manager()
        mib_parser = get_mib_parser()
        oid_generator = OIDGenerator(mib_manager, mib_parser)
        
        # 获取模板
        template_result = oid_generator.get_templates()
        assert template_result['success'] is True
        
        templates = template_result['data']['templates']
        
        # 使用华为OTS性能模板
        if 'huawei_ots_performance' in templates:
            template = templates['huawei_ots_performance']
            
            # 根据模板生成OID
            oid_result = oid_generator.generate_oid(
                device_id='dc908',
                table_name='ots-port',
                index_values=template['index_values'],
                selected_columns=template['columns'],
                output_format=template['output_format']
            )
            
            assert oid_result['success'] is True
            assert len(oid_result['data']['generated_oids']) == len(template['columns'])


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])