#!/usr/bin/env python3
"""
Test ZIP file upload functionality
"""

import requests
import zipfile
import io
import os

def test_zip_upload():
    """Test ZIP file upload functionality"""
    
    # Create test ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add existing MIB files to ZIP
        mib_files = [
            'test_data/sample_mibs/CHILD-MIB.mib',
            'test_data/sample_mibs/RELATED-MIB.mib',
            'test_data/sample_mibs/SAMPLE-MIB.mib'
        ]
        
        for mib_file in mib_files:
            if os.path.exists(mib_file):
                zip_file.write(mib_file, os.path.basename(mib_file))
                print(f"Added {mib_file} to ZIP")
    
    zip_buffer.seek(0)
    
    # Send to Flask application
    url = 'http://127.0.0.1:5000/upload-mib'
    
    files = {'mib_files': ('test_mibs.zip', zip_buffer, 'application/zip')}
    
    try:
        print("Uploading ZIP file to server...")
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("Upload successful!")
            print(f"Parsing result: {result}")
            
            if result.get('success'):
                print(f"✅ Successfully parsed {result.get('total_objects', 0)} objects")
                if result.get('zip_info'):
                    for zip_info in result['zip_info']:
                        print(f"📦 ZIP file {zip_info['filename']}: extracted {zip_info['extracted_files']} MIB files")
                if result.get('modules'):
                    print("📋 Parsed modules:")
                    for module in result['modules']:
                        print(f"  - {module['name']}: {module['object_count']} objects")
            else:
                print(f"❌ Parsing failed: {result.get('error')}")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server, please ensure server is running at http://127.0.0.1:5000")
        print("   Start server with: cd src && python app.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == '__main__':
    test_zip_upload()
