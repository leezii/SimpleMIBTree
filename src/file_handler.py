"""File handling module"""
import os
import zipfile
import io
import logging
from werkzeug.utils import secure_filename
from flask import current_app

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def extract_zip_file(zip_file):
    """Extract MIB files from ZIP file"""
    try:
        # Read ZIP file content to memory
        zip_content = zip_file.read()
        zip_file_obj = io.BytesIO(zip_content)
        
        extracted_files = []
        
        with zipfile.ZipFile(zip_file_obj, 'r') as zip_ref:
            # Check if ZIP file is safe (prevent path traversal attacks)
            for file_info in zip_ref.infolist():
                filename = file_info.filename
                
                # Skip directories and dangerous files
                if filename.endswith('/') or '..' in filename or filename.startswith('/'):
                    continue
                
                # Check if file extension is MIB file
                if '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mib', 'txt', 'my'}:
                    # Extract file content
                    with zip_ref.open(file_info) as extracted_file:
                        file_content = extracted_file.read().decode('utf-8', errors='ignore')
                        
                        # Create file-like object
                        class FileLikeObject:
                            def __init__(self, filename, content):
                                self.filename = filename
                                self.content = content
                            
                            def save(self, path):
                                with open(path, 'w', encoding='utf-8') as f:
                                    f.write(self.content)
                        
                        extracted_files.append(FileLikeObject(filename, file_content))
        
        return extracted_files
        
    except zipfile.BadZipFile:
        raise Exception("Invalid ZIP file format")
    except Exception as e:
        raise Exception(f"Error extracting ZIP file: {str(e)}")

def validate_and_process_files(files):
    """Validate and process uploaded files"""
    if not files or (hasattr(files, '__iter__') and len(files) > 0 and files[0].filename == ''):
        return None, 'No file selected'
    
    # Handle single file (backward compatibility)
    if hasattr(files, 'filename'):
        files = [files]
    
    valid_files = []
    invalid_files = []
    zip_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            if file.filename.lower().endswith('.zip'):
                zip_files.append(file)
            else:
                valid_files.append(file)
        else:
            invalid_files.append(file.filename)
    
    if invalid_files:
        return None, f'Invalid file types: {", ".join(invalid_files)}. Please upload .mib, .txt, .my or .zip files'
    
    # Process ZIP files
    all_extracted_files = []
    zip_info = []
    
    for zip_file in zip_files:
        try:
            extracted = extract_zip_file(zip_file)
            if extracted:
                all_extracted_files.extend(extracted)
                zip_info.append({
                    'filename': zip_file.filename,
                    'extracted_files': len(extracted)
                })
        except Exception as e:
            logger.error(f"Error extracting ZIP file {zip_file.filename}: {str(e)}")
            return None, f'Error extracting ZIP file {zip_file.filename}: {str(e)}'
    
    # Merge all files
    all_files = valid_files + all_extracted_files
    
    if not all_files:
        return None, 'No valid files'
    
    return {
        'files': all_files,
        'zip_info': zip_info if zip_info else None
    }, None

def save_uploaded_file(file):
    """Save uploaded file and return file path"""
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # Ensure upload directory exists
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    file.save(file_path)
    return file_path

def cleanup_file(file_path):
    """Clean up temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.warning(f"Error cleaning up file {file_path}: {str(e)}")
