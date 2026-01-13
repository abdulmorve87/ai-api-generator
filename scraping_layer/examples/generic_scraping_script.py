"""
Generic Scraping Script Template

This script serves as a standardized template that will be populated by the AI layer
based on user inputs from the form (components/form.py) and then executed by the
scraping layer to extract meaningful data from the web.

The AI layer will populate this template with:
1. Target URL(s) and data source information
2. CSS/XPath selectors for data extraction
3. Expected data schema and field mappings
4. Interaction steps for dynamic content
5. Pagination and navigation logic
6. Data validation and cleaning rules
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
from enum import Enum

# Import scraping layer models
from scraping_layer.models import (
    ScrapingStrategy, InteractionStep, PaginationConfig, 
    BrowserRequirements, RetryConfig
)


class DataType(Enum):
    """Supported data types for field validation."""
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    URL = "url"
    EMAIL = "email"
    ARRAY = "array"
    OBJECT = "object"


class UpdateFrequency(Enum):
    """Data update frequency options."""
    REAL_TIME = "real-time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class FieldDefinition:
    """Definition of a data field to be extracted."""
    name: str
    data_type: DataType
    selector: str  # CSS selector or XPath
    required: bool = True
    default_value: Any = None
    validation_pattern: Optional[str] = None  # Regex pattern for validation
    transformation: Optional[str] = None  # Data transformation rule
    description: Optional[str] = None


@dataclass
class DataSource:
    """Information about the data source."""
    name: str
    base_url: str
    description: str
    requires_authentication: bool = False
    rate_limit: Optional[int] = None  # Requests per minute
    known_anti_bot_measures: List[str] = field(default_factory=list)
    reliability_score: float = 1.0  # 0.0 to 1.0


@dataclass
class ResponseSchema:
    """Expected structure of the API response."""
    root_key: Optional[str] = None  # e.g., "data", "results"
    is_array: bool = True
    fields: List[FieldDefinition] = field(default_factory=list)
    nested_objects: Dict[str, 'ResponseSchema'] = field(default_factory=dict)
    sample_response: Optional[Dict[str, Any]] = None


@dataclass
class ScrapingRules:
    """Rules for data extraction and processing."""
    # Content detection rules
    content_indicators: List[str] = field(default_factory=list)  # Selectors that indicate content is loaded
    error_indicators: List[str] = field(default_factory=list)   # Selectors that indicate errors
    
    # Data cleaning rules
    remove_html_tags: bool = True
    trim_whitespace: bool = True
    decode_html_entities: bool = True
    normalize_unicode: bool = True
    
    # Validation rules
    min_items_required: int = 1
    max_items_expected: Optional[int] = None
    required_fields_percentage: float = 0.8  # 80% of required fields must be present
    
    # Custom processing rules (will be converted to executable code by AI)
    custom_transformations: List[str] = field(default_factory=list)


@dataclass
class GenericScrapingScript:
    """
    Generic scraping script that will be populated by AI layer
    and executed by the scraping layer.
    """
    
    # === USER REQUIREMENTS (from form.py) ===
    script_id: str
    name: str
    description: str  # User's data description from form
    
    # Data source information
    data_sources: List[DataSource] = field(default_factory=list)
    fallback_sources: List[DataSource] = field(default_factory=list)
    
    # Expected output structure
    response_schema: ResponseSchema = field(default_factory=ResponseSchema)
    update_frequency: UpdateFrequency = UpdateFrequency.DAILY
    
    # === TECHNICAL CONFIGURATION ===
    # Scraping strategy (determined by AI based on website analysis)
    strategy: ScrapingStrategy = ScrapingStrategy.STATIC
    
    # Field definitions for data extraction
    fields: List[FieldDefinition] = field(default_factory=list)
    
    # Navigation and interaction
    entry_url: str = ""
    navigation_steps: List[InteractionStep] = field(default_factory=list)
    pagination_config: Optional[PaginationConfig] = None
    
    # Data processing rules
    scraping_rules: ScrapingRules = field(default_factory=ScrapingRules)
    
    # Browser and execution settings
    browser_requirements: BrowserRequirements = field(default_factory=BrowserRequirements)
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    timeout: int = 30
    cache_ttl: int = 3600  # Cache time-to-live in seconds
    
    # === METADATA ===
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "ai_layer"
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    
    # Quality and reliability metrics
    confidence_score: float = 0.0  # AI's confidence in this script (0.0 to 1.0)
    estimated_success_rate: float = 0.0  # Expected success rate based on website analysis
    
    def to_script_config(self):
        """
        Convert this generic script to ScriptConfig for the scraping engine.
        This method bridges the gap between AI-generated scripts and the scraping layer.
        """
        from scraping_layer.models import ScriptConfig
        
        # Convert field definitions to selectors dictionary
        selectors = {field.name: field.selector for field in self.fields}
        
        # Build output schema for validation
        output_schema = {
            "type": "array" if self.response_schema.is_array else "object",
            "properties": {
                field.name: {
                    "type": field.data_type.value,
                    "required": field.required
                }
                for field in self.fields
            }
        }
        
        return ScriptConfig(
            url=self.entry_url,
            script_type=self.strategy,
            selectors=selectors,
            pagination=self.pagination_config,
            interactions=self.navigation_steps,
            output_schema=output_schema,
            retry_config=self.retry_config,
            cache_ttl=self.cache_ttl,
            timeout=self.timeout,
            browser_requirements=self.browser_requirements
        )
    
    def validate_completeness(self) -> List[str]:
        """
        Validate that the script has all required information.
        Returns list of missing or invalid components.
        """
        issues = []
        
        if not self.entry_url:
            issues.append("Entry URL is required")
        
        if not self.fields:
            issues.append("At least one field definition is required")
        
        if not self.data_sources:
            issues.append("At least one data source must be specified")
        
        # Validate field definitions
        for field in self.fields:
            if not field.selector:
                issues.append(f"Field '{field.name}' missing selector")
        
        # Validate response schema
        if self.response_schema.is_array and not self.response_schema.fields:
            issues.append("Array response schema must define fields")
        
        return issues
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of what this script will do.
        Useful for logging and user feedback.
        """
        return {
            "script_id": self.script_id,
            "name": self.name,
            "strategy": self.strategy.value,
            "target_url": self.entry_url,
            "fields_to_extract": [f.name for f in self.fields],
            "data_sources": [ds.name for ds in self.data_sources],
            "has_pagination": self.pagination_config is not None,
            "has_interactions": len(self.navigation_steps) > 0,
            "update_frequency": self.update_frequency.value,
            "confidence_score": self.confidence_score,
            "estimated_items": self.scraping_rules.max_items_expected
        }


