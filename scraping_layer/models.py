"""
Core data models for the Universal Scraping Layer (Phase 1: Static Scraping).

This module defines the minimal data structures needed for static HTML scraping.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class ScrapingStrategy(Enum):
    """Available scraping strategies."""
    STATIC = "static"
    DYNAMIC = "dynamic"  # For future use
    HYBRID = "hybrid"    # For future use


@dataclass
class ScriptConfig:
    """Configuration for scraping operations."""
    url: str
    selectors: Dict[str, str]  # field_name -> CSS selector
    timeout: int = 30  # seconds
    script_type: ScrapingStrategy = ScrapingStrategy.STATIC


@dataclass
class StaticScrapingConfig:
    """Configuration specific to static scraping."""
    url: str
    selectors: Dict[str, str]
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=dict)


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
    items_extracted: int = 0


@dataclass
class ScrapingMetadata:
    """Metadata about the scraping operation."""
    strategy_used: ScrapingStrategy
    final_url: Optional[str] = None
    response_status: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScrapingResult:
    """Standardized result format for scraping operations."""
    success: bool
    data: List[Dict[str, Any]]
    metadata: ScrapingMetadata
    errors: List[ScrapingError] = field(default_factory=list)
    performance_metrics: Optional[PerformanceMetrics] = None


# Keep these for backward compatibility with script_execution layer
@dataclass
class PaginationConfig:
    """Configuration for handling paginated content (future use)."""
    next_selector: str
    max_pages: int = 10


@dataclass
class InteractionStep:
    """Defines a user interaction step (future use)."""
    action: str
    selector: Optional[str] = None
    value: Optional[str] = None


@dataclass
class BrowserRequirements:
    """Requirements for browser instances (future use)."""
    headless: bool = True
    javascript_enabled: bool = True
