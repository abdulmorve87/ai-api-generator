"""
Script Sandbox - Provides isolated execution environment for scraper scripts.

This module implements a sandboxed execution environment that restricts
access to dangerous operations while allowing necessary scraping functionality.
"""

import ast
import builtins
import logging
import re
from typing import Dict, Any, List, Set, Callable

from .models import ExecutionConfig
from .exceptions import SecurityError, ScriptSyntaxError


class ScriptSandbox:
    """Sandboxed execution environment for scraper scripts."""
    
    # Built-in functions that are forbidden
    FORBIDDEN_BUILTINS: Set[str] = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'input', 'breakpoint', 'globals', 'locals',
        'vars', 'dir', 'getattr', 'setattr', 'delattr',
        'memoryview', 'bytearray'
    }
    
    # Modules that are forbidden to import
    FORBIDDEN_MODULES: Set[str] = {
        'os', 'sys', 'subprocess', 'shutil', 'socket',
        'pickle', 'marshal', 'ctypes', 'multiprocessing',
        'threading', 'asyncio', 'signal', 'pty', 'tty',
        'fcntl', 'termios', 'resource', 'syslog',
        'importlib', 'builtins', '__builtins__'
    }
    
    # Allowed modules for scraping
    ALLOWED_MODULES: Set[str] = {
        'requests', 'bs4', 'BeautifulSoup', 're', 'json',
        'datetime', 'typing', 'urllib', 'html', 'collections',
        'math', 'string', 'itertools', 'functools'
    }
    
    def __init__(self, config: ExecutionConfig = None, logger: logging.Logger = None):
        """
        Initialize the sandbox.
        
        Args:
            config: Execution configuration
            logger: Optional logger instance
        """
        self.config = config or ExecutionConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # Update allowed modules from config
        if self.config.allowed_imports:
            self.ALLOWED_MODULES = set(self.config.allowed_imports)
    
    def execute(
        self,
        script_code: str,
        entry_function: str,
        args: tuple = (),
        kwargs: dict = None
    ) -> Any:
        """
        Execute script code in sandboxed environment.
        
        Args:
            script_code: Python code to execute
            entry_function: Name of function to call (e.g., 'scrape_data')
            args: Positional arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
            
        Returns:
            Return value from the entry function
            
        Raises:
            SecurityError: If script attempts forbidden operations
            ScriptSyntaxError: If script has syntax errors
        """
        kwargs = kwargs or {}
        
        # Step 1: Validate syntax
        self._validate_syntax(script_code)
        
        # Step 2: Check for forbidden imports
        forbidden = self._validate_imports(script_code)
        if forbidden:
            raise SecurityError(
                f"Script contains forbidden imports: {', '.join(forbidden)}",
                forbidden_operation=f"import {forbidden[0]}"
            )
        
        # Step 3: Check for forbidden operations in AST
        self._validate_ast(script_code)
        
        # Step 4: Create safe execution environment
        # CRITICAL: Use the same dict for both globals and locals!
        # When exec() uses separate dicts, top-level defs go into locals,
        # but when functions run, they only see globals - not the outer locals.
        # This causes "name 'detect_scraping_strategy' is not defined" errors
        # because helper functions defined at module level aren't visible
        # to other functions when they execute.
        safe_globals = self._create_safe_globals()
        
        # Step 5: Execute the script to define functions
        # Using safe_globals for BOTH globals and locals ensures all
        # top-level definitions are in the same namespace
        try:
            exec(script_code, safe_globals, safe_globals)
        except Exception as e:
            raise SecurityError(
                f"Script execution failed during definition: {str(e)}",
                forbidden_operation="script_definition"
            )
        
        # Step 6: Find and call the entry function
        if entry_function not in safe_globals:
            raise SecurityError(
                f"Entry function '{entry_function}' not found in script",
                forbidden_operation="missing_function"
            )
        func = safe_globals[entry_function]
        
        if not callable(func):
            raise SecurityError(
                f"'{entry_function}' is not callable",
                forbidden_operation="non_callable"
            )
        
        # Step 7: Call the function
        return func(*args, **kwargs)
    
    def _validate_syntax(self, script_code: str) -> None:
        """
        Validate Python syntax.
        
        Args:
            script_code: Python code to validate
            
        Raises:
            ScriptSyntaxError: If syntax is invalid
        """
        try:
            ast.parse(script_code)
        except SyntaxError as e:
            raise ScriptSyntaxError(
                message=str(e.msg) if e.msg else "Syntax error",
                line_number=e.lineno,
                offset=e.offset,
                text=e.text
            )
    
    def _validate_imports(self, script_code: str) -> List[str]:
        """
        Check script imports against allowed/forbidden lists.
        
        Args:
            script_code: Python code to check
            
        Returns:
            List of forbidden module names found
        """
        forbidden_found = []
        
        try:
            tree = ast.parse(script_code)
        except SyntaxError:
            return forbidden_found  # Syntax errors handled elsewhere
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name in self.FORBIDDEN_MODULES:
                        forbidden_found.append(module_name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    if module_name in self.FORBIDDEN_MODULES:
                        forbidden_found.append(module_name)
        
        return forbidden_found
    
    def _validate_ast(self, script_code: str) -> None:
        """
        Validate AST for forbidden operations.
        
        Args:
            script_code: Python code to validate
            
        Raises:
            SecurityError: If forbidden operations are found
        """
        try:
            tree = ast.parse(script_code)
        except SyntaxError:
            return  # Syntax errors handled elsewhere
        
        for node in ast.walk(tree):
            # Check for calls to forbidden builtins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_BUILTINS:
                        raise SecurityError(
                            f"Forbidden builtin function: {node.func.id}",
                            forbidden_operation=node.func.id
                        )
                
                # Check for __import__ calls
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == '__import__':
                        raise SecurityError(
                            "Dynamic imports are forbidden",
                            forbidden_operation='__import__'
                        )
            
            # Check for attribute access to forbidden names
            if isinstance(node, ast.Attribute):
                if node.attr in ('__class__', '__bases__', '__subclasses__', '__mro__'):
                    raise SecurityError(
                        f"Access to '{node.attr}' is forbidden",
                        forbidden_operation=node.attr
                    )
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """
        Create restricted globals dict for script execution.
        
        Returns:
            Dictionary of safe global variables and functions
        """
        # Start with safe builtins
        safe_builtins = {}
        for name in dir(builtins):
            if name not in self.FORBIDDEN_BUILTINS and not name.startswith('_'):
                safe_builtins[name] = getattr(builtins, name)
        
        # Create safe globals
        safe_globals = {
            '__builtins__': safe_builtins,
            '__name__': '__sandbox__',
            '__doc__': None,
        }
        
        # Add allowed imports
        self._add_allowed_imports(safe_globals)
        
        return safe_globals
    
    def _add_allowed_imports(self, globals_dict: Dict[str, Any]) -> None:
        """
        Add allowed module imports to globals.
        
        Args:
            globals_dict: Dictionary to add imports to
        """
        import requests
        from bs4 import BeautifulSoup
        import re as re_module
        import json as json_module
        import datetime as datetime_module
        from datetime import datetime, timedelta
        from typing import Dict, List, Any, Optional, Tuple
        import html as html_module
        from collections import defaultdict, Counter
        from urllib.parse import urljoin, urlparse
        
        # Add modules
        globals_dict['requests'] = requests
        globals_dict['BeautifulSoup'] = BeautifulSoup
        globals_dict['bs4'] = __import__('bs4')
        globals_dict['re'] = re_module
        globals_dict['json'] = json_module
        globals_dict['datetime'] = datetime_module  # The module
        globals_dict['timedelta'] = timedelta
        globals_dict['html'] = html_module
        globals_dict['collections'] = __import__('collections')
        globals_dict['urllib'] = __import__('urllib')
        globals_dict['typing'] = __import__('typing')
        
        # Add commonly used classes/functions directly
        globals_dict['Dict'] = Dict
        globals_dict['List'] = List
        globals_dict['Any'] = Any
        globals_dict['Optional'] = Optional
        globals_dict['Tuple'] = Tuple
        globals_dict['defaultdict'] = defaultdict
        globals_dict['Counter'] = Counter
        globals_dict['urljoin'] = urljoin
        globals_dict['urlparse'] = urlparse
        
        # Add a safe __import__ that only allows whitelisted modules
        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            """Safe import that only allows whitelisted modules."""
            base_module = name.split('.')[0]
            if base_module in self.ALLOWED_MODULES or base_module in {
                'datetime', 'typing', 'collections', 'urllib', 'html',
                'math', 'string', 'itertools', 'functools', 're', 'json'
            }:
                return __import__(name, globals, locals, fromlist, level)
            raise ImportError(f"Import of '{name}' is not allowed")
        
        # Replace __import__ in builtins with safe version
        safe_builtins = globals_dict.get('__builtins__', {})
        if isinstance(safe_builtins, dict):
            safe_builtins['__import__'] = safe_import
        globals_dict['__builtins__'] = safe_builtins
    
    def is_safe_script(self, script_code: str) -> tuple:
        """
        Check if a script is safe to execute.
        
        Args:
            script_code: Python code to check
            
        Returns:
            Tuple of (is_safe: bool, errors: List[str])
        """
        errors = []
        
        # Check syntax
        try:
            self._validate_syntax(script_code)
        except ScriptSyntaxError as e:
            errors.append(f"Syntax error: {str(e)}")
        
        # Check imports
        forbidden = self._validate_imports(script_code)
        if forbidden:
            errors.append(f"Forbidden imports: {', '.join(forbidden)}")
        
        # Check AST
        try:
            self._validate_ast(script_code)
        except SecurityError as e:
            errors.append(f"Security violation: {str(e)}")
        
        return (len(errors) == 0, errors)