# === HELPER FUNCTIONS FOR AI LAYER ===

def create_field_from_user_input(
    field_name: str, 
    field_type: str = "string",
    css_selector: str = "",
    required: bool = True,
    description: str = ""
) -> FieldDefinition:
    """
    Helper function for AI layer to create field definitions
    from user input and website analysis.
    """
    # Map common field types
    type_mapping = {
        "text": DataType.STRING,
        "string": DataType.STRING,
        "number": DataType.NUMBER,
        "integer": DataType.NUMBER,
        "date": DataType.DATE,
        "datetime": DataType.DATE,
        "url": DataType.URL,
        "link": DataType.URL,
        "email": DataType.EMAIL,
        "boolean": DataType.BOOLEAN,
        "array": DataType.ARRAY,
        "list": DataType.ARRAY
    }
    
    data_type = type_mapping.get(field_type.lower(), DataType.STRING)
    
    return FieldDefinition(
        name=field_name,
        data_type=data_type,
        selector=css_selector,
        required=required,
        description=description
    )


def create_data_source_from_url(
    url: str,
    name: str = "",
    description: str = ""
) -> DataSource:
    """
    Helper function to create data source from URL.
    AI layer can enhance this with website analysis results.
    """
    if not name:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        name = parsed.netloc
    
    return DataSource(
        name=name,
        base_url=url,
        description=description or f"Data source: {name}"
    )


