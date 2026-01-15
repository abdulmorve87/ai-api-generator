"""
Simple test to verify script generation components work together.

This is a basic integration test that doesn't require API calls.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_layer.script_models import (
    ScriptMetadata,
    ScriptValidationResult,
    GeneratedScript,
    ScriptValidationError
)
from ai_layer.script_prompt_builders.script_validator import ScriptValidator
from ai_layer.script_prompt_builders.script_prompt_builder import ScriptPromptBuilder
from scraping_layer.config import ScrapingConfig
from datetime import datetime


def test_script_models():
    """Test script models can be instantiated."""
    print("Testing script models...")
    
    metadata = ScriptMetadata(
        timestamp=datetime.utcnow(),
        model="test-model",
        tokens_used=100,
        generation_time_ms=1000,
        target_url="https://example.com",
        required_fields=["field1", "field2"]
    )
    
    validation_result = ScriptValidationResult(
        is_valid=True,
        syntax_valid=True,
        imports_valid=True,
        no_forbidden_ops=True,
        function_signature_valid=True
    )
    
    script = GeneratedScript(
        script_code="print('hello')",
        metadata=metadata,
        validation_result=validation_result,
        raw_output="print('hello')"
    )
    
    assert script.is_valid == True
    print("✓ Script models work correctly")


def test_script_validator():
    """Test script validator with valid and invalid scripts."""
    print("\nTesting script validator...")
    
    validator = ScriptValidator()
    
    # Test valid script
    valid_script = """
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any

def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]:
    return {'data': [], 'metadata': {}}
"""
    
    result = validator.validate_script(valid_script)
    assert result.is_valid == True
    assert result.syntax_valid == True
    assert result.imports_valid == True
    assert result.no_forbidden_ops == True
    assert result.function_signature_valid == True
    print("✓ Valid script passes validation")
    
    # Test script with syntax error
    invalid_syntax = "def broken("
    result = validator.validate_script(invalid_syntax)
    assert result.is_valid == False
    assert result.syntax_valid == False
    print("✓ Syntax errors detected")
    
    # Test script with missing imports
    missing_imports = """
def scrape_data(url: str):
    return {}
"""
    result = validator.validate_script(missing_imports)
    assert result.is_valid == False
    assert result.imports_valid == False
    print("✓ Missing imports detected")
    
    # Test script with forbidden operations
    forbidden_script = """
import requests
from bs4 import BeautifulSoup

def scrape_data(url: str):
    eval("malicious code")
    return {}
"""
    result = validator.validate_script(forbidden_script)
    assert result.is_valid == False
    assert result.no_forbidden_ops == False
    print("✓ Forbidden operations detected")
    
    # Test script with wrong function signature
    wrong_signature = """
import requests
from bs4 import BeautifulSoup

def wrong_name():
    return {}
"""
    result = validator.validate_script(wrong_signature)
    assert result.is_valid == False
    assert result.function_signature_valid == False
    print("✓ Wrong function signature detected")


def test_script_prompt_builder():
    """Test script prompt builder."""
    print("\nTesting script prompt builder...")
    
    scraping_config = ScrapingConfig.from_env()
    builder = ScriptPromptBuilder(scraping_config)
    
    form_input = {
        'data_description': 'Test data',
        'data_source': 'https://example.com',
        'desired_fields': 'field1\nfield2',
        'response_structure': '',
        'update_frequency': 'Daily'
    }
    
    messages = builder.build_script_prompt(form_input)
    
    assert len(messages) == 2
    assert messages[0]['role'] == 'system'
    assert messages[1]['role'] == 'user'
    assert 'https://example.com' in messages[1]['content']
    assert 'Test data' in messages[1]['content']
    print("✓ Prompt builder works correctly")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Script Generation Component Tests")
    print("=" * 60)
    
    try:
        test_script_models()
        test_script_validator()
        test_script_prompt_builder()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
