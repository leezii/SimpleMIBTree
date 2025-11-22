"""Test cases for Huawei transport device feature in SNMP command generator"""
import pytest
from flask import Flask
import re

class TestHuaweiTransportFeature:
    """Test cases for Huawei transport device context option"""
    
    def test_oid_calculator_page_has_huawei_checkbox(self, client):
        """Test that OID calculator page contains Huawei transport device checkbox"""
        response = client.get('/oid-calculator')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        
        # Check for Huawei transport device checkbox
        assert 'id="huawei_transport_device"' in response_text
        assert 'type="checkbox"' in response_text
        
        # Check for help text
        assert ('华为传送设备' in response_text or
                'Huawei Transport Device' in response_text or
                'HuaWei Transport Device' in response_text)
        
        # Check for context parameter help text
        assert ('context参数' in response_text or
                'context parameter' in response_text)
    
    def test_oid_calculator_page_has_help_link(self, client):
        """Test that OID calculator page contains command parameter help link"""
        response = client.get('/oid-calculator')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        
        # Check for help link
        assert 'href="https://net-snmp.sourceforge.io/docs/man/snmpcmd.html"' in response_text
        assert 'target="_blank"' in response_text
        
        # Check for help link text
        assert ('命令参数帮助' in response_text or
                'Command Parameter Help' in response_text)
    
    def test_huawei_checkbox_in_snmpv3_section(self, client):
        """Test that Huawei checkbox is properly placed in SNMPv3 section"""
        response = client.get('/oid-calculator')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        
        # Find SNMPv3 options section
        assert 'id="snmpv3_options"' in response_text
        
        # Check that Huawei checkbox is inside SNMPv3 section (appears after SNMPv3 section starts)
        snmpv3_start = response_text.find('id="snmpv3_options"')
        huawei_checkbox = response_text.find('id="huawei_transport_device"')
        assert huawei_checkbox > snmpv3_start
    
    @pytest.mark.parametrize("lang", ["zh", "en"])
    def test_huawei_feature_multilingual(self, client, lang):
        """Test Huawei feature works in both languages"""
        response = client.get(f'/oid-calculator?lang={lang}')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        
        # Check for Huawei checkbox exists in both languages
        assert 'id="huawei_transport_device"' in response_text
        
        # Check that the feature is present (text may be in Chinese or English)
        # For now, we just check that the checkbox exists and has proper structure
        assert 'for="huawei_transport_device"' in response_text
    
    def test_page_structure_integrity(self, client):
        """Test that adding Huawei feature doesn't break page structure"""
        response = client.get('/oid-calculator')
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        
        # Check that all major sections are present
        assert 'class="form-section"' in response_text
        assert 'id="snmpv3_options"' in response_text
        assert 'id="version"' in response_text
        assert 'id="huawei_transport_device"' in response_text
        
        # Check that form elements are properly structured
        assert 'class="form-group"' in response_text
        
        # Check for duplicate IDs using regex
        id_pattern = r'id="([^"]+)"'
        found_ids = re.findall(id_pattern, response_text)
        unique_ids = set(found_ids)
        assert len(found_ids) == len(unique_ids), f"Duplicate IDs found: {[id for id in found_ids if found_ids.count(id) > 1]}"