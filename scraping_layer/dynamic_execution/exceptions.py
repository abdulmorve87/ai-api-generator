"""
Exception classes for the Dynamic Execution module.

This module defines custom exceptions for various error conditions
that can occur during script execution.
"""

from typing import Dict, Any, List, Optional


class ScriptExecutionError(Exception):
    """Base exception for script execution errors."""
    
    def __init__(
        self,
        message: str,
        error_type: str = 'execution',
        details: Dict[str, Any] = None
    ):
        """
        Initialize script execution error.
        
        Args:
            message: Error message
            error_type: Type of error (execution, security, timeout, syntax, runtime)
            details: Optional dictionary with error details
        """
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            'error_type': self.error_type,
            'message': str(self),
            'details': self.details
        }


class SecurityError(ScriptExecutionError):
    """Raised when script attempts forbidden operations."""
    
    def __init__(self, message: str, forbidden_operation: str):
        """
        Initialize security error.
        
        Args:
            message: Error message
            forbidden_operation: The operation that was blocked
        """
        super().__init__(
            message,
            error_type='security',
            details={'forbidden_operation': forbidden_operation}
        )
        self.forbidden_operation = forbidden_operation


class ScriptTimeoutError(ScriptExecutionError):
    """Raised when script execution exceeds timeout."""
    
    def __init__(
        self,
        timeout_seconds: int,
        partial_results: List[Dict] = None
    ):
        """
        Initialize timeout error.
        
        Args:
            timeout_seconds: The timeout duration that was exceeded
            partial_results: Any partial results collected before timeout
        """
        super().__init__(
            f"Script execution timed out after {timeout_seconds} seconds",
            error_type='timeout',
            details={
                'timeout_seconds': timeout_seconds,
                'has_partial_results': partial_results is not None and len(partial_results) > 0
            }
        )
        self.timeout_seconds = timeout_seconds
        self.partial_results = partial_results or []


class ScriptSyntaxError(ScriptExecutionError):
    """Raised when script has syntax errors."""
    
    def __init__(
        self,
        message: str,
        line_number: int = None,
        offset: int = None,
        text: str = None
    ):
        """
        Initialize syntax error.
        
        Args:
            message: Error message
            line_number: Line number where error occurred
            offset: Character offset in the line
            text: The problematic text/line
        """
        super().__init__(
            message,
            error_type='syntax',
            details={
                'line_number': line_number,
                'offset': offset,
                'text': text
            }
        )
        self.line_number = line_number
        self.offset = offset
        self.text = text


class ScriptRuntimeError(ScriptExecutionError):
    """Raised when script has runtime errors during execution."""
    
    def __init__(
        self,
        message: str,
        exception_type: str = None,
        traceback_str: str = None,
        line_number: int = None
    ):
        """
        Initialize runtime error.
        
        Args:
            message: Error message
            exception_type: Type of the original exception
            traceback_str: Full traceback as string
            line_number: Line number where error occurred (if available)
        """
        super().__init__(
            message,
            error_type='runtime',
            details={
                'exception_type': exception_type,
                'traceback': traceback_str,
                'line_number': line_number
            }
        )
        self.exception_type = exception_type
        self.traceback_str = traceback_str
        self.line_number = line_number


class NetworkError(ScriptExecutionError):
    """Raised when network requests fail during script execution."""
    
    def __init__(
        self,
        message: str,
        url: str = None,
        status_code: int = None,
        response_text: str = None
    ):
        """
        Initialize network error.
        
        Args:
            message: Error message
            url: The URL that failed
            status_code: HTTP status code (if available)
            response_text: Response body (if available)
        """
        super().__init__(
            message,
            error_type='network',
            details={
                'url': url,
                'status_code': status_code,
                'response_text': response_text[:500] if response_text else None
            }
        )
        self.url = url
        self.status_code = status_code
        self.response_text = response_text


class ParseError(ScriptExecutionError):
    """Raised when HTML parsing fails during script execution."""
    
    def __init__(
        self,
        message: str,
        selector: str = None,
        html_snippet: str = None
    ):
        """
        Initialize parse error.
        
        Args:
            message: Error message
            selector: The CSS selector that failed
            html_snippet: Snippet of HTML being parsed
        """
        super().__init__(
            message,
            error_type='parse',
            details={
                'selector': selector,
                'html_snippet': html_snippet[:200] if html_snippet else None
            }
        )
        self.selector = selector
        self.html_snippet = html_snippet