def map_update_frequency(frequency_str: str) -> UpdateFrequency:
    """
    Map user-selected update frequency to enum.
    """
    mapping = {
        "real-time": UpdateFrequency.REAL_TIME,
        "hourly": UpdateFrequency.HOURLY,
        "daily": UpdateFrequency.DAILY,
        "weekly": UpdateFrequency.WEEKLY,
        "monthly": UpdateFrequency.MONTHLY
    }
    return mapping.get(frequency_str.lower(), UpdateFrequency.DAILY)


# === EXAMPLE USAGE FOR AI LAYER ===

def create_example_script() -> GenericScrapingScript:
    """
    Example of how AI layer would create a script based on user input.
    This shows the structure and expected data flow.
    """
    
    # Example: User wants IPO data with GMP information
    script = GenericScrapingScript(
        script_id="ipo_gmp_scraper_001",
        name="IPO Grey Market Premium Scraper",
        description="Extract current IPOs with their grey market premium data",
        
        # Data sources (AI would discover these)
        data_sources=[
            DataSource(
                name="Chittorgarh",
                base_url="https://www.chittorgarh.com",
                description="IPO and GMP data source",
                rate_limit=60  # requests per minute
            )
        ],
        
        # Entry point
        entry_url="https://www.chittorgarh.com/ipo/ipo_grey_market_premium.asp",
        strategy=ScrapingStrategy.STATIC,
        
        # Fields to extract (AI would determine selectors)
        fields=[
            FieldDefinition(
                name="company_name",
                data_type=DataType.STRING,
                selector="td.company-name",
                required=True,
                description="Name of the company going public"
            ),
            FieldDefinition(
                name="listing_date",
                data_type=DataType.DATE,
                selector="td.listing-date",
                required=True,
                description="Expected listing date"
            ),
            FieldDefinition(
                name="issue_price",
                data_type=DataType.NUMBER,
                selector="td.issue-price",
                required=True,
                description="IPO issue price per share"
            ),
            FieldDefinition(
                name="grey_market_premium",
                data_type=DataType.NUMBER,
                selector="td.gmp",
                required=False,
                description="Current grey market premium"
            )
        ],
        
        # Response structure
        response_schema=ResponseSchema(
            is_array=True,
            fields=[],  # Would be populated from fields above
            sample_response={
                "data": [
                    {
                        "company_name": "Example Corp Ltd",
                        "listing_date": "2024-01-15",
                        "issue_price": 100,
                        "grey_market_premium": 25
                    }
                ]
            }
        ),
        
        # Processing rules
        scraping_rules=ScrapingRules(
            content_indicators=["table.ipo-table", ".data-table"],
            error_indicators=[".error-message", ".no-data"],
            min_items_required=1,
            required_fields_percentage=0.8
        ),
        
        # Metadata
        update_frequency=UpdateFrequency.DAILY,
        confidence_score=0.85,
        estimated_success_rate=0.90,
        tags=["ipo", "stock_market", "financial_data"]
    )
    
    return script


if __name__ == "__main__":
    # Example usage
    example_script = create_example_script()
    
    # Validate completeness
    issues = example_script.validate_completeness()
    if issues:
        print("Script validation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Script validation passed!")
    
    # Show execution summary
    summary = example_script.get_execution_summary()
    print("\nExecution Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Convert to ScriptConfig for scraping engine
    script_config = example_script.to_script_config()
    print(f"\nGenerated ScriptConfig for URL: {script_config.url}")
    print(f"Strategy: {script_config.script_type.value}")
    print(f"Selectors: {list(script_config.selectors.keys())}")