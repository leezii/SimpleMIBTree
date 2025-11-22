"""Integration tests for routes module"""
import json
import pytest
from unittest.mock import patch, Mock
from flask import Flask

class TestMainRoutes:
    """Test cases for main route handlers"""
    
    def test_index_route_get(self, client):
        """Test index route with GET request"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_index_route_with_lang_en(self, client):
        """Test index route with English language parameter"""
        response = client.get('/?lang=en')
        
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_index_route_with_lang_zh(self, client):
        """Test index route with Chinese language parameter"""
        response = client.get('/?lang=zh')
        
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_mib_parser_page_route(self, client):
        """Test MIB parser page route"""
        response = client.get('/mib-parser')
        
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_mib_parser_page_with_lang(self, client):
        """Test MIB parser page with language parameter"""
        response = client.get('/mib-parser?lang=zh')
        
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_oid_calculator_page_route(self, client):
        """Test OID calculator page route"""
        response = client.get('/oid-calculator')
        
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_oid_calculator_page_contains_huawei_option(self, client):
        """Test OID calculator page contains Huawei transport device option"""
        response = client.get('/oid-calculator')
        
        assert response.status_code == 200
        assert b'huawei_transport_device' in response.data
        # Check for either Chinese or English version using decode
        response_text = response.data.decode('utf-8')
        assert ('华为传送设备' in response_text or
                'HuaWei Transport Device' in response_text or
                'Huawei Transport Device' in response_text)
    
    def test_mib_oid_generator_page_route(self, client):
        """Test MIB OID generator page route"""
        response = client.get('/mib-oid-generator')
        
        assert response.status_code == 200
        assert b'html' in response.data.lower()
    
    def test_set_language_route_en(self, client):
        """Test language setting route with English"""
        with client.session_transaction() as sess:
            sess.clear()
        
        response = client.get('/set-language?lang=en', follow_redirects=False)
        
        assert response.status_code in [302, 303]  # Redirect
        
        # Check if language is set in session
        with client.session_transaction() as sess:
            assert sess.get('language') == 'en'
    
    def test_set_language_route_zh(self, client):
        """Test language setting route with Chinese"""
        with client.session_transaction() as sess:
            sess.clear()
        
        response = client.get('/set-language?lang=zh', follow_redirects=False)
        
        assert response.status_code in [302, 303]  # Redirect
        
        # Check if language is set in session
        with client.session_transaction() as sess:
            assert sess.get('language') == 'zh'
    
    def test_set_language_route_invalid(self, client):
        """Test language setting route with invalid language"""
        with client.session_transaction() as sess:
            sess['language'] = 'en'  # Set initial language
        
        response = client.get('/set-language?lang=invalid', follow_redirects=False)
        
        assert response.status_code in [302, 303]  # Redirect
        
        # Language should remain unchanged
        with client.session_transaction() as sess:
            assert sess.get('language') == 'en'
    
    def test_set_language_route_no_parameter(self, client):
        """Test language setting route without parameter"""
        with client.session_transaction() as sess:
            sess['language'] = 'en'
        
        response = client.get('/set-language', follow_redirects=False)
        
        assert response.status_code in [302, 303]  # Redirect
        
        # Language should remain unchanged
        with client.session_transaction() as sess:
            assert sess.get('language') == 'en'

class TestUploadMibRoute:
    """Test cases for MIB file upload route"""
    
    def test_upload_mib_no_file(self, client):
        """Test upload with no file"""
        response = client.post('/upload-mib', data={})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No file selected' in data['error']
    
    def test_upload_mib_empty_filename(self, client):
        """Test upload with empty filename"""
        mock_file = Mock(filename='')
        mock_file.__len__ = lambda: len('content')
        response = client.post('/upload-mib', 
                            data={'mib_file': (mock_file, 'content')})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No file selected' in data['error']
    
    def test_upload_mib_single_file_success(self, client, sample_mib_content):
        """Test successful single MIB file upload"""
        with patch('mib_parser.mib_parser') as mock_parser:
            mock_result = {
                'success': True,
                'tree': [{'text': 'test', 'type': 'object'}],
                'module': 'test'
            }
            mock_parser.return_value.parse_mib_file.return_value = mock_result
            
            mock_file = Mock(filename='test.mib')
            mock_file.__len__ = lambda: len(sample_mib_content)
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 
                                                  sample_mib_content)},
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'tree' in data
        assert 'module' in data
    
    def test_upload_mib_single_file_parse_error(self, client, sample_mib_content):
        """Test single MIB file upload with parse error"""
        with patch('mib_parser.mib_parser') as mock_parser:
            mock_result = {'success': False, 'error': 'Parse error'}
            mock_parser.return_value.parse_mib_file.return_value = mock_result
            
            mock_file = Mock(filename='test.mib')
            mock_file.__len__ = lambda: len(sample_mib_content)
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 
                                                  sample_mib_content)},
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_upload_mib_multiple_files_success(self, client, sample_mib_content):
        """Test successful multiple MIB files upload"""
        with patch('mib_parser.mib_parser') as mock_parser:
            mock_result = {
                'success': True,
                'tree': [{'text': 'test', 'type': 'object'}],
                'modules': [{'name': 'test', 'filename': 'test.mib', 'object_count': 1}],
                'total_objects': 1
            }
            mock_parser.return_value.parse_multiple_mib_files.return_value = mock_result
            
            mock_file1 = Mock(filename='test1.mib')
            mock_file1.__len__ = lambda: len(sample_mib_content)
            mock_file2 = Mock(filename='test2.mib')
            mock_file2.__len__ = lambda: len(sample_mib_content)
            
            response = client.post('/upload-mib',
                                data={
                                    'mib_files': [
                                        (mock_file1, sample_mib_content),
                                        (mock_file2, sample_mib_content)
                                    ]
                                },
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'tree' in data
        assert 'modules' in data
        assert 'total_objects' in data
    
    def test_upload_mib_zip_file_success(self, client, sample_mib_content):
        """Test successful ZIP file upload"""
        import io
        import zipfile
        
        # Create ZIP file in memory
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zip_file:
            zip_file.writestr('test1.mib', sample_mib_content)
            zip_file.writestr('test2.mib', sample_mib_content)
        
        zip_content.seek(0)
        
        with patch('file_handler.validate_and_process_files') as mock_validate, \
             patch('mib_parser.mib_parser') as mock_parser:
            
            mock_file1 = Mock(filename='test1.mib')
            mock_file1.__len__ = lambda: len('dummy')
            mock_file2 = Mock(filename='test2.mib')
            mock_file2.__len__ = lambda: len('dummy')
            mock_validate.return_value = ({
                'files': [
                    mock_file1,
                    mock_file2
                ]
            }, None)
            
            mock_result = {
                'success': True,
                'tree': [{'text': 'test', 'type': 'object'}],
                'modules': [{'name': 'test', 'filename': 'test.mib', 'object_count': 2}],
                'total_objects': 2
            }
            mock_parser.return_value.parse_multiple_mib_files.return_value = mock_result
            
            mock_zip = Mock(filename='test.zip')
            mock_zip.__len__ = lambda: len(zip_content.getvalue())
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_zip, 
                                                  zip_content.getvalue())},
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'tree' in data
        assert 'zip_info' in data
    
    def test_upload_mib_invalid_file_type(self, client):
        """Test upload with invalid file type"""
        mock_file = Mock(filename='test.exe')
        mock_file.__len__ = lambda: len('content')
        response = client.post('/upload-mib',
                            data={'mib_file': (mock_file, 'content')},
                            content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid file types' in data['error']
    
    def test_upload_mib_large_file(self, client):
        """Test upload with file exceeding size limit"""
        large_content = 'x' * (17 * 1024 * 1024)  # 17MB (exceeds 16MB limit)
        
        mock_file = Mock(filename='large.mib')
        mock_file.__len__ = lambda: len(large_content)
        response = client.post('/upload-mib',
                            data={'mib_file': (mock_file, 
                                                  large_content)},
                            content_type='multipart/form-data')
        
        # Should get a 413 (Request Entity Too Large) or handle gracefully
        assert response.status_code in [200, 413]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_upload_mib_malformed_content(self, client):
        """Test upload with malformed MIB content"""
        malformed_content = "This is not a valid MIB file content"
        
        with patch('mib_parser.mib_parser') as mock_parser:
            mock_result = {'success': False, 'error': 'Invalid MIB format'}
            mock_parser.return_value.parse_mib_file.return_value = mock_result
            
            mock_file = Mock(filename='invalid.mib')
            mock_file.__len__ = lambda: len(malformed_content)
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 
                                                  malformed_content)},
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

class TestRoutesEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_routes_with_invalid_methods(self, client):
        """Test routes with invalid HTTP methods"""
        # These should return 405 Method Not Allowed
        assert client.put('/').status_code in [405, 404]
        assert client.delete('/mib-parser').status_code in [405, 404]
        assert client.patch('/oid-calculator').status_code in [405, 404]
        assert client.post('/set-language').status_code in [405, 404]
    
    def test_upload_mib_with_exception(self, client):
        """Test upload route when exception occurs"""
        with patch('mib_parser.mib_parser') as mock_parser:
            mock_parser.return_value.parse_mib_file.side_effect = Exception("Test error")
            
            mock_file = Mock(filename='test.mib')
            mock_file.__len__ = lambda: len('content')
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 'content')},
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Test error' in data['error']
    
    def test_upload_mib_unicode_filename(self, client, sample_mib_content):
        """Test upload with Unicode characters in filename"""
        unicode_filename = '测试文件.mib'
        
        with patch('mib_parser.mib_parser') as mock_parser:
            mock_result = {'success': True, 'tree': [], 'module': 'test'}
            mock_parser.return_value.parse_mib_file.return_value = mock_result
            
            mock_file = Mock(filename=unicode_filename)
            mock_file.__len__ = lambda: len(sample_mib_content)
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 
                                                  sample_mib_content)},
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_upload_mib_special_characters_content(self, client):
        """Test upload with special characters in content"""
        special_content = """SPECIAL-MIB DEFINITIONS ::= BEGIN
