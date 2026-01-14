"""
Script Validator - Validates generated scraper scripts for safety and correctness.

This module provides validation for AI-generated Python scripts to ensure they:
- Have valid syntax
- Include required imports
- Don't contain forbidden operations
- Have the correct function signature
"""

import ast
import re
from typing import Tuple, List, Optional
import logging

from ai_layer.script_models import ScriptValidationResult, ScriptValidationError


class ScriptValidator:
    """Validates generated scraper scripts for safety and correctness."""
    
    # Required imports for scraper scripts
    REQUIRED_IMPORTS = ['bs4', 'requests']
    
    # Forbidden operations for security
    FORBIDDEN_OPERATIONS = [
        'exec', 'eval', 'os.system', 'subprocess',
        '__import__', 'compile', 'open'
    ]
    
    # Expected main function name
    EXPECTED_FUNCTION_NAME = 'scrape_data'
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the script validator.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_script(self, script_code: str) -> ScriptValidationResult:
        """
        Validate a generated script for safety and correctness.
        
        Performs the following checks:
        1. Syntax correctness (compile check)
        2. Required imports present
        3. No forbidden operations
        4. Main function exists with correct signature
        
        Args:
            script_code: Python script code to validate
            
        Returns:
            ScriptValidationResult with validation status and details
        """
        result = ScriptValidationResult(
            is_valid=True,
            syntax_valid=False,
            imports_valid=False,
            no_forbidden_ops=False,
            function_signature_valid=False
        )
        
        # Check 1: Syntax validation
        syntax_valid, syntax_error = self.check_syntax(script_code)
        result.syntax_valid = syntax_valid
        if not syntax_valid:
            result.add_error(f"Syntax error: {syntax_error}")
            # If syntax is invalid, can't perform other checks
            return result
        
        # Check 2: Required imports
        imports_valid, missing_imports = self.check_imports(script_code)
        result.imports_valid = imports_valid
        if not imports_valid:
            result.add_error(f"Missing required imports: {', '.join(missing_imports)}")
        
        # Check 3: Forbidden operations
        no_forbidden, forbidden_found = self.check_forbidden_operations(script_code)
        result.no_forbidden_ops = no_forbidden
        if not no_forbidden:
            result.add_error(f"Forbidden operations detected: {', '.join(forbidden_found)}")
        
        # Check 4: Function signature
        signature_valid, signature_error = self.check_function_signature(script_code)
        result.function_signature_valid = signature_valid
        if not signature_valid:
            result.add_error(f"Function signature error: {signature_error}")
        
        # Overall validation status
        result.is_valid = all([
            result.syntax_valid,
            result.imports_valid,
            result.no_forbidden_ops,
            result.function_signature_valid
        ])
        
        if result.is_valid:
            self.logger.info("Script validation passed")
        else:
            self.logger.warning(f"Script validation failed: {result.errors}")
        
        return result
    
    def check_syntax(self, script_code: str) -> Tuple[bool, Optional[str]]:
        """
        Check if script has valid Python syntax.
        
        Args:
            script_code: Python script code to check
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            compile(script_code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            error_msg = f"Line {e.lineno}: {e.msg}"
            self.logger.debug(f"Syntax error detected: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Compilation error: {str(e)}"
            self.logger.debug(f"Compilation error: {error_msg}")
            return False, error_msg
    
    def check_imports(self, script_code: str) -> Tuple[bool, List[str]]:
        """
        Check if required imports are present in the script.
        
        Args:
            script_code: Python script code to check
            
        Returns:
            Tuple of (all_present, missing_imports)
        """
        missing_imports = []
        
        for required_import in self.REQUIRED_IMPORTS:
            # Check for various import patterns
            patterns = [
                f"import {required_import}",
                f"from {required_import} import"
            ]
            
            found = any(pattern in script_code for pattern in patterns)
            
            if not found:
                missing_imports.append(required_import)
                self.logger.debug(f"Missing required import: {required_import}")
        
        return len(missing_imports) == 0, missing_imports
    
    def check_forbidden_operations(self, script_code: str) -> Tuple[bool, List[str]]:
        """
        Check for dangerous operations in the script.
        
        Args:
            script_code: Python script code to check
            
        Returns:
            Tuple of (no_forbidden_ops, forbidden_operations_found)
        """
        forbidden_found = []
        
        for forbidden_op in self.FORBIDDEN_OPERATIONS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + re.escape(forbidden_op) + r'\b'
            
            if re.search(pattern, script_code):
                forbidden_found.append(forbidden_op)
                self.logger.warning(f"Forbidden operation detected: {forbidden_op}")
        
        return len(forbidden_found) == 0, forbidden_found
    
    def check_function_signature(self, script_code: str) -> Tuple[bool, Optional[str]]:
        """
        Check if main scraping function exists with correct signature.
        
        Expected signature: def scrape_data(url: str, timeout: int = 30) -> Dict[str, Any]
        
        Args:
            script_code: Python script code to check
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Parse the script into an AST
            tree = ast.parse(script_code)
            
            # Find function definitions
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            # Look for the expected function
            target_function = None
            for func in functions:
                if func.name == self.EXPECTED_FUNCTION_NAME:
                    target_function = func
                    break
            
            if not target_function:
                return False, f"Function '{self.EXPECTED_FUNCTION_NAME}' not found"
            
            # Check function has at least one parameter (url)
            if len(target_function.args.args) < 1:
                return False, f"Function '{self.EXPECTED_FUNCTION_NAME}' must accept at least 'url' parameter"
            
            # Check first parameter is named 'url'
            first_param = target_function.args.args[0].arg
            if first_param != 'url':
                return False, f"First parameter should be 'url', found '{first_param}'"
            
            self.logger.debug(f"Function signature valid: {self.EXPECTED_FUNCTION_NAME}")
            return True, None
            
        except SyntaxError as e:
            return False, f"Cannot parse script: {str(e)}"
        except Exception as e:
            return False, f"Error checking function signature: {str(e)}"
    
    def validate_or_raise(self, script_code: str) -> ScriptValidationResult:
        """
        Validate script and raise exception if validation fails.
        
        Args:
            script_code: Python script code to validate
            
        Returns:
            ScriptValidationResult if validation passes
            
        Raises:
            ScriptValidationError: If validation fails
        """
        result = self.validate_script(script_code)
        
        if not result.is_valid:
            error_msg = "Script validation failed:\n" + "\n".join(result.errors)
            raise ScriptValidationError(error_msg, result)
        
        return result
