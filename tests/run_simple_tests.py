#!/usr/bin/env python3
"""
Simple test runner for Flask MIB Parser application
"""
import sys
import os

def main():
    """Simple test runner"""
    print("🚀 Running Flask MIB Parser Unit Tests")
    print("=" * 50)
    
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    os.chdir(project_root)
    
    # Add src to Python path
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        import pytest
        
        # Run tests with basic configuration
        exit_code = pytest.main([
            'tests/',
            '-v',
            '--tb=short',
            '--disable-warnings'
        ])
        
        if exit_code == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code: {exit_code}")
        
        return exit_code
        
    except ImportError:
        print("❌ pytest not found. Please install with:")
        print("pip install pytest pytest-cov")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
