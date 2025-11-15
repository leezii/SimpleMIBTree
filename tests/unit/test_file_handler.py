"""Unit tests for file handler module"""
import os
import tempfile
import zipfile
import pytest
from unittest.mock import patch, Mock, mock_open
from file_handler import (
    allowed_file, extract_zip_file, validate_and_process_files,
    save_uploaded_file, cleanup_file
)

class TestFileHandler:
    """Test cases for file handler functions"""
    
    def test_allowed_file_valid_extensions(self, mock_flask_app):
        """Test allowed file validation with valid extensions"""
        with patch('file_handler.current_app', mock_flask_app):
            valid_files = [
                'test.mib',
                'test.txt',
                'test.my',
                'TEST.MIB',
                'test.TXT',
                'file.mib'
            ]
            
            for filename in valid_files:
                assert allowed_file(filename) is True, f"Failed for {filename}"
    
    def test_allowed_file_invalid_extensions(self, mock_flask_app):
        """Test allowed file validation with invalid extensions"""
        with patch('file_handler.current_app', mock_flask_app):
            invalid_files = [
                'test.exe',
                'test.dll',
                'test.sh',
                'test.py',
                'test.doc',
                'test.pdf',
                'test',
                'test.mib.exe'
            ]
            
            for filename in invalid_files:
                assert allowed_file(filename) is False, f"Failed for {filename}"
    
    def test_allowed_file_edge_cases(self, mock_flask_app):
        """Test allowed file validation with edge cases"""
        with patch('file_handler.current_app', mock_flask_app):
            assert allowed_file('.mib') is True
            assert allowed_file('') is False
            assert allowed_file(None) is False
            assert allowed_file('test.') is False
    
    def test_extract_zip_file_success(self):
        """Test successful ZIP file extraction"""
        # Create a temporary ZIP file in memory
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zip_file:
            zip_file.writestr('test1.mib', 'test content 1')
            zip_file.writestr('test2.txt', 'test content 2')
            zip_file.writestr('invalid.exe', 'invalid content')
            zip_file.writestr('subdir/test3.mib', 'test content 3')
        
        zip_content.seek(0)
        
        # Create mock file object
        mock_zip_file = Mock()
        mock_zip_file.read.return_value = zip_content.getvalue()
        
        extracted_files = extract_zip_file(mock_zip_file)
        
        assert len(extracted_files) == 3  # Should only extract MIB files
        filenames = [f.filename for f in extracted_files]
        assert 'test1.mib' in filenames
        assert 'test2.txt' in filenames
        assert 'subdir/test3.mib' in filenames
        assert 'invalid.exe' not in filenames
    
    def test_extract_zip_file_with_dangerous_paths(self):
        """Test ZIP extraction with dangerous paths"""
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zip_file:
            zip_file.writestr('../../../etc/passwd', 'dangerous content')
            zip_file.writestr('/etc/passwd', 'dangerous content')
            zip_file.writestr('safe.mib', 'safe content')
            zip_file.writestr('subdir/', '')  # Directory entry
        
        zip_content.seek(0)
        
        mock_zip_file = Mock()
        mock_zip_file.read.return_value = zip_content.getvalue()
        
        extracted_files = extract_zip_file(mock_zip_file)
        
        # Should only extract safe files
        assert len(extracted_files) == 1
        assert extracted_files[0].filename == 'safe.mib'
    
    def test_extract_zip_file_invalid_zip(self):
        """Test extraction of invalid ZIP file"""
        mock_zip_file = Mock()
        mock_zip_file.read.return_value = b'not a zip file'
        
        with pytest.raises(Exception) as exc_info:
            extract_zip_file(mock_zip_file)
        
        assert 'Invalid ZIP file format' in str(exc_info.value)
    
    def test_validate_and_process_files_single_file(self, mock_flask_app):
        """Test validation and processing of single file"""
        with patch('file_handler.current_app', mock_flask_app):
            # Create mock file
            mock_file = Mock()
            mock_file.filename = 'test.mib'
            
            files, error = validate_and_process_files(mock_file)
            
            assert error is None
            assert 'files' in files
            assert len(files['files']) == 1
            assert files['files'][0].filename == 'test.mib'
    
    def test_validate_and_process_files_multiple_files(self, mock_flask_app):
        """Test validation and processing of multiple files"""
        with patch('file_handler.current_app', mock_flask_app):
            # Create mock files
            mock_files = [
                Mock(filename='test1.mib'),
                Mock(filename='test2.txt'),
                Mock(filename='invalid.exe')
            ]
            
            files, error = validate_and_process_files(mock_files)
            
            assert error is None
            assert 'files' in files
            # Should only include valid files
            assert len(files['files']) == 2
            filenames = [f.filename for f in files['files']]
            assert 'test1.mib' in filenames
            assert 'test2.txt' in filenames
    
    def test_validate_and_process_files_invalid_types(self, mock_flask_app):
        """Test validation with invalid file types"""
        with patch('file_handler.current_app', mock_flask_app):
            mock_files = [
                Mock(filename='test.exe'),
                Mock(filename='test.dll')
            ]
            
            files, error = validate_and_process_files(mock_files)
            
            assert files is None
            assert 'Invalid file types' in error
            assert 'test.exe' in error
            assert 'test.dll' in error
    
    def test_validate_and_process_files_no_files(self, mock_flask_app):
        """Test validation with no files"""
        with patch('file_handler.current_app', mock_flask_app):
            files, error = validate_and_process_files([])
            
            assert files is None
            assert 'No file selected' in error
    
    def test_validate_and_process_files_empty_filename(self, mock_flask_app):
        """Test validation with empty filename"""
        with patch('file_handler.current_app', mock_flask_app):
            mock_file = Mock()
            mock_file.filename = ''
            
            files, error = validate_and_process_files(mock_file)
            
            assert files is None
            assert 'No file selected' in error
    
    def test_validate_and_process_files_with_zip(self, mock_flask_app):
        """Test validation with ZIP file containing MIB files"""
        import io
        
        with patch('file_handler.current_app', mock_flask_app):
            # Create ZIP file content
            zip_content = io.BytesIO()
            with zipfile.ZipFile(zip_content, 'w') as zip_file:
                zip_file.writestr('test1.mib', 'content 1')
                zip_file.writestr('test2.mib', 'content 2')
            
            zip_content.seek(0)
            
            mock_zip_file = Mock()
            mock_zip_file.filename = 'test.zip'
            mock_zip_file.read.return_value = zip_content.getvalue()
            
            files, error = validate_and_process_files(mock_zip_file)
            
            assert error is None
            assert 'files' in files
            assert 'zip_info' in files
            assert len(files['files']) == 2
            assert files['zip_info'][0]['filename'] == 'test.zip'
            assert files['zip_info'][0]['extracted_files'] == 2
    
    def test_save_uploaded_file(self, mock_flask_app):
        """Test saving uploaded file"""
        with patch('file_handler.current_app', mock_flask_app):
            with tempfile.TemporaryDirectory() as temp_dir:
                mock_flask_app.config['UPLOAD_FOLDER'] = temp_dir
                
                # Create mock file
                mock_file = Mock()
                mock_file.filename = 'test.mib'
                
                # Mock the save method
                file_path = os.path.join(temp_dir, 'test.mib')
                with open(file_path, 'w') as f:
                    f.write('test content')
                
                mock_file.save.side_effect = lambda path: open(path, 'w').write('test content')
                
                result_path = save_uploaded_file(mock_file)
                
                assert result_path == file_path
                assert os.path.exists(file_path)
    
    def test_cleanup_file_success(self):
        """Test successful file cleanup"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b'test content')
        
        # Ensure file exists
        assert os.path.exists(temp_path)
        
        # Cleanup file
        cleanup_file(temp_path)
        
        # File should be deleted
        assert not os.path.exists(temp_path)
    
    def test_cleanup_file_nonexistent(self):
        """Test cleanup of non-existent file"""
        # Should not raise exception
        cleanup_file('/nonexistent/file.mib')
    
    def test_cleanup_file_permission_error(self, monkeypatch):
        """Test cleanup with permission error"""
        # Mock os.remove to raise permission error
        def mock_remove(path):
            raise PermissionError("Permission denied")
        
        monkeypatch.setattr(os, 'remove', mock_remove)
        monkeypatch.setattr(os.path, 'exists', lambda x: True)
        
        # Should not raise exception, just log warning
        cleanup_file('/test/file.mib')

class TestFileHandlerEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_extract_zip_empty_zip(self):
        """Test extraction of empty ZIP file"""
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zip_file:
            pass  # Create empty ZIP
        
        zip_content.seek(0)
        
        mock_zip_file = Mock()
        mock_zip_file.read.return_value = zip_content.getvalue()
        
        extracted_files = extract_zip_file(mock_zip_file)
        
        assert len(extracted_files) == 0
    
    def test_extract_zip_with_subdirectories(self):
        """Test ZIP extraction with subdirectories"""
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zip_file:
            zip_file.writestr('dir1/test.mib', 'content 1')
            zip_file.writestr('dir1/subdir/test2.mib', 'content 2')
            zip_file.writestr('dir2/test3.txt', 'content 3')
        
        zip_content.seek(0)
        
        mock_zip_file = Mock()
        mock_zip_file.read.return_value = zip_content.getvalue()
        
        extracted_files = extract_zip_file(mock_zip_file)
        
        assert len(extracted_files) == 3
        filenames = [f.filename for f in extracted_files]
        assert 'dir1/test.mib' in filenames
        assert 'dir1/subdir/test2.mib' in filenames
        assert 'dir2/test3.txt' in filenames
    
    def test_validate_files_with_zip_extraction_error(self, mock_flask_app):
        """Test validation when ZIP extraction fails"""
        import io
        
        with patch('file_handler.current_app', mock_flask_app):
            # Create invalid ZIP content
            mock_zip_file = Mock()
            mock_zip_file.filename = 'invalid.zip'
            mock_zip_file.read.return_value = b'invalid zip content'
            
            files, error = validate_and_process_files(mock_zip_file)
            
            assert files is None
            assert 'Error extracting ZIP file' in error
    
    def test_save_file_with_special_characters(self, mock_flask_app):
        """Test saving file with special characters in filename"""
        with patch('file_handler.current_app', mock_flask_app):
            with tempfile.TemporaryDirectory() as temp_dir:
                mock_flask_app.config['UPLOAD_FOLDER'] = temp_dir
                
                # Test filename with special characters
                mock_file = Mock()
                mock_file.filename = 'test-file_123.mib'
                
                # Mock werkzeug's secure_filename function
                with patch('werkzeug.utils.secure_filename') as mock_secure:
                    mock_secure.return_value = 'test-file_123.mib'
                    
                    result_path = save_uploaded_file(mock_file)
                    
                    assert 'test-file_123.mib' in result_path
                    mock_secure.assert_called_once_with('test-file_123.mib')
    
    def test_validate_files_iterator_input(self, mock_flask_app):
        """Test validation with iterator input"""
        with patch('file_handler.current_app', mock_flask_app):
            # Create iterator of files
            file_list = [
                Mock(filename='test1.mib'),
                Mock(filename='test2.txt')
            ]
            file_iterator = iter(file_list)
            
            files, error = validate_and_process_files(file_iterator)
            
            assert error is None
            assert len(files['files']) == 2

class TestFileHandlerPerformance:
    """Test performance-related scenarios"""
    
    def test_large_zip_extraction(self):
        """Test extraction of large ZIP file"""
        # Create ZIP with many files
        zip_content = io.BytesIO()
        with zipfile.ZipFile(zip_content, 'w') as zip_file:
            for i in range(100):
                zip_file.writestr(f'test{i}.mib', f'content {i}')
        
        zip_content.seek(0)
        
        mock_zip_file = Mock()
        mock_zip_file.read.return_value = zip_content.getvalue()
        
        extracted_files = extract_zip_file(mock_zip_file)
        
        assert len(extracted_files) == 100
    
    def test_many_files_validation(self, mock_flask_app):
        """Test validation of many files"""
        with patch('file_handler.current_app', mock_flask_app):
            # Create many mock files
            mock_files = [Mock(filename=f'test{i}.mib') for i in range(1000)]
            
            files, error = validate_and_process_files(mock_files)
            
            assert error is None
            assert len(files['files']) == 1000

# Import required modules
import io
