"""pytest configuration and shared fixtures"""
import os
import sys
import tempfile
import pytest
from unittest.mock import Mock, patch

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def app():
    """Create and configure a test app"""
    import tempfile
    from app import create_app
    
    # Create a temporary directory for uploads
    temp_dir = tempfile.mkdtemp()
    
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'UPLOAD_FOLDER': temp_dir,
        'WTF_CSRF_ENABLED': False,
    })
    
    with app.app_context():
        yield app
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def sample_mib_content():
    """Sample MIB file content for testing"""
    return """SAMPLE-MIB DEFINITIONS ::= BEGIN

IMPORTS
    MODULE-IDENTITY, OBJECT-TYPE, enterprises FROM SNMPv2-SMI
    DisplayString FROM SNMPv2-TC;

sampleMIB MODULE-IDENTITY
    LAST-UPDATED "202301010000Z"
    ORGANIZATION "Test Organization"
    CONTACT-INFO "Test Contact"
    DESCRIPTION "Test MIB module"
    ::= { sampleMIB 1 }

sampleObjects OBJECT IDENTIFIER ::= { sampleMIB 1 }

sampleSystemInfo OBJECT IDENTIFIER ::= { sampleObjects 1 }

sampleSystemName OBJECT-TYPE
    SYNTAX DisplayString
    MAX-ACCESS read-only
    STATUS current
    DESCRIPTION "System name"
    ::= { sampleSystemInfo 1 }

sampleSystemVersion OBJECT-TYPE
    SYNTAX DisplayString
    MAX-ACCESS read-only
    STATUS current
    DESCRIPTION "System version"
    ::= { sampleSystemInfo 2 }

sampleConfigTable OBJECT-TYPE
    SYNTAX SEQUENCE OF SampleConfigEntry
    MAX-ACCESS not-accessible
    STATUS current
    DESCRIPTION "Configuration table"
    ::= { sampleObjects 2 }

SampleConfigEntry ::= SEQUENCE {
    sampleConfigIndex Integer32,
    sampleConfigValue DisplayString
}

sampleConfigIndex OBJECT-TYPE
    SYNTAX Integer32
    MAX-ACCESS read-only
    STATUS current
    DESCRIPTION "Configuration index"
    ::= { sampleConfigTable 1 }

sampleConfigValue OBJECT-TYPE
    SYNTAX DisplayString
    MAX-ACCESS read-write
    STATUS current
    DESCRIPTION "Configuration value"
    ::= { sampleConfigTable 1 1 }

END
"""

@pytest.fixture
def invalid_mib_content():
    """Invalid MIB file content for testing"""
    return """INVALID-MIB DEFINITIONS ::= BEGIN
This is not a valid MIB file
It has no proper structure
END
"""

@pytest.fixture
def empty_mib_content():
    """Empty MIB file content for testing"""
    return ""

@pytest.fixture
def sample_mib_file(sample_mib_content):
    """Create a temporary MIB file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mib', delete=False, encoding='utf-8') as f:
        f.write(sample_mib_content)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    try:
        os.unlink(temp_file)
    except OSError:
        pass

@pytest.fixture
def mock_file_object():
    """Create a mock file object for testing"""
    class MockFile:
        def __init__(self, filename, content):
            self.filename = filename
            self.content = content
        
        def save(self, path):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.content)
    
    return MockFile

@pytest.fixture
def standard_oid_map():
    """Standard OID mapping for testing"""
    return {
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
        'snmpV2': '1.3.6.1.6',
        'interfaces': '1.3.6.1.2.1.2',
        'ip': '1.3.6.1.2.1.4',
        'icmp': '1.3.6.1.2.1.5',
        'tcp': '1.3.6.1.2.1.6',
        'udp': '1.3.6.1.2.1.7',
        'egp': '1.3.6.1.2.1.8',
        'transmission': '1.3.6.1.2.1.10',
        'snmp': '1.3.6.1.2.1.11',
        'at': '1.3.6.1.2.1.3',
        'system': '1.3.6.1.2.1.1'
    }

@pytest.fixture
def mock_flask_app(standard_oid_map):
    """Create a mock Flask app with configuration"""
    app = Mock()
    app.config = {
        'STANDARD_OID_MAP': standard_oid_map,
        'UPLOAD_FOLDER': '/tmp/test_uploads',
        'ALLOWED_EXTENSIONS': {'mib', 'txt', 'my', 'zip'}
    }
    return app
