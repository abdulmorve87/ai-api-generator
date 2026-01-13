"""
AI Script Generator

This module demonstrates how the AI layer would populate the GenericScrapingScript
based on user inputs from the form (components/form.py). This serves as a bridge
between user requirements and the technical scraping implementation.

The AI layer would:
1. Analyze user requirements from the form
2. Discover and analyze target websites
3. Generate appropriate selectors and extraction logic
4. Create a complete GenericScrapingScript ready for execution
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse, urljoin

from generic_scraping_script import (
    GenericScrapingScript, FieldDefinition, DataSource, ResponseSchema,
    ScrapingRules, DataType, UpdateFrequency, create_field_from_user_input,
    create_data_source_from_url, map_update_frequency
)
from scraping_layer.models import ScrapingStrategy, InteractionStep, PaginationConfig


class AIScriptGenerator:
    """
    AI-powered script generator that converts user requirements
    into executable scraping scripts.
    """
    
    def __init__(self):
        self.confidence_threshold = 0.7
        self.known_data_sources = {
            "ipo": [
                "chittorgarh.com",
                "investorgain.com", 
                "moneycontrol.com",
                "nseindia.com"
            ],
            "stock": [
                "yahoo.com",
                "google.com/finance",
                "moneycontrol.com"
            ],
            "news": [
                "reuters.com",
                "bloomberg.com",
                "economictimes.com"
            ]
        }
    
    def generate_script_from_form(self, form_data: Dict[str, Any]) -> GenericScrapingScript:
        """
        Main method to generate a scraping script from form data.
        This simulates what the AI layer would do.
        """
        print("🤖 AI Layer: Generating script from form data...")
        
        # Extract and analyze user requirements
        requirements = self._analyze_user_requirements(form_data)
        print(f"📋 Requirements analyzed: {requirements['data_type']}")
        
        # Discover or validate data sources
        data_sources = self._discover_data_sources(
            form_data.get('data_source', ''),
            requirements['data_type']
        )
        print(f"🔍 Data sources found: {[ds.name for ds in data_sources]}")
        
        # Generate field definitions
        fields = self._generate_field_definitions(
            form_data.get('desired_fields', ''),
            requirements
        )
        print(f"📊 Fields generated: {[f.name for f in fields]}")
        
        # Create response schema
        response_schema = self._create_response_schema(
            form_data.get('response_structure', ''),
            fields
        )
        
        # Determine scraping strategy
        strategy = self._determine_scraping_strategy(data_sources[0] if data_sources else None)
        print(f"⚙️ Strategy selected: {strategy.value}")
        
        # Generate scraping rules
        scraping_rules = self._generate_scraping_rules(requirements, fields)
        
        # Create the complete script
        script = GenericScrapingScript(
            script_id=self._generate_script_id(requirements['data_type']),
            name=self._generate_script_name(form_data['data_description']),
            description=form_data['data_description'],
            
            data_sources=data_sources,
            entry_url=data_sources[0].base_url if data_sources else "",
            strategy=strategy,
            fields=fields,
            response_schema=response_schema,
            scraping_rules=scraping_rules,
            
            update_frequency=map_update_frequency(form_data.get('update_frequency', 'daily')),
            confidence_score=self._calculate_confidence_score(data_sources, fields),
            estimated_success_rate=0.85,  # Would be calculated based on website analysis
            
            tags=self._generate_tags(requirements, form_data)
        )
        
        print("✅ Script generation completed!")
        return script
    
    def _analyze_user_requirements(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user's data description to understand what they want.
        In a real AI system, this would use NLP to extract intent.
        """
        description = form_data.get('data_description', '').lower()
        
        # Simple keyword-based analysis (real AI would be more sophisticated)
        data_type = "general"
        domain = "web"
        
        if any(keyword in description for keyword in ['ipo', 'initial public offering', 'grey market']):
            data_type = "ipo"
            domain = "finance"
        elif any(keyword in description for keyword in ['stock', 'share', 'equity']):
            data_type = "stock"
            domain = "finance"
        elif any(keyword in description for keyword in ['news', 'article', 'headline']):
            data_type = "news"
            domain = "media"
        elif any(keyword in description for keyword in ['product', 'price', 'ecommerce']):
            data_type = "product"
            domain = "ecommerce"
        
        return {
            "data_type": data_type,
            "domain": domain,
            "description": description,
            "complexity": "medium"  # Would be determined by AI analysis
        }
    
    def _discover_data_sources(self, user_source: str, data_type: str) -> List[DataSource]:
        """
        Discover or validate data sources based on user input and data type.
        """
        sources = []
        
        if user_source:
            # User provided a specific source
            sources.append(self._analyze_user_provided_source(user_source))
        else:
            # AI discovers sources based on data type
            known_sources = self.known_data_sources.get(data_type, [])
            for source_domain in known_sources[:2]:  # Limit to top 2 sources
                sources.append(DataSource(
                    name=source_domain.split('.')[0].title(),
                    base_url=f"https://{source_domain}",
                    description=f"Known source for {data_type} data",
                    reliability_score=0.8
                ))
        
        return sources
    
    def _analyze_user_provided_source(self, source_url: str) -> DataSource:
        """
        Analyze a user-provided data source URL.
        """
        if not source_url.startswith(('http://', 'https://')):
            source_url = f"https://{source_url}"
        
        parsed = urlparse(source_url)
        domain_name = parsed.netloc.replace('www.', '')
        
        return DataSource(
            name=domain_name.split('.')[0].title(),
            base_url=source_url,
            description=f"User-specified data source: {domain_name}",
            reliability_score=0.7  # Lower confidence for unknown sources
        )
    
    def _generate_field_definitions(
        self, 
        desired_fields: str, 
        requirements: Dict[str, Any]
    ) -> List[FieldDefinition]:
        """
        Generate field definitions based on user input and data type.
        """
        fields = []
        
        if desired_fields:
            # Parse user-specified fields
            field_lines = [line.strip() for line in desired_fields.split('\n') if line.strip()]
            for field_line in field_lines:
                field_name = field_line.lower().replace(' ', '_')
                field_type = self._infer_field_type(field_name, field_line)
                
                fields.append(create_field_from_user_input(
                    field_name=field_name,
                    field_type=field_type,
                    css_selector=self._generate_css_selector(field_name),
                    description=f"User-requested field: {field_line}"
                ))
        else:
            # Generate default fields based on data type
            fields = self._generate_default_fields(requirements['data_type'])
        
        return fields
    
    def _generate_default_fields(self, data_type: str) -> List[FieldDefinition]:
        """
        Generate default field definitions based on data type.
        """
        field_templates = {
            "ipo": [
                ("company_name", "string", "Company name"),
                ("listing_date", "date", "Expected listing date"),
                ("issue_price", "number", "IPO issue price"),
                ("grey_market_premium", "number", "Grey market premium"),
                ("subscription_status", "string", "Subscription status")
            ],
            "stock": [
                ("symbol", "string", "Stock symbol"),
                ("company_name", "string", "Company name"),
                ("current_price", "number", "Current stock price"),
                ("change", "number", "Price change"),
                ("volume", "number", "Trading volume")
            ],
            "news": [
                ("headline", "string", "News headline"),
                ("summary", "string", "Article summary"),
                ("published_date", "date", "Publication date"),
                ("author", "string", "Article author"),
                ("category", "string", "News category")
            ],
            "general": [
                ("title", "string", "Item title"),
                ("description", "string", "Item description"),
                ("url", "url", "Item URL"),
                ("date", "date", "Item date")
            ]
        }
        
        template = field_templates.get(data_type, field_templates["general"])
        fields = []
        
        for field_name, field_type, description in template:
            fields.append(create_field_from_user_input(
                field_name=field_name,
                field_type=field_type,
                css_selector=self._generate_css_selector(field_name),
                description=description
            ))
        
        return fields
    
    def _infer_field_type(self, field_name: str, field_text: str) -> str:
        """
        Infer the data type of a field based on its name and context.
        """
        field_name_lower = field_name.lower()
        field_text_lower = field_text.lower()
        
        # Date fields
        if any(keyword in field_name_lower for keyword in ['date', 'time', 'created', 'updated']):
            return "date"
        
        # Number fields
        if any(keyword in field_name_lower for keyword in ['price', 'amount', 'count', 'number', 'premium', 'volume']):
            return "number"
        
        # URL fields
        if any(keyword in field_name_lower for keyword in ['url', 'link', 'href']):
            return "url"
        
        # Email fields
        if 'email' in field_name_lower:
            return "email"
        
        # Default to string
        return "string"
    
    def _generate_css_selector(self, field_name: str) -> str:
        """
        Generate a CSS selector based on field name.
        In a real AI system, this would analyze the target website.
        """
        # Common selector patterns based on field names
        selector_patterns = {
            "company_name": "td.company-name, .company-name, [data-field='company']",
            "listing_date": "td.listing-date, .date, [data-field='date']",
            "issue_price": "td.price, .price, [data-field='price']",
            "grey_market_premium": "td.gmp, .premium, [data-field='premium']",
            "title": "h1, h2, .title, [data-field='title']",
            "description": ".description, .summary, [data-field='description']",
            "url": "a[href], [data-field='url']",
            "date": ".date, [data-field='date']"
        }
        
        return selector_patterns.get(field_name, f"[data-field='{field_name}'], .{field_name}")
    
    def _create_response_schema(
        self, 
        user_structure: str, 
        fields: List[FieldDefinition]
    ) -> ResponseSchema:
        """
        Create response schema based on user input or default structure.
        """
        if user_structure:
            try:
                # Try to parse user-provided JSON structure
                parsed_structure = json.loads(user_structure)
                return ResponseSchema(
                    root_key="data" if "data" in parsed_structure else None,
                    is_array=isinstance(parsed_structure.get("data", []), list),
                    fields=fields,
                    sample_response=parsed_structure
                )
            except json.JSONDecodeError:
                pass
        
        # Default structure
        return ResponseSchema(
            root_key="data",
            is_array=True,
            fields=fields,
            sample_response={
                "data": [
                    {field.name: f"sample_{field.data_type.value}" for field in fields[:3]}
                ],
                "total": 0,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )
    
    def _determine_scraping_strategy(self, data_source: Optional[DataSource]) -> ScrapingStrategy:
        """
        Determine the best scraping strategy based on data source analysis.
        """
        if not data_source:
            return ScrapingStrategy.STATIC
        
        # Simple heuristics (real AI would analyze the actual website)
        domain = data_source.base_url.lower()
        
        # Known dynamic sites
        if any(keyword in domain for keyword in ['react', 'angular', 'vue', 'spa']):
            return ScrapingStrategy.DYNAMIC
        
        # Financial sites often have dynamic content
        if any(keyword in domain for keyword in ['trading', 'live', 'realtime']):
            return ScrapingStrategy.DYNAMIC
        
        # Default to static with hybrid fallback
        return ScrapingStrategy.HYBRID
    
    def _generate_scraping_rules(
        self, 
        requirements: Dict[str, Any], 
        fields: List[FieldDefinition]
    ) -> ScrapingRules:
        """
        Generate scraping rules based on requirements and field definitions.
        """
        return ScrapingRules(
            content_indicators=[
                "table", ".data-table", ".results", ".content",
                f"[data-type='{requirements['data_type']}']"
            ],
            error_indicators=[
                ".error", ".no-data", ".empty", "[data-error]"
            ],
            min_items_required=1,
            max_items_expected=1000,  # Reasonable default
            required_fields_percentage=0.8,
            custom_transformations=[
                "trim_whitespace",
                "remove_extra_spaces",
                "normalize_currency" if requirements['domain'] == 'finance' else "normalize_text"
            ]
        )
    
    def _calculate_confidence_score(
        self, 
        data_sources: List[DataSource], 
        fields: List[FieldDefinition]
    ) -> float:
        """
        Calculate confidence score for the generated script.
        """
        base_score = 0.5
        
        # Boost confidence for known reliable sources
        if data_sources:
            avg_reliability = sum(ds.reliability_score for ds in data_sources) / len(data_sources)
            base_score += avg_reliability * 0.3
        
        # Boost confidence for well-defined fields
        if fields:
            defined_selectors = sum(1 for f in fields if f.selector)
            selector_ratio = defined_selectors / len(fields)
            base_score += selector_ratio * 0.2
        
        return min(base_score, 1.0)
    
    def _generate_script_id(self, data_type: str) -> str:
        """Generate a unique script ID."""
        import uuid
        short_uuid = str(uuid.uuid4())[:8]
        return f"{data_type}_scraper_{short_uuid}"
    
    def _generate_script_name(self, description: str) -> str:
        """Generate a human-readable script name."""
        # Extract key terms and create a name
        words = description.split()[:5]  # First 5 words
        name = " ".join(words).title()
        return f"{name} Scraper"
    
    def _generate_tags(self, requirements: Dict[str, Any], form_data: Dict[str, Any]) -> List[str]:
        """Generate relevant tags for the script."""
        tags = [
            requirements['data_type'],
            requirements['domain'],
            form_data.get('update_frequency', 'daily').lower()
        ]
        
        # Add domain-specific tags
        if requirements['domain'] == 'finance':
            tags.extend(['financial_data', 'market_data'])
        elif requirements['domain'] == 'media':
            tags.extend(['news', 'content'])
        
        return list(set(tags))  # Remove duplicates


# === EXAMPLE USAGE ===

def demo_ai_script_generation():
    """
    Demonstrate how the AI layer would generate scripts from form data.
    """
    # Simulate form data from components/form.py
    sample_form_data = {
        'data_description': 'Current IPOs listed on Indian stock market with their grey market premium history',
        'data_source': 'chittorgarh.com',
        'desired_fields': 'company_name\nlisting_date\nissue_price\ngrey_market_premium\nsubscription_status',
        'response_structure': '{\n  "data": [\n    {\n      "company_name": "string",\n      "listing_date": "date",\n      "issue_price": "number",\n      "grey_market_premium": "number"\n    }\n  ]\n}',
        'update_frequency': 'Daily'
    }
    
    # Generate script using AI layer
    generator = AIScriptGenerator()
    script = generator.generate_script_from_form(sample_form_data)
    
    # Validate and show results
    print("\n" + "="*50)
    print("GENERATED SCRIPT SUMMARY")
    print("="*50)
    
    summary = script.get_execution_summary()
    for key, value in summary.items():
        print(f"{key:20}: {value}")
    
    # Check validation
    issues = script.validate_completeness()
    if issues:
        print(f"\n⚠️  Validation Issues: {issues}")
    else:
        print("\n✅ Script validation passed!")
    
    # Show field details
    print(f"\n📊 Field Definitions ({len(script.fields)} fields):")
    for field in script.fields:
        print(f"  • {field.name} ({field.data_type.value}): {field.selector}")
    
    return script


if __name__ == "__main__":
    demo_ai_script_generation()