"""
Basic setup tests to verify the Universal Scraping Layer foundation.

These tests ensure that the core components can be imported and instantiated
correctly, and that the basic configuration and logging systems work.
"""

import pytest
from unittest.mock import Mock, AsyncMock

from scraping_layer.models import (
    ScriptConfig, ScrapingStrategy, ScrapingResult, WebsiteAnalysis,
    FrameworkType, FrameworkInfo, BrowserRequirements
)
from scraping_layer.config import ScrapingConfig, get_config, set_config
from scraping_layer.utils.logging import get_logger, ScrapingLogger
from scraping_layer.engine import ScrapingEngine


class TestModelsImport:
    """Test that all models can be imported and instantiated."""
    
    def test_script_config_creation(self):
        """Test ScriptConfig can be created with required fields."""
        config = ScriptConfig(
            url="https://example.com",
            script_type=ScrapingStrategy.STATIC,
            selectors={"title": "h1"}
        )
        
        assert config.url == "https://example.com"
        assert config.script_type == ScrapingStrategy.STATIC
        assert config.selectors == {"title": "h1"}
        assert config.cache_ttl == 3600  # Default value
    
    def test_website_analysis_creation(self):
        """Test WebsiteAnalysis can be created."""
        framework_info = FrameworkInfo(
            framework=FrameworkType.REACT,
            version="18.0.0",
            confidence=0.9
        )
        
        analysis = WebsiteAnalysis(
            is_static=False,
            framework=framework_info,
            requires_javascript=True,
            recommended_strategy=ScrapingStrategy.DYNAMIC
        )
        
        assert analysis.is_static is False
        assert analysis.framework.framework == FrameworkType.REACT
        assert analysis.requires_javascript is True
    
    def test_scraping_result_creation(self):
        """Test ScrapingResult can be created."""
        from scraping_layer.models import ScrapingMetadata
        
        result = ScrapingResult(
            success=True,
            data=[{"title": "Test"}],
            metadata=ScrapingMetadata(strategy_used=ScrapingStrategy.STATIC)
        )
        
        assert result.success is True
        assert len(result.data) == 1
        assert result.metadata.strategy_used == ScrapingStrategy.STATIC


class TestConfiguration:
    """Test configuration management."""
    
    def test_default_config_creation(self):
        """Test that default configuration can be created."""
        config = ScrapingConfig()
        
        assert config.security.max_script_execution_time == 300
        assert config.browser.max_concurrent_browsers == 5
        assert config.cache.default_ttl == 3600
        assert config.network.max_retries == 3
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = ScrapingConfig()
        errors = config.validate()
        
        # Default config should be valid
        assert len(errors) == 0
    
    def test_invalid_config_validation(self):
        """Test that invalid configuration is caught."""
        config = ScrapingConfig()
        config.security.max_script_execution_time = -1  # Invalid
        config.browser.max_concurrent_browsers = 0  # Invalid
        
        errors = config.validate()
        
        assert len(errors) >= 2
        assert any("max_script_execution_time" in error for error in errors)
        assert any("max_concurrent_browsers" in error for error in errors)
    
    def test_config_from_dict(self):
        """Test creating configuration from dictionary."""
        config_dict = {
            "security": {"max_script_execution_time": 600},
            "browser": {"max_concurrent_browsers": 10}
        }
        
        config = ScrapingConfig.from_dict(config_dict)
        
        assert config.security.max_script_execution_time == 600
        assert config.browser.max_concurrent_browsers == 10
        # Other values should be defaults
        assert config.cache.default_ttl == 3600


class TestLogging:
    """Test logging functionality."""
    
    def test_logger_creation(self):
        """Test that logger can be created."""
        logger = ScrapingLogger("test_logger")
        
        assert logger.logger.name == "test_logger"
        assert hasattr(logger, 'performance')
        assert hasattr(logger, 'security')
    
    def test_get_logger_singleton(self):
        """Test that get_logger returns the same instance."""
        logger1 = get_logger()
        logger2 = get_logger()
        
        assert logger1 is logger2
    
    def test_performance_logger(self):
        """Test performance logging functionality."""
        logger = ScrapingLogger("test_perf")
        
        # Test that performance logger methods exist and are callable
        assert hasattr(logger.performance, 'time_operation')
        assert hasattr(logger.performance, 'log_metrics')
        
        # Test metrics logging (should not raise exception)
        logger.performance.log_metrics("test_operation", {"duration": 1.5})
    
    def test_security_logger(self):
        """Test security logging functionality."""
        logger = ScrapingLogger("test_security")
        
        # Test that security logger methods exist and are callable
        assert hasattr(logger.security, 'log_security_alert')
        assert hasattr(logger.security, 'log_script_validation')
        
        # Test security alert logging (should not raise exception)
        logger.security.log_security_alert("test_alert", "Test message", detail="test")


class TestEngineSetup:
    """Test that the scraping engine can be set up with mock components."""
    
    def test_engine_creation_with_mocks(self):
        """Test that ScrapingEngine can be created with mock components."""
        # Create mock components
        content_detector = Mock()
        script_executor = Mock()
        static_scraper = Mock()
        dynamic_scraper = Mock()
        browser_manager = Mock()
        data_extractor = Mock()
        cache_manager = Mock()
        error_handler = Mock()
        
        # Create engine
        engine = ScrapingEngine(
            content_detector=content_detector,
            script_executor=script_executor,
            static_scraper=static_scraper,
            dynamic_scraper=dynamic_scraper,
            browser_manager=browser_manager,
            data_extractor=data_extractor,
            cache_manager=cache_manager,
            error_handler=error_handler
        )
        
        assert engine.content_detector is content_detector
        assert engine.script_executor is script_executor
        assert len(engine.get_supported_strategies()) == 3
    
    def test_engine_supported_strategies(self):
        """Test that engine returns correct supported strategies."""
        # Create minimal engine with mocks
        engine = ScrapingEngine(
            content_detector=Mock(),
            script_executor=Mock(),
            static_scraper=Mock(),
            dynamic_scraper=Mock(),
            browser_manager=Mock(),
            data_extractor=Mock(),
            cache_manager=Mock(),
            error_handler=Mock()
        )
        
        strategies = engine.get_supported_strategies()
        
        assert "static" in strategies
        assert "dynamic" in strategies
        assert "hybrid" in strategies


class TestIntegration:
    """Integration tests for the basic setup."""
    
    def test_full_import_chain(self):
        """Test that all components can be imported together."""
        from scraping_layer import ScrapingEngine, ScriptConfig, ScrapingResult
        from scraping_layer.config import get_config
        from scraping_layer.utils.logging import get_logger
        
        # Should not raise any import errors
        config = get_config()
        logger = get_logger()
        
        assert config is not None
        assert logger is not None
    
    def test_config_and_logging_integration(self):
        """Test that configuration affects logging setup."""
        # Create custom config
        config = ScrapingConfig()
        config.logging.log_level = "DEBUG"
        config.logging.enable_performance_logging = True
        
        # Set the config
        set_config(config)
        
        # Get updated config to verify it was set
        updated_config = get_config()
        
        assert updated_config.logging.log_level == "DEBUG"
        assert updated_config.logging.enable_performance_logging is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])