#!/usr/bin/env python3
"""
Script to test multi-MIB file upload functionality
"""

import requests
import json
import os

def test_single_file_upload():
    """Test single file upload"""
    print("=== Testing Single File Upload ===")
    
    url = 'http://127.0.0.1:5000/upload-mib'
    
    with open('test_data/sample_mibs/SAMPLE-MIB.mib', 'rb') as f:
        files = {'mib_file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Single file upload successful")
        print(f"   Module: {data.get('module')}")
        print(f"   Object count: {len(data.get('tree', []))}")
    else:
        print(f"❌ Single file upload failed: {response.status_code}")

def test_multi_file_upload():
    """Test multi-file upload"""
    print("\n=== Testing Multi-File Upload ===")
    
    url = 'http://127.0.0.1:5000/upload-mib'
    files = []
    
    # Add multiple files
    file_names = ['SAMPLE-MIB.mib', 'RELATED-MIB.mib', 'CHILD-MIB.mib']
    for file_name in file_names:
        file_path = f'test_data/sample_mibs/{file_name}'
        if os.path.exists(file_path):
            files.append(('mib_files', open(file_path, 'rb')))
    
    try:
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Multi-file upload successful")
            print(f"   Number of parsed modules: {len(data.get('modules', []))}")
            print(f"   Total object count: {data.get('total_objects', 0)}")
            
            # Display information for each module
            for module in data.get('modules', []):
                print(f"   - {module['name']}: {module['object_count']} objects")
        else:
            print(f"❌ Multi-file upload failed: {response.status_code}")
    
    finally:
        # Close files
        for _, file_obj in files:
            file_obj.close()

def test_invalid_files():
    """Test invalid file upload"""
    print("\n=== Testing Invalid File Upload ===")
    
    url = 'http://127.0.0.1:5000/upload-mib'
    
    # Create an invalid file
    with open('test_invalid.txt', 'w') as f:
        f.write('This is not a MIB file')
    
    with open('test_invalid.txt', 'rb') as f:
        files = {'mib_files': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        data = response.json()
        if not data.get('success'):
            print(f"✅ Correctly rejected invalid file: {data.get('error')}")
        else:
            print(f"❌ Unexpectedly accepted invalid file")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    # Clean up test file
    os.remove('test_invalid.txt')

if __name__ == '__main__':
    print("Starting multi-MIB file upload functionality test...\n")
    
    # Ensure Flask application is running
    try:
        response = requests.get('http://127.0.0.1:5000/mib-parser')
        if response.status_code != 200:
            print("❌ Flask application not running, please start it first: python3 src/app.py")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask application, please start it first: python3 src/app.py")
        exit(1)
    
    # Run tests
    test_single_file_upload()
    test_multi_file_upload()
    test_invalid_files()
    
    print("\n🎉 All tests completed!")
