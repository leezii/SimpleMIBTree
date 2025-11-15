"""Unit tests for MIB parser module"""
import pytest
from unittest.mock import patch, Mock
from mib_parser import MIBParser, get_mib_parser, mib_parser

class TestMIBParser:
    """Test cases for MIBParser class"""
    
    def test_parser_initialization(self):
        """Test MIBParser initialization"""
        parser = MIBParser()
        assert parser._standard_oid_map is None
        assert hasattr(parser, 'standard_oid_map')
    
    @patch('mib_parser.current_app')
    def test_standard_oid_map_property(self, mock_current_app, standard_oid_map):
        """Test standard_oid_map property lazy loading"""
        mock_current_app.config = {'STANDARD_OID_MAP': standard_oid_map}
        
        parser = MIBParser()
        
        # First access should load from current_app
        oid_map = parser.standard_oid_map
        assert oid_map == standard_oid_map
        mock_current_app.config.__getitem__.assert_called_with('STANDARD_OID_MAP')
        
        # Second access should use cached value
        parser._standard_oid_map = {'test': 'cached'}
        assert parser.standard_oid_map == {'test': 'cached'}
    
    def test_parse_mib_file_success(self, sample_mib_file, mock_flask_app):
        """Test successful MIB file parsing"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            result = parser.parse_mib_file(sample_mib_file)
            
            assert result['success'] is True
            assert 'tree' in result
            assert 'module' in result
            assert result['module'] == 'SAMPLE-MIB'
            assert isinstance(result['tree'], list)
    
    def test_parse_mib_file_not_found(self, mock_flask_app):
        """Test parsing non-existent file"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            result = parser.parse_mib_file('nonexistent.mib')
            
            assert result['success'] is False
            assert 'error' in result
            assert 'No such file or directory' in result['error']
    
    def test_parse_oid_path_valid(self):
        """Test OID path parsing with valid input"""
        parser = MIBParser()
        
        # Test valid OID path
        oid_path = parser.parse_oid_path('{ sampleSystemInfo 1 }')
        assert oid_path == ['sampleSystemInfo', '1']
        
        # Test another valid format
        oid_path = parser.parse_oid_path('{ sampleObjects 2 1 }')
        assert oid_path == ['sampleObjects', '2', '1']
    
    def test_parse_oid_path_empty(self):
        """Test OID path parsing with empty input"""
        parser = MIBParser()
        
        assert parser.parse_oid_path('') == []
        assert parser.parse_oid_path('N/A') == []
        assert parser.parse_oid_path(None) == []
        assert parser.parse_oid_path('{ }') == []
        assert parser.parse_oid_path('{   }') == []
    
    def test_parse_mib_content_raw(self, sample_mib_content, mock_flask_app):
        """Test raw MIB content parsing"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            objects = parser.parse_mib_content_raw(sample_mib_content, 'test.mib')
            
            assert isinstance(objects, list)
            assert len(objects) > 0
            
            # Check for expected objects
            object_names = [obj['text'] for obj in objects]
            assert 'sampleSystemName' in object_names
            assert 'sampleSystemVersion' in object_names
            assert 'sampleConfigTable' in object_names
    
    def test_parse_mib_content_empty(self, empty_mib_content, mock_flask_app):
        """Test parsing empty MIB content"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            tree = parser.parse_mib_content(empty_mib_content, 'empty.mib')
            
            assert isinstance(tree, list)
            assert len(tree) > 0
            assert tree[0]['text'] == 'File: empty.mib'
            assert tree[0]['type'] == 'file'
    
    def test_parse_mib_content_invalid(self, invalid_mib_content, mock_flask_app):
        """Test parsing invalid MIB content"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            tree = parser.parse_mib_content(invalid_mib_content, 'invalid.mib')
            
            assert isinstance(tree, list)
            # Should return file info structure when no valid MIB objects found
            assert tree[0]['type'] == 'file'
    
    def test_calculate_numeric_oids(self, mock_flask_app):
        """Test numeric OID calculation"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            # Create mock objects
            raw_objects = [
                {
                    'text': 'sampleMIB',
                    'type': 'identifier',
                    'oid': '{ sampleMIB 1 }',
                    'oid_path': ['sampleMIB', '1'],
                    'numeric_oid': 'N/A',
                    'children': []
                },
                {
                    'text': 'sampleSystemName',
                    'type': 'object',
                    'oid': '{ sampleSystemInfo 1 }',
                    'oid_path': ['sampleSystemInfo', '1'],
                    'numeric_oid': 'N/A',
                    'children': []
                }
            ]
            
            result = parser.calculate_numeric_oids(raw_objects)
            assert isinstance(result, list)
            assert len(result) == len(raw_objects)
    
    def test_build_hierarchy(self, mock_flask_app):
        """Test hierarchy building"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            # Create mock objects with relationships
            raw_objects = [
                {
                    'text': 'Module: SAMPLE-MIB',
                    'type': 'module',
                    'oid': 'Module Identity',
                    'oid_path': [],
                    'numeric_oid': 'Module',
                    'children': []
                },
                {
                    'text': 'sampleObjects',
                    'type': 'identifier',
                    'oid': '{ sampleMIB 1 }',
                    'oid_path': ['sampleMIB', '1'],
                    'numeric_oid': '1.3.6.1.4.1.99999',
                    'children': []
                },
                {
                    'text': 'sampleSystemName',
                    'type': 'object',
                    'oid': '{ sampleObjects 1 }',
                    'oid_path': ['sampleObjects', '1'],
                    'numeric_oid': '1.3.6.1.4.1.99999.1',
                    'children': []
                }
            ]
            
            hierarchy = parser.build_hierarchy(raw_objects)
            assert isinstance(hierarchy, list)
    
    def test_merge_mib_objects(self, mock_flask_app):
        """Test merging multiple MIB objects"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            all_objects = [
                {
                    'text': 'sampleSystemName',
                    'type': 'object',
                    'oid': '{ sampleObjects 1 }',
                    'source_file': 'test.mib',
                    'source_module': 'SAMPLE-MIB',
                    'children': []
                }
            ]
            
            result = parser.merge_mib_objects(all_objects)
            assert isinstance(result, list)
    
    def test_get_oid_depth(self):
        """Test OID depth calculation"""
        parser = MIBParser()
        
        assert parser.get_oid_depth('1.3.6.1.4.1') == 6  # 1.3.6.1.4.1 = 6 parts
        assert parser.get_oid_depth('1.3.6') == 3
        assert parser.get_oid_depth('') == 999
        assert parser.get_oid_depth('N/A') == 999
        assert parser.get_oid_depth(None) == 999
    
    def test_get_parent_oid(self):
        """Test parent OID calculation"""
        parser = MIBParser()
        
        assert parser.get_parent_oid('1.3.6.1.4.1') == '1.3.6.1.4'
        assert parser.get_parent_oid('1.3.6') == '1.3.6'
        assert parser.get_parent_oid('1') == None
        assert parser.get_parent_oid('') == None
        assert parser.get_parent_oid('N/A') == None
    
    def test_parse_multiple_mib_files_success(self, mock_flask_app, mock_file_object):
        """Test successful multiple MIB files parsing"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            # Create mock files
            mock_files = [
                mock_file_object('test1.mib', 'sampleSystemName OBJECT-TYPE ::= { test 1 }'),
                mock_file_object('test2.mib', 'sampleSystemVersion OBJECT-TYPE ::= { test 2 }')
            ]
            
            result = parser.parse_multiple_mib_files(mock_files)
            
            assert result['success'] is True
            assert 'tree' in result
            assert 'modules' in result
            assert 'total_objects' in result
    
    def test_parse_multiple_mib_files_empty(self, mock_flask_app):
        """Test parsing empty file list"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            result = parser.parse_multiple_mib_files([])
            
            assert result['success'] is False
            assert 'error' in result
            assert 'No file selected' in result['error']
    
    def test_build_mib2_hierarchy(self, mock_flask_app):
        """Test MIB-II hierarchy building"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            # Create MIB-II objects
            mib2_objects = [
                {
                    'text': 'sysDescr',
                    'type': 'object',
                    'numeric_oid': '1.3.6.1.2.1.1.1',
                    'children': []
                },
                {
                    'text': 'ifNumber',
                    'type': 'object',
                    'numeric_oid': '1.3.6.1.2.1.2.1',
                    'children': []
                }
            ]
            
            result = parser.build_mib2_hierarchy(mib2_objects)
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0]['text'] == 'MIB-II Tree'
            assert result[0]['type'] == 'root'
    
    def test_build_oid_based_hierarchy(self, mock_flask_app):
        """Test OID-based hierarchy building"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            # Create objects with different OID depths
            objects = [
                {
                    'text': 'root',
                    'type': 'object',
                    'numeric_oid': '1.3.6.1.4.1',
                    'children': []
                },
                {
                    'text': 'child1',
                    'type': 'object',
                    'numeric_oid': '1.3.6.1.4.1.1',
                    'children': []
                },
                {
                    'text': 'child2',
                    'type': 'object',
                    'numeric_oid': '1.3.6.1.4.1.2',
                    'children': []
                }
            ]
            
            result = parser.build_oid_based_hierarchy(objects)
            
            assert isinstance(result, list)
            # Should build proper parent-child relationships
            root_object = next((obj for obj in result if obj['text'] == 'root'), None)
            assert root_object is not None
            assert len(root_object['children']) >= 1

