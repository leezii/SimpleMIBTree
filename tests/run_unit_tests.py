#!/usr/bin/env python3
"""
Run unit tests for the Flask MIB Parser application
"""
import sys
import os
import subprocess
import argparse

def run_tests(test_type="all", coverage=True, verbose=False):
    """Run tests with specified options"""
    
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test directory
    cmd.append("tests/")
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=80"
        ])
    
    # Filter by test type
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    
    # Add other options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        return e.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest:")
        print("pip install -r tests/requirements-test.txt")
        return 1

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run unit tests for Flask MIB Parser")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage", 
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(__file__))
    os.chdir(project_root)
    
    # Run tests
    exit_code = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=args.verbose
    )
    
    # Print results summary
    if exit_code == 0:
        print("\n✅ All tests passed!")
        if not args.no_coverage:
            print("📄 Coverage report generated in htmlcov/")
            print("🌐 Open htmlcov/index.html to view detailed coverage report")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
