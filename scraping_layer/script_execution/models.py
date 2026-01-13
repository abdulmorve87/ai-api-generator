"""
Data models for script execution layer.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from ..models import ScrapingStrategy, InteractionStep, PaginationConfig


class ScriptStatus(Enum):
    """Status of script execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


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
    interactions: List[InteractionStep] = field(default_factory=list)
    pagination: Optional[PaginationConfig] = None
    expected_fields: List[str] = field(default_factory=list)
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