class TestMIBParserModuleFunctions:
    """Test cases for module-level functions"""
    
    def test_get_mib_parser(self):
        """Test get_mib_parser function"""
        parser = get_mib_parser()
        assert isinstance(parser, MIBParser)
        assert hasattr(parser, 'parse_mib_file')
    
    def test_mib_parser_singleton(self):
        """Test mib_parser singleton function"""
        parser1 = mib_parser()
        parser2 = mib_parser()
        
        # Should return the same instance (singleton pattern)
        assert parser1 is parser2
        assert isinstance(parser1, MIBParser)

class TestMIBParserEdgeCases:
    """Test edge cases and error conditions"""
    
    @patch('mib_parser.current_app')
    def test_malformed_oid_parsing(self, mock_current_app, mock_flask_app):
        """Test parsing malformed OID strings"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            # Test various malformed OID formats
            test_cases = [
                '{',
                '}',
                '{{}}',
                '{ invalid }',
                '{ only one part }',
                '{ 123 }',
                '{ nonnumeric id }'
            ]
            
            for oid_str in test_cases:
                result = parser.parse_oid_path(oid_str)
                assert isinstance(result, list)
    
    @patch('mib_parser.current_app')
    def test_unicode_handling(self, mock_current_app, mock_flask_app):
        """Test Unicode character handling in MIB content"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            unicode_content = """UNICODE-MIB DEFINITIONS ::= BEGIN