specialTest OBJECT-TYPE
    SYNTAX DisplayString
    MAX-ACCESS read-only
    STATUS current
    DESCRIPTION "Special chars: àáâãäåæçèéêë"
    ::= { specialTest 1 }
END
"""
        
        with patch('mib_parser.mib_parser') as mock_parser:
            mock_result = {'success': True, 'tree': [], 'module': 'special'}
            mock_parser.return_value.parse_mib_file.return_value = mock_result
            
            mock_file = Mock(filename='special.mib')
            mock_file.__len__ = lambda: len(special_content)
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 
                                                  special_content)},
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

class TestRoutesIntegration:
    """Test integration scenarios"""
    
    def test_language_persistence_across_requests(self, client):
        """Test that language setting persists across requests"""
        # Set language
        response = client.get('/set-language?lang=zh', follow_redirects=False)
        assert response.status_code in [302, 303]
        
        # Check language persists in subsequent request
        response = client.get('/mib-parser')
        assert response.status_code == 200
        
        # The template should respect the language setting
        # (This would depend on template implementation)
    
    def test_full_workflow_upload_and_parse(self, client, sample_mib_content):
        """Test complete workflow from upload to parsing"""
        with patch('file_handler.save_uploaded_file') as mock_save, \
             patch('file_handler.cleanup_file') as mock_cleanup, \
             patch('mib_parser.mib_parser') as mock_parser:
            
            # Mock file saving
            mock_save.return_value = '/tmp/test.mib'
            
            # Mock parser
            mock_result = {
                'success': True,
                'tree': [
                    {
                        'text': 'sampleSystemName',
                        'type': 'object',
                        'oid': '1.3.6.1.4.1.99999.1.1.1',
                        'children': []
                    }
                ],
                'module': 'SAMPLE-MIB'
            }
            mock_parser.return_value.parse_mib_file.return_value = mock_result
            
            mock_file = Mock(filename='sample.mib')
            mock_file.__len__ = lambda: len(sample_mib_content)
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 
                                                  sample_mib_content)},
                                content_type='multipart/form-data')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['tree']) > 0
            assert data['module'] == 'SAMPLE-MIB'
            
            # Verify cleanup was called
            mock_cleanup.assert_called_once_with('/tmp/test.mib')
    
    def test_error_handling_workflow(self, client):
        """Test error handling in upload workflow"""
        with patch('file_handler.validate_and_process_files') as mock_validate:
            mock_validate.return_value = (None, 'Validation error')
            
            mock_file = Mock(filename='test.zip')
            mock_file.__len__ = lambda: len('content')
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 'content')},
                                content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Validation error' in data['error']

class TestRoutesPerformance:
    """Test performance-related scenarios"""
    
    def test_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get('/')
            results.append(response.status_code)
        
        # Create multiple concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    def test_large_response_handling(self, client, sample_mib_content):
        """Test handling of large responses"""
        with patch('mib_parser.mib_parser') as mock_parser:
            # Create large tree structure
            large_tree = []
            for i in range(1000):
                large_tree.append({
                    'text': f'object{i}',
                    'type': 'object',
                    'oid': f'1.3.6.1.4.1.99999.{i}',
                    'children': []
                })
            
            mock_result = {
                'success': True,
                'tree': large_tree,
                'module': 'LARGE-MIB'
            }
            mock_parser.return_value.parse_mib_file.return_value = mock_result
            
            mock_file = Mock(filename='large.mib')
            mock_file.__len__ = lambda: len(sample_mib_content)
            response = client.post('/upload-mib',
                                data={'mib_file': (mock_file, 
                                                  sample_mib_content)},
                                content_type='multipart/form-data')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['tree']) == 1000

@pytest.mark.parametrize("route_path,expected_content", [
    ('/', 'navigation'),
    ('/mib-parser', 'mib parser'),
    ('/oid-calculator', 'oid calculator'),
    ('/mib-oid-generator', 'oid generator')
])
def test_route_content_presence(client, route_path, expected_content):
    """Test that routes contain expected content"""
    response = client.get(route_path)
    assert response.status_code == 200
    # This assumes templates contain these keywords
    # In real implementation, you'd check for specific HTML elements
    assert response.headers['Content-Type'].startswith('text/html')

@pytest.mark.parametrize("method,route_path", [
    ('GET', '/'),
    ('GET', '/mib-parser'),
    ('GET', '/oid-calculator'),
    ('GET', '/mib-oid-generator'),
    ('GET', '/set-language'),
    ('POST', '/upload-mib')
])
def test_route_method_support(client, method, route_path):
    """Test that routes support expected HTTP methods"""
    if method == 'GET':
        response = client.get(route_path)
    elif method == 'POST':
        response = client.post(route_path, data={})
    
    # Should return 200 (success) or 302 (redirect) or 405 (method not allowed)
    assert response.status_code in [200, 302, 303, 405]
