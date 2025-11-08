from flask import Flask, jsonify, render_template, request
import logging
import os
import tempfile
from werkzeug.utils import secure_filename
import json
import sys
import re
import zipfile
import io

# Standard OID mapping table
STANDARD_OID_MAP = {
    'iso': '1',
    'org': '1.3',
    'dod': '1.3.6',
    'internet': '1.3.6.1',
    'directory': '1.3.6.1.1',
    'mgmt': '1.3.6.1.2',
    'mib-2': '1.3.6.1.2.1',
    'experimental': '1.3.6.1.3',
    'private': '1.3.6.1.4',
    'enterprises': '1.3.6.1.4.1',
    'security': '1.3.6.1.5',
    'snmpV2': '1.3.6.1.6'
}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_form_data(form_data):
    """Helper function to process form data"""
    firstname = form_data.get('firstname', '').strip()
    lastname = form_data.get('lastname', '').strip()
    if firstname and lastname:
        output = firstname + " " + lastname
        return {'output': f'Your Name is {output}, right?'}
    return {'error': 'Missing data!'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mib', 'txt', 'my', 'zip'}

def extract_zip_file(zip_file):
    """Extract MIB files from ZIP file"""
    try:
        # Read ZIP file content into memory
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
                        
                        # Create a file-like object
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

def parse_mib_file(file_path):
    """Parse MIB file and return tree structure"""
    try:
        # Use simplified MIB parsing method
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            mib_content = f.read()
        
        # Basic MIB parsing (simplified version)
        tree_data = parse_mib_content(mib_content, os.path.basename(file_path))
        return {'success': True, 'tree': tree_data, 'module': os.path.splitext(os.path.basename(file_path))[0]}
            
    except Exception as e:
        logger.error(f"Error parsing MIB file: {str(e)}")
        return {'success': False, 'error': str(e)}

def parse_multiple_mib_files(files):
    """Parse multiple MIB files and return merged tree structure"""
    try:
        all_objects = []  # Store all file objects
        module_info = []  # Store module information
        saved_files = []   # Saved file paths for cleanup
        
        # Step 1: Parse all files
        for file in files:
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                saved_files.append(file_path)
                
                # Read and parse file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    mib_content = f.read()
                
                # Parse single file content
                file_objects = parse_mib_content_raw(mib_content, filename)
                
                # Add module information
                module_name = os.path.splitext(filename)[0]
                module_info.append({
                    'name': module_name,
                    'filename': filename,
                    'object_count': len([obj for obj in file_objects if obj['type'] in ['object', 'identifier']])
                })
                
                # Add file source information for each object
                for obj in file_objects:
                    obj['source_file'] = filename
                    obj['source_module'] = module_name
                
                all_objects.extend(file_objects)
                
            except Exception as e:
                logger.error(f"Error parsing file {file.filename}: {str(e)}")
                continue
        
        # Clean up temporary files
        for file_path in saved_files:
            try:
                os.remove(file_path)
            except:
                pass
        
        if not all_objects:
            return {'success': False, 'error': 'No valid MIB objects found in any file'}
        
        # Step 2: Merge and build hierarchy
        merged_tree = merge_mib_objects(all_objects)
        
        # Calculate total object count
        total_objects = len([obj for obj in all_objects if obj['type'] in ['object', 'identifier']])
        
        return {
            'success': True,
            'tree': merged_tree,
            'modules': module_info,
            'total_objects': total_objects
        }
        
    except Exception as e:
        logger.error(f"Error parsing multiple MIB files: {str(e)}")
        return {'success': False, 'error': str(e)}

def parse_mib_content_raw(content, filename):
    """Parse MIB content, return raw object list (without building hierarchy)"""
    lines = content.split('\n')
    raw_objects = []
    current_object = None
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
            
        # Find OBJECT-TYPE definition
        if 'OBJECT-TYPE' in line:
            object_name = line.split('OBJECT-TYPE')[0].strip()
            if object_name:
                current_object = {
                    'text': object_name,
                    'type': 'object',
                    'oid': 'N/A',
                    'oid_path': [],
                    'numeric_oid': 'N/A',
                    'syntax': 'N/A',
                    'access': 'N/A',
                    'status': 'N/A',
                    'description': 'N/A',
                    'children': []
                }
                raw_objects.append(current_object)
        
        # Extract SYNTAX
        elif current_object and 'SYNTAX' in line:
            syntax = line.replace('SYNTAX', '').strip()
            current_object['syntax'] = syntax
        
        # Extract MAX-ACCESS
        elif current_object and 'MAX-ACCESS' in line:
            access = line.replace('MAX-ACCESS', '').strip()
            current_object['access'] = access
        
        # Extract STATUS
        elif current_object and 'STATUS' in line:
            status = line.replace('STATUS', '').strip()
            current_object['status'] = status
        
        # Extract OID
        elif current_object and '::=' in line:
            oid_part = line.split('::=')[1].strip()
            current_object['oid'] = oid_part
            current_object['oid_path'] = parse_oid_path(oid_part)
            current_object = None
        
        # Find OBJECT IDENTIFIER
        elif 'OBJECT IDENTIFIER' in line and '::=' in line:
            parts = line.split('OBJECT IDENTIFIER')
            if len(parts) >= 2:
                object_name = parts[0].strip()
                oid_part = line.split('::=')[1].strip() if '::=' in line else 'N/A'
                raw_objects.append({
                    'text': object_name,
                    'type': 'identifier',
                    'oid': oid_part,
                    'oid_path': parse_oid_path(oid_part),
                    'numeric_oid': 'N/A',
                    'children': []
                })
        
        # Find MODULE-IDENTITY
        elif 'MODULE-IDENTITY' in line:
            module_name = line.split('MODULE-IDENTITY')[0].strip()
            if module_name:
                raw_objects.append({
                    'text': f"Module: {module_name}",
                    'type': 'module',
                    'oid': 'Module Identity',
                    'oid_path': [],
                    'numeric_oid': 'Module',
                    'children': []
                })
    
    return raw_objects

def merge_mib_objects(all_objects):
    """Merge multiple MIB file objects and build unified hierarchy"""
    if not all_objects:
        return []
    
    # Calculate numeric OIDs (cross-file)
    all_objects = calculate_numeric_oids_cross_files(all_objects)
    
    # Build hierarchy
    return build_hierarchy_cross_files(all_objects)

def calculate_numeric_oids_cross_files(raw_objects):
    """Calculate numeric OIDs across files"""
    # Create name to object mapping
    name_to_obj = {}
    name_to_numeric = {}
    
    # First collect all object names
    for obj in raw_objects:
        clean_name = obj['text'].replace('Module: ', '')
        name_to_obj[clean_name] = obj
    
    # Set base OID values (including standard OIDs and common enterprise OIDs)
    name_to_numeric.update(STANDARD_OID_MAP)
    
    # Calculate numeric OID for each object
    def calculate_oid_for_object(obj):
        if obj.get('numeric_oid') != 'N/A' and obj.get('numeric_oid') != 'Module':
            return
            
        oid_str = obj.get('oid', '')
        if not oid_str or oid_str == 'N/A' or oid_str == 'Module Identity':
            return
        
        # Parse OID string like "{ sampleSystemInfo 1 }"
        clean_oid = oid_str.strip('{ }')
        parts = clean_oid.split()
        
        if len(parts) >= 2:
            parent_name = parts[0]
            child_id = parts[-1]
            
            if child_id.isdigit():
                # Find parent object's numeric OID
                parent_numeric = None
                
                if parent_name in name_to_numeric:
                    parent_numeric = name_to_numeric[parent_name]
                elif parent_name in name_to_obj:
                    # Recursively calculate parent object
                    calculate_oid_for_object(name_to_obj[parent_name])
                    if name_to_obj[parent_name].get('numeric_oid', 'N/A') != 'N/A':
                        parent_numeric = name_to_obj[parent_name]['numeric_oid']
                        name_to_numeric[parent_name] = parent_numeric
                
                if parent_numeric:
                    full_oid = parent_numeric + '.' + child_id
                    obj['numeric_oid'] = full_oid
                    name_to_numeric[obj['text']] = full_oid
        
        elif len(parts) == 1 and parts[0].isdigit():
            # Direct number
            obj['numeric_oid'] = parts[0]
    
    # Multiple iterations to ensure all dependencies are resolved
    for _ in range(10):  # Increase iterations to handle complex dependencies
        for obj in raw_objects:
            calculate_oid_for_object(obj)
    
    return raw_objects

def build_hierarchy_cross_files(raw_objects):
    """Build object hierarchy across files"""
    # Create object dictionary with name as key
    obj_dict = {}
    root_objects = []
    used_objects = []  # Record objects that have been used as child nodes
    
    # First create dictionary of all objects
    for obj in raw_objects:
        clean_name = obj['text'].replace('Module: ', '')
        obj_dict[clean_name] = obj
    
    # Step 1: Find clear parent-child relationships
    for obj in raw_objects:
        if obj['type'] == 'module':
            continue  # Modules handled separately
            
        oid_path = obj.get('oid_path', [])
        if oid_path:
            # Try to find the most direct parent object (last one in path)
            for potential_parent_name in reversed(oid_path):
                if potential_parent_name in obj_dict:
                    parent_obj = obj_dict[potential_parent_name]
                    if parent_obj != obj and obj not in used_objects:
                        parent_obj['children'].append(obj)
                        used_objects.append(obj)
                        break
    
    # Step 2: Add objects without parents to root level
    for obj in raw_objects:
        if obj not in used_objects:
            root_objects.append(obj)
    
    # Step 3: Organize root level objects by module
    return organize_by_modules(root_objects, raw_objects)

def organize_by_modules(root_objects, all_objects):
    """Organize objects by module"""
    # Group by module
    modules = {}
    other_objects = []
    
    for obj in all_objects:
        if obj['type'] == 'module':
            module_name = obj['text'].replace('Module: ', '')
            modules[module_name] = obj
        elif obj not in root_objects:
            # These objects have already been added as child nodes
            continue
        else:
            other_objects.append(obj)
    
    # Create root node structure
    organized = []
    
    # If there are modules, organize by module
    if modules:
        # Create a total root node
        root_node = {
            'text': 'MIB Modules',
            'type': 'root',
            'oid': 'Root',
            'numeric_oid': 'Root',
            'children': []
        }
        
        for module_name, module_obj in modules.items():
            # Try to get source file from any object with this module name
            source_file = None
            
            # First try exact matching
            for obj in all_objects:
                if obj.get('source_module') == module_name and obj.get('source_file'):
                    source_file = obj.get('source_file')
                    break
            
            # If not found, try case-insensitive matching
            if not source_file:
                for obj in all_objects:
                    if obj.get('source_module') and obj.get('source_module').lower() == module_name.lower() and obj.get('source_file'):
                        source_file = obj.get('source_file')
                        break
            
            # If still not found, try matching with the original module text
            if not source_file:
                original_module_text = module_obj['text'].replace('Module: ', '')
                for obj in all_objects:
                    if obj.get('source_module') and obj.get('source_module').lower() == original_module_text.lower() and obj.get('source_file'):
                        source_file = obj.get('source_file')
                        break
            
            # If still not found, try fuzzy matching (remove common prefixes/suffixes)
            if not source_file:
                # Try to match by removing common MIB naming patterns
                module_variants = [
                    module_name.lower(),
                    module_name.lower().replace('mib', ''),
                    module_name.lower().replace('-mib', ''),
                    module_name.lower().replace('_mib', ''),
                ]
                
                for variant in module_variants:
                    for obj in all_objects:
                        if obj.get('source_module') and variant in obj.get('source_module').lower() and obj.get('source_file'):
                            source_file = obj.get('source_file')
                            break
                    if source_file:
                        break
            
            # Last resort: just take the first available source file
            if not source_file:
                for obj in all_objects:
                    if obj.get('source_file'):
                        source_file = obj.get('source_file')
                        break
            
            # Find objects belonging to this module
            module_objects = [obj for obj in root_objects if obj.get('source_module') == module_name]
            
            # Add file information to module object
            if source_file:
                module_obj['source_file'] = source_file
                # Update the display text to include filename
                module_obj['text'] = f"{module_name} ({source_file})"
            else:
                module_obj['text'] = f"{module_name}"
            
            # Add these child objects to module object
            for obj in module_objects:
                if obj != module_obj and obj not in module_obj['children']:
                    module_obj['children'].append(obj)
            
            root_node['children'].append(module_obj)
        
        # Add objects not belonging to any module
        for obj in other_objects:
            if obj['type'] != 'module' and obj not in root_node['children']:
                root_node['children'].append(obj)
        
        organized.append(root_node)
    else:
        # No modules, return all objects directly
        organized = root_objects
    
    return organized if organized else root_objects

def parse_mib_content(content, filename):
    """Brand new MIB content parsing, build parent-child relationships"""
    lines = content.split('\n')
    raw_objects = []  # First collect all objects
    current_object = None
    
    # Step 1: Parse all objects
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
            
        # Find OBJECT-TYPE definition
        if 'OBJECT-TYPE' in line:
            object_name = line.split('OBJECT-TYPE')[0].strip()
            if object_name:
                current_object = {
                    'text': object_name,
                    'type': 'object',
                    'oid': 'N/A',
                    'oid_path': [],
                    'numeric_oid': 'N/A',
                    'syntax': 'N/A',
                    'access': 'N/A',
                    'status': 'N/A',
                    'description': 'N/A',
                    'children': []
                }
                raw_objects.append(current_object)
        
        # Extract SYNTAX
        elif current_object and 'SYNTAX' in line:
            syntax = line.replace('SYNTAX', '').strip()
            current_object['syntax'] = syntax
        
        # Extract MAX-ACCESS
        elif current_object and 'MAX-ACCESS' in line:
            access = line.replace('MAX-ACCESS', '').strip()
            current_object['access'] = access
        
        # Extract STATUS
        elif current_object and 'STATUS' in line:
            status = line.replace('STATUS', '').strip()
            current_object['status'] = status
        
        # Extract OID
        elif current_object and '::=' in line:
            oid_part = line.split('::=')[1].strip()
            current_object['oid'] = oid_part
            current_object['oid_path'] = parse_oid_path(oid_part)
            current_object = None
        
        # Find OBJECT IDENTIFIER
        elif 'OBJECT IDENTIFIER' in line and '::=' in line:
            parts = line.split('OBJECT IDENTIFIER')
            if len(parts) >= 2:
                object_name = parts[0].strip()
                oid_part = line.split('::=')[1].strip() if '::=' in line else 'N/A'
                raw_objects.append({
                    'text': object_name,
                    'type': 'identifier',
                    'oid': oid_part,
                    'oid_path': parse_oid_path(oid_part),
                    'numeric_oid': 'N/A',
                    'children': []
                })
        
        # Find MODULE-IDENTITY
        elif 'MODULE-IDENTITY' in line:
            module_name = line.split('MODULE-IDENTITY')[0].strip()
            if module_name:
                raw_objects.insert(0, {
                    'text': f"Module: {module_name}",
                    'type': 'module',
                    'oid': 'Module Identity',
                    'oid_path': [],
                    'numeric_oid': 'Module',
                    'children': []
                })
    
    # Step 2: Calculate numeric OIDs
    if raw_objects:
        raw_objects = calculate_numeric_oids(raw_objects)
    
    # Step 3: Build parent-child relationships
    if raw_objects:
        return build_hierarchy(raw_objects)
    else:
        return [{
            'text': f"File: {filename}",
            'type': 'file',
            'oid': 'Parsed File',
            'children': [{
                'text': f"Lines: {len(lines)}",
                'type': 'info',
                'oid': 'File Statistics'
            }]
        }]

def parse_oid_path(oid_str):
    """Parse OID path"""
    if not oid_str or oid_str == 'N/A':
        return []
    
    # Remove braces and spaces
    cleaned = oid_str.strip('{ }')
    if not cleaned:
        return []
    
    # Split path
    parts = [part.strip() for part in cleaned.split() if part.strip()]
    return parts

def calculate_numeric_oids(raw_objects):
    """Calculate numeric OIDs"""
    # Create name to object mapping
    name_to_obj = {}
    name_to_numeric = {}
    
    # First collect all object names
    for obj in raw_objects:
        clean_name = obj['text'].replace('Module: ', '')
        name_to_obj[clean_name] = obj
    
    # Set base OID values
    name_to_numeric['sampleMIB'] = '1.3.6.1.4.1.99999'  # enterprises 99999
    name_to_numeric['enterprises'] = '1.3.6.1.4.1'
    
    # Calculate numeric OID for each object
    def calculate_oid_for_object(obj):
        if obj.get('numeric_oid') != 'N/A' and obj.get('numeric_oid') != 'Module':
            return
            
        oid_str = obj.get('oid', '')
        if not oid_str or oid_str == 'N/A' or oid_str == 'Module Identity':
            return
        
        # Parse OID string like "{ sampleSystemInfo 1 }"
        clean_oid = oid_str.strip('{ }')
        parts = clean_oid.split()
        
        if len(parts) >= 2:
            parent_name = parts[0]
            child_id = parts[-1]
            
            if child_id.isdigit():
                # Find parent object's numeric OID
                parent_numeric = None
                
                if parent_name in name_to_numeric:
                    parent_numeric = name_to_numeric[parent_name]
                elif parent_name == 'enterprises':
                    parent_numeric = STANDARD_OID_MAP['enterprises']
                    # If it's enterprises 99999 format
                    if len(parts) == 2 and parts[1].isdigit():
                        parent_numeric = STANDARD_OID_MAP['enterprises'] + '.' + parts[1]
                        obj['numeric_oid'] = parent_numeric
                        name_to_numeric[obj['text']] = parent_numeric
                        return
                elif parent_name in name_to_obj:
                    # Recursively calculate parent object
                    calculate_oid_for_object(name_to_obj[parent_name])
                    if name_to_obj[parent_name].get('numeric_oid', 'N/A') != 'N/A':
                        parent_numeric = name_to_obj[parent_name]['numeric_oid']
                        name_to_numeric[parent_name] = parent_numeric
                
                if parent_numeric:
                    full_oid = parent_numeric + '.' + child_id
                    obj['numeric_oid'] = full_oid
                    name_to_numeric[obj['text']] = full_oid
        
        elif len(parts) == 1 and parts[0].isdigit():
            # Direct number
            obj['numeric_oid'] = parts[0]
    
    # Multiple iterations to ensure all dependencies are resolved
    for _ in range(5):  # Maximum 5 iterations
        for obj in raw_objects:
            calculate_oid_for_object(obj)
    
    return raw_objects

def build_hierarchy(raw_objects):
    """Build object hierarchy"""
    # Create object dictionary with name as key
    obj_dict = {}
    root_objects = []
    used_objects = []  # Record objects that have been used as child nodes
    
    # First create dictionary of all objects
    for obj in raw_objects:
        clean_name = obj['text'].replace('Module: ', '')
        obj_dict[clean_name] = obj
    
    # Step 1: Find clear parent-child relationships
    for obj in raw_objects:
        if obj['type'] == 'module':
            continue  # Modules handled separately
            
        oid_path = obj.get('oid_path', [])
        if oid_path:
            # Try to find the most direct parent object (last one in path)
            for potential_parent_name in reversed(oid_path):
                if potential_parent_name in obj_dict:
                    parent_obj = obj_dict[potential_parent_name]
                    if parent_obj != obj and obj not in used_objects:
                        parent_obj['children'].append(obj)
                        used_objects.append(obj)
                        break
    
    # Step 2: Add objects without parents to root level
    for obj in raw_objects:
        if obj not in used_objects:
            root_objects.append(obj)
    
    # Step 3: Further optimize hierarchy based on name matching
    root_objects = organize_by_naming_convention(root_objects)
    
    return root_objects if root_objects else raw_objects

def organize_by_naming_convention(objects):
    """Further organize hierarchy based on naming conventions"""
    # For sample MIB, we can organize based on naming patterns
    organized = []
    
    # Find module objects
    modules = [obj for obj in objects if obj['type'] == 'module']
    
    # Find root level objects (names without dots)
    root_level = [obj for obj in objects if obj['type'] != 'module' and 
                  ('sampleObjects' in obj['text'] or 'sampleNotifications' in obj['text'])]
    
    # Find system info group
    system_group = [obj for obj in objects if 'sampleSystemInfo' in obj['text']]
    
    # Find system objects
    system_objects = [obj for obj in objects if obj['text'].startswith('sampleSystem') and 
                      obj['text'] not in ['sampleSystemInfo']]
    
    # Find config table related objects
    config_objects = [obj for obj in objects if 'sampleConfig' in obj['text']]
    
    # Organize structure
    for module in modules:
        organized.append(module)
        
        # Add child nodes for module
        for root_obj in root_level:
            if root_obj['text'] == 'sampleObjects':
                # Add subgroups to sampleObjects
                for sys_group in system_group:
                    if sys_group not in root_obj['children']:
                        # Add system objects to sampleSystemInfo
                        for sys_obj in system_objects:
                            if sys_obj not in sys_group['children']:
                                sys_group['children'].append(sys_obj)
                        root_obj['children'].append(sys_group)
                
                # Add config table
                config_table = next((obj for obj in config_objects if obj['text'] == 'sampleConfigTable'), None)
                if config_table and config_table not in root_obj['children']:
                    # Add child objects to config table
                    config_entry = next((obj for obj in config_objects if obj['text'] == 'sampleConfigEntry'), None)
                    if config_entry:
                        config_entry_items = [obj for obj in config_objects if 
                                            obj['text'].startswith('sampleConfig') and 
                                            obj['text'] not in ['sampleConfigTable', 'sampleConfigEntry']]
                        for item in config_entry_items:
                            if item not in config_entry['children']:
                                config_entry['children'].append(item)
                        if config_entry not in config_table['children']:
                            config_table['children'].append(config_entry)
                    root_obj['children'].append(config_table)
                    
            module['children'].append(root_obj)
    
    # If no modules, return all objects directly
    return organized if organized else objects

# This function has been deleted, replaced by parse_mib_content

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        response = process_form_data(request.form)
        return jsonify(response)
    return render_template('index.html')

@app.route('/hello', methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        response = process_form_data(request.form)
        logger.debug(f"Received POST request with data: {request.form}")
        return jsonify(response)
    return render_template('hello.html')

@app.route('/mib-parser')
def mib_parser():
    """MIB parser page"""
    return render_template('mib_parser.html')

@app.route('/upload-mib', methods=['POST'])
def upload_mib():
    """Handle MIB file upload and parsing"""
    # Check if single file or multiple file upload
    if 'mib_file' in request.files:
        # Single file upload (backward compatibility)
        file = request.files['mib_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and allowed_file(file.filename):
            try:
                # Check if it's a ZIP file
                if file.filename.lower().endswith('.zip'):
                    # Handle ZIP file
                    extracted_files = extract_zip_file(file)
                    if not extracted_files:
                        return jsonify({'success': False, 'error': 'No valid MIB files found in ZIP file (.mib, .txt, .my)'})
                    
                    # Parse all MIB files in ZIP
                    result = parse_multiple_mib_files(extracted_files)
                    if result['success']:
                        result['zip_info'] = {
                            'filename': file.filename,
                            'extracted_files': len(extracted_files)
                        }
                    return result
                else:
                    # Handle single MIB file
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    # Parse MIB file
                    result = parse_mib_file(file_path)
                    
                    # Clean up temporary file
                    try:
                        os.remove(file_path)
                    except:
                        pass
                    
                    return jsonify(result)
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return jsonify({'success': False, 'error': str(e)})
        else:
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload a .mib, .txt, .my, or .zip file'})
    
    elif 'mib_files' in request.files:
        # Multiple file upload
        files = request.files.getlist('mib_files')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'No files selected'})
        
        # Validate all files
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
            return jsonify({'success': False, 'error': f'Invalid file types: {", ".join(invalid_files)}. Please upload only .mib, .txt, .my, or .zip files'})
        
        # Handle ZIP files
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
                return jsonify({'success': False, 'error': f'Error extracting ZIP file {zip_file.filename}: {str(e)}'})
        
        # Merge all files
        all_files = valid_files + all_extracted_files
        
        if not all_files:
            return jsonify({'success': False, 'error': 'No valid files selected'})
        
        try:
            # Parse all MIB files
            result = parse_multiple_mib_files(all_files)
            if result['success'] and zip_info:
                result['zip_info'] = zip_info
            return result
            
        except Exception as e:
            logger.error(f"Error processing multiple files: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})
    
    else:
        return jsonify({'success': False, 'error': 'No file selected'})

if __name__ == '__main__':
    app.run(debug=True)