unicodeTest OBJECT-TYPE
    SYNTAX DisplayString
    MAX-ACCESS read-only
    STATUS current
    DESCRIPTION "测试中文描述"
    ::= { unicodeTest 1 }
END
"""
            
            tree = parser.parse_mib_content(unicode_content, 'unicode.mib')
            assert isinstance(tree, list)
    
    @patch('mib_parser.current_app')
    def test_large_file_parsing(self, mock_current_app, mock_flask_app):
        """Test parsing large MIB files"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            # Generate a large MIB content
            large_content = "LARGE-MIB DEFINITIONS ::= BEGIN\n"
            for i in range(100):
                large_content += f"""object{i} OBJECT-TYPE
    SYNTAX Integer32
    MAX-ACCESS read-only
    STATUS current
    DESCRIPTION "Object {i}"
    ::= {{ largeTree {i} }}
"""
            large_content += "END\n"
            
            tree = parser.parse_mib_content(large_content, 'large.mib')
            assert isinstance(tree, list)
    
    @patch('mib_parser.current_app')
    def test_circular_reference_handling(self, mock_current_app, mock_flask_app):
        """Test handling of circular OID references"""
        with patch('mib_parser.current_app', mock_flask_app):
            parser = MIBParser()
            
            # Create content with potential circular reference
            circular_content = """CIRCULAR-MIB DEFINITIONS ::= BEGIN
objectA OBJECT-TYPE
    SYNTAX Integer32
    MAX-ACCESS read-only
    STATUS current
    DESCRIPTION "Object A"
    ::= { objectB 1 }

objectB OBJECT-TYPE
    SYNTAX Integer32
    MAX-ACCESS read-only
    STATUS current
    DESCRIPTION "Object B"
    ::= { objectA 1 }
END
"""
            
            # Should not crash or hang
            tree = parser.parse_mib_content(circular_content, 'circular.mib')
            assert isinstance(tree, list)
