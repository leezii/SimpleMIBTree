"""Routing module"""
import logging
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from file_handler import validate_and_process_files, save_uploaded_file, cleanup_file
from mib_parser import mib_parser

logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Navigation page (homepage)"""
    lang = session.get('language', request.args.get('lang', 'zh'))
    return render_template('index.html', lang=lang)

@main_bp.route('/mib-parser')
def mib_parser_page():
    """MIB parser page"""
    lang = session.get('language', request.args.get('lang', 'zh'))
    return render_template('mib_parser.html', lang=lang)

@main_bp.route('/oid-calculator')
def oid_calculator_page():
    """SNMP command generator page"""
    lang = session.get('language', request.args.get('lang', 'zh'))
    return render_template('oid_calculator.html', lang=lang)

@main_bp.route('/mib-oid-generator')
def mib_oid_generator_page():
    """MIB table OID generator page"""
    lang = session.get('language', request.args.get('lang', 'zh'))
    return render_template('mib_oid_generator.html', lang=lang)

@main_bp.route('/set-language')
def set_language():
    """Set language preference"""
    lang = request.args.get('lang')
    if lang in ['zh', 'en']:
        session['language'] = lang
        logger.info(f"Language set to: {lang}")
    # Redirect to previous page or homepage
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/upload-mib', methods=['POST'])
def upload_mib():
    """Handle MIB file upload and parsing"""
    try:
        # Check if single file or multi-file upload
        if 'mib_file' in request.files:
            # Single file upload (backward compatibility)
            file = request.files['mib_file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'})
            
            if file.filename.lower().endswith('.zip'):
                # Handle ZIP file
                files_data, error = validate_and_process_files(file)
                if error:
                    return jsonify({'success': False, 'error': error})
                
                # Parse all MIB files in ZIP
                result = mib_parser().parse_multiple_mib_files(files_data['files'])
                if result['success']:
                    result['zip_info'] = {
                        'filename': file.filename,
                        'extracted_files': len(files_data['files'])
                    }
                return result
            else:
                # Handle single MIB file
                file_path = save_uploaded_file(file)
                
                # Parse MIB file
                result = mib_parser().parse_mib_file(file_path)
                
                # Clean up temporary file
                cleanup_file(file_path)
                
                return jsonify(result)
        
        elif 'mib_files' in request.files:
            # Multi-file upload
            files = request.files.getlist('mib_files')
            
            files_data, error = validate_and_process_files(files)
            if error:
                return jsonify({'success': False, 'error': error})
            
            # Parse all MIB files
            result = mib_parser().parse_multiple_mib_files(files_data['files'])
            if result['success'] and files_data['zip_info']:
                result['zip_info'] = files_data['zip_info']
            return result
        
        else:
            return jsonify({'success': False, 'error': 'No file selected'})
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
