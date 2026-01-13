"""
Core data models for the Universal Scraping Layer.

This module defines all the data structures used throughout the scraping system,
including configuration objects, result formats, and analysis data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Literal, Union
from datetime import datetime
from enum import Enum


class ScrapingStrategy(Enum):
    """Available scraping strategies."""
    STATIC = "static"
    DYNAMIC = "dynamic"
    HYBRID = "hybrid"


class FrameworkType(Enum):
    """Detected JavaScript frameworks."""
    REACT = "react"
    ANGULAR = "angular"
    VUE = "vue"
    JQUERY = "jquery"
    VANILLA_JS = "vanilla_js"
    UNKNOWN = "unknown"


@dataclass
class PaginationConfig:
    """Configuration for handling paginated content."""
    next_selector: str
    max_pages: int = 10
    page_param: Optional[str] = None
    base_url: Optional[str] = None


@dataclass
class InteractionStep:
    """Defines a user interaction step for dynamic scraping."""
    action: Literal["click", "scroll", "type", "wait", "submit"]
    selector: Optional[str] = None
    value: Optional[str] = None
    timeout: int = 5000  # milliseconds


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0


@dataclass
class BrowserRequirements:
    """Requirements for browser instances."""
    headless: bool = True
    user_agent: Optional[str] = None
    viewport_width: int = 1920
    viewport_height: int = 1080
    javascript_enabled: bool = True


@dataclass
class ScriptConfig:
    """Configuration for AI-generated scraping scripts."""
    url: str
    script_type: ScrapingStrategy
    selectors: Dict[str, str]
    pagination: Optional[PaginationConfig] = None
    interactions: List[InteractionStep] = field(default_factory=list)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    cache_ttl: int = 3600  # seconds
    timeout: int = 30  # seconds
    browser_requirements: BrowserRequirements = field(default_factory=BrowserRequirements)


@dataclass
class ScrapingError:
    """Represents an error that occurred during scraping."""
    error_type: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    recoverable: bool = True


@dataclass
class PerformanceMetrics:
    """Performance metrics for scraping operations."""
    start_time: datetime
    end_time: datetime
    total_duration: float  # seconds
    network_time: float = 0.0
    processing_time: float = 0.0
    memory_usage: float = 0.0  # MB
    items_extracted: int = 0
    pages_processed: int = 1


@dataclass
class CacheInfo:
    """Information about cache usage."""
    cache_hit: bool
    cache_key: str
    cached_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    ttl_remaining: Optional[int] = None  # seconds


@dataclass
class ScrapingMetadata:
    """Metadata about the scraping operation."""
    strategy_used: ScrapingStrategy
    framework_detected: Optional[FrameworkType] = None
    user_agent: Optional[str] = None
    final_url: Optional[str] = None  # After redirects
    response_status: Optional[int] = None
    content_type: Optional[str] = None
    page_load_time: Optional[float] = None  # seconds


@dataclass
class ScrapingResult:
    """Standardized result format for all scraping operations."""
    success: bool
    data: List[Dict[str, Any]]
    metadata: ScrapingMetadata
    errors: List[ScrapingError] = field(default_factory=list)
    performance_metrics: Optional[PerformanceMetrics] = None
    cache_info: Optional[CacheInfo] = None


@dataclass
class FrameworkInfo:
    """Information about detected JavaScript frameworks."""
    framework: FrameworkType
    version: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    indicators: List[str] = field(default_factory=list)


@dataclass
class WebsiteAnalysis:
    """Analysis results from content detection."""
    is_static: bool
    framework: Optional[FrameworkInfo] = None
    requires_javascript: bool = False
    has_anti_bot: bool = False
    estimated_load_time: float = 0.0
    recommended_strategy: ScrapingStrategy = ScrapingStrategy.STATIC
    confidence_score: float = 0.0  # 0.0 to 1.0
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    # Additional detection results
    has_authentication: bool = False
    has_rate_limiting: bool = False
    protection_mechanisms: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of script validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)


@dataclass
class ExecutionContext:
    """Context for script execution."""
    script_config: ScriptConfig
    sandbox_id: str
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    allowed_domains: List[str] = field(default_factory=list)
    temp_directory: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result of script execution."""
    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    execution_time: float = 0.0  # seconds
    memory_used: float = 0.0  # MB
    errors: List[ScrapingError] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)


@dataclass
class SecurityValidation:
    """Security validation result for scripts."""
    is_safe: bool
    risk_level: Literal["low", "medium", "high", "critical"] = "low"
    violations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class SandboxEnvironment:
    """Sandbox environment configuration."""
    sandbox_id: str
    process_id: Optional[int] = None
    temp_directory: str = ""
    allowed_domains: List[str] = field(default_factory=list)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


# Configuration classes for different scraping types
@dataclass
class StaticScrapingConfig:
    """Configuration specific to static scraping."""
    url: str
    selectors: Dict[str, str]
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    follow_redirects: bool = True
    pagination: Optional[PaginationConfig] = None


@dataclass
class DynamicScrapingConfig:
    """Configuration specific to dynamic scraping."""
    url: str
    selectors: Dict[str, str]
    interactions: List[InteractionStep] = field(default_factory=list)
    wait_for_selector: Optional[str] = None
    wait_timeout: int = 30000  # milliseconds
    browser_requirements: BrowserRequirements = field(default_factory=BrowserRequirements)
    custom_js: Optional[str] = None