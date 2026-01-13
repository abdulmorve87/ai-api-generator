"""
Logging utilities for the Universal Scraping Layer.

This module provides structured logging with performance metrics,
security alerts, and operation tracking.
"""

import logging
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

from ..config import get_config


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra') and record.extra:
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


class PerformanceLogger:
    """Logger for performance metrics and timing."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    @contextmanager
    def time_operation(self, operation_name: str, **context):
        """Context manager to time operations."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            duration = end_time - start_time
            memory_delta = end_memory - start_memory if end_memory and start_memory else 0
            
            self.logger.info(
                f"Operation '{operation_name}' completed",
                extra={
                    'operation': operation_name,
                    'duration_seconds': duration,
                    'memory_delta_mb': memory_delta,
                    'start_memory_mb': start_memory,
                    'end_memory_mb': end_memory,
                    **context
                }
            )
    
    def log_metrics(self, operation: str, metrics: Dict[str, Any]):
        """Log performance metrics for an operation."""
        self.logger.info(
            f"Performance metrics for {operation}",
            extra={
                'operation': operation,
                'metrics': metrics,
                'metric_type': 'performance'
            }
        )
    
    def _get_memory_usage(self) -> Optional[float]:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return None


class SecurityLogger:
    """Logger for security-related events and alerts."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_security_alert(self, alert_type: str, message: str, **details):
        """Log a security alert."""
        self.logger.warning(
            f"SECURITY ALERT: {alert_type} - {message}",
            extra={
                'alert_type': alert_type,
                'security_event': True,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def log_script_validation(self, script_hash: str, is_safe: bool, violations: list):
        """Log script validation results."""
        level = logging.INFO if is_safe else logging.WARNING
        
        self.logger.log(
            level,
            f"Script validation: {'SAFE' if is_safe else 'UNSAFE'}",
            extra={
                'script_hash': script_hash,
                'is_safe': is_safe,
                'violations': violations,
                'validation_type': 'script_security'
            }
        )
    
    def log_sandbox_violation(self, sandbox_id: str, violation_type: str, details: Dict[str, Any]):
        """Log sandbox security violations."""
        self.logger.error(
            f"Sandbox violation in {sandbox_id}: {violation_type}",
            extra={
                'sandbox_id': sandbox_id,
                'violation_type': violation_type,
                'violation_details': details,
                'security_event': True
            }
        )


class ScrapingLogger:
    """Main logger class that combines all logging functionality."""
    
    def __init__(self, name: str = "scraping_layer"):
        self.config = get_config().logging
        self.logger = self._setup_logger(name)
        self.performance = PerformanceLogger(self.logger)
        self.security = SecurityLogger(self.logger)
    
    def _setup_logger(self, name: str) -> logging.Logger:
        """Set up the main logger with appropriate handlers and formatters."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # Use structured formatter if performance logging is enabled
        if self.config.enable_performance_logging:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(self.config.log_format)
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if self.config.log_file:
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(getattr(logging, self.config.log_level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str, **extra):
        """Log info message with optional extra fields."""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **extra):
        """Log warning message with optional extra fields."""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, **extra):
        """Log error message with optional extra fields."""
        self.logger.error(message, extra=extra)
    
    def debug(self, message: str, **extra):
        """Log debug message with optional extra fields."""
        self.logger.debug(message, extra=extra)
    
    def log_operation_start(self, operation: str, **details):
        """Log the start of a scraping operation."""
        self.info(
            f"Starting operation: {operation}",
            operation=operation,
            operation_phase='start',
            **details
        )
    
    def log_operation_end(self, operation: str, success: bool, **details):
        """Log the end of a scraping operation."""
        level = self.info if success else self.error
        status = "SUCCESS" if success else "FAILURE"
        
        level(
            f"Operation {operation} completed: {status}",
            operation=operation,
            operation_phase='end',
            success=success,
            **details
        )
    
    def log_strategy_selection(self, url: str, strategy: str, confidence: float, **analysis):
        """Log strategy selection decision."""
        self.info(
            f"Selected strategy '{strategy}' for {url}",
            url=url,
            strategy=strategy,
            confidence=confidence,
            analysis=analysis,
            decision_type='strategy_selection'
        )
    
    def log_cache_operation(self, operation: str, cache_key: str, hit: bool = None, **details):
        """Log cache operations."""
        self.debug(
            f"Cache {operation}: {cache_key}",
            cache_operation=operation,
            cache_key=cache_key,
            cache_hit=hit,
            **details
        )
    
    def log_browser_operation(self, operation: str, browser_id: str = None, **details):
        """Log browser management operations."""
        self.debug(
            f"Browser {operation}",
            browser_operation=operation,
            browser_id=browser_id,
            **details
        )
    
    def log_data_extraction(self, items_count: int, validation_errors: int = 0, **details):
        """Log data extraction results."""
        self.info(
            f"Extracted {items_count} items",
            items_extracted=items_count,
            validation_errors=validation_errors,
            extraction_type='data_extraction',
            **details
        )


# Global logger instance
_logger: Optional[ScrapingLogger] = None


def get_logger(name: str = "scraping_layer") -> ScrapingLogger:
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        _logger = ScrapingLogger(name)
    return _logger


def setup_logging(config_override: Optional[Dict[str, Any]] = None) -> ScrapingLogger:
    """Set up logging with optional configuration override."""
    global _logger
    
    if config_override:
        # Temporarily override logging config
        original_config = get_config().logging
        for key, value in config_override.items():
            setattr(original_config, key, value)
    
    _logger = ScrapingLogger()
    return _logger