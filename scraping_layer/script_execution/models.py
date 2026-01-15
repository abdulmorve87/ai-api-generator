"""
Data models for script execution layer (Phase 1: Static Scraping).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime

from ..models import ScrapingStrategy


@dataclass
class ScrapingScript:
    """A pre-written scraping script configuration."""
    script_id: str
    name: str
    description: str
    url: str
    strategy: ScrapingStrategy
    selectors: Dict[str, str]
    
    # Optional configurations
    timeout: int = 30
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "user"
    tags: List[str] = field(default_factory=list)


@dataclass
class ScriptMetadata:
    """Metadata about script execution."""
    script_id: str
    execution_id: str
    strategy_used: ScrapingStrategy
    url_processed: str
    items_found: int
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScriptResult:
    """Result of script execution."""
    success: bool
    script_id: str
    execution_id: str
    data: List[Dict[str, Any]]
    metadata: ScriptMetadata
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Performance info
    total_items: int = 0
    execution_time: float = 0.0
    memory_used: float = 0.0