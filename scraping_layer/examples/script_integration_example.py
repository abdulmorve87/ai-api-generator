"""
Script Integration Example

This file demonstrates the complete flow from user form input to scraping execution:
1. User fills form (components/form.py)
2. AI layer generates generic script (ai_script_generator.py)
3. Script is converted to ScriptConfig for scraping layer
4. Scraping engine executes the script

This serves as the entry point that the future scraping layer will use.
"""

import asyncio
from typing import Dict, Any

# Import our components
from ai_script_generator import AIScriptGenerator
from generic_scraping_script import GenericScrapingScript

# Import scraping layer (when available)
try:
    from scraping_layer.engine import ScrapingEngine
    from scraping_layer.models import ScriptConfig
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("⚠️  Scraping layer not fully available - running in demo mode")


class ScriptExecutionPipeline:
    """
    Main pipeline that orchestrates the entire process from form input to data extraction.
    This is the entry point that will be called by the future API layer.
    """
    
    def __init__(self):
        self.ai_generator = AIScriptGenerator()
        self.scraping_engine = None  # Will be initialized when scraping layer is ready
    
    async def execute_from_form_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method that takes form data and returns scraped results.
        
        Args:
            form_data: Dictionary containing user inputs from components/form.py
            
        Returns:
            Dictionary containing scraped data and metadata
        """
        try:
            print("🚀 Starting script execution pipeline...")
            
            # Step 1: Generate script from form data using AI layer
            print("\n📝 Step 1: Generating script from form data")
            generic_script = self.ai_generator.generate_script_from_form(form_data)
            
            # Validate the generated script
            validation_issues = generic_script.validate_completeness()
            if validation_issues:
                return {
                    "success": False,
                    "error": "Script validation failed",
                    "issues": validation_issues
                }
            
            print(f"✅ Generated script: {generic_script.name}")
            
            # Step 2: Convert to ScriptConfig for scraping layer
            print("\n⚙️  Step 2: Converting to scraping layer format")
            script_config = generic_script.to_script_config()
            
            # Step 3: Execute scraping (mock for now, real implementation later)
            print("\n🔍 Step 3: Executing scraping operation")
            if SCRAPING_AVAILABLE and self.scraping_engine:
                # Real scraping execution
                result = await self.scraping_engine.scrape(script_config)
                scraped_data = result.data
                success = result.success
                errors = [error.message for error in result.errors]
            else:
                # Mock execution for demonstration
                scraped_data, success, errors = await self._mock_scraping_execution(
                    generic_script, script_config
                )
            
            # Step 4: Format response
            print(f"\n📊 Step 4: Formatting response ({len(scraped_data)} items)")
            response = self._format_response(
                generic_script, scraped_data, success, errors
            )
            
            print("✅ Pipeline execution completed!")
            return response
            
        except Exception as e:
            print(f"❌ Pipeline execution failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
    
    async def _mock_scraping_execution(
        self, 
        generic_script: GenericScrapingScript, 
        script_config: ScriptConfig
    ) -> tuple:
        """
        Mock scraping execution for demonstration purposes.
        This will be replaced with real scraping engine calls.
        """
        print("🎭 Running mock scraping (real implementation pending)")
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Generate mock data based on field definitions
        mock_data = []
        for i in range(3):  # Generate 3 sample items
            item = {}
            for field in generic_script.fields:
                if field.data_type.value == "string":
                    item[field.name] = f"Sample {field.name.replace('_', ' ').title()} {i+1}"
                elif field.data_type.value == "number":
                    item[field.name] = (i + 1) * 100
                elif field.data_type.value == "date":
                    item[field.name] = f"2024-01-{15 + i:02d}"
                elif field.data_type.value == "url":
                    item[field.name] = f"https://example.com/item/{i+1}"
                else:
                    item[field.name] = f"sample_value_{i+1}"
            
            mock_data.append(item)
        
        return mock_data, True, []
    
    def _format_response(
        self, 
        script: GenericScrapingScript, 
        data: list, 
        success: bool, 
        errors: list
    ) -> Dict[str, Any]:
        """
        Format the final response according to user's expected structure.
        """
        # Use the response schema from the script
        if script.response_schema.root_key:
            formatted_data = {
                script.response_schema.root_key: data,
                "total": len(data),
                "timestamp": "2024-01-01T00:00:00Z",
                "source": script.data_sources[0].name if script.data_sources else "unknown"
            }
        else:
            formatted_data = data
        
        return {
            "success": success,
            "data": formatted_data,
            "metadata": {
                "script_id": script.script_id,
                "script_name": script.name,
                "strategy_used": script.strategy.value,
                "fields_extracted": [f.name for f in script.fields],
                "confidence_score": script.confidence_score,
                "update_frequency": script.update_frequency.value
            },
            "errors": errors,
            "execution_summary": script.get_execution_summary()
        }


# === DEMO FUNCTIONS ===

async def demo_complete_pipeline():
    """
    Demonstrate the complete pipeline with sample form data.
    """
    print("🎯 DEMO: Complete Script Execution Pipeline")
    print("=" * 60)
    
    # Sample form data (as would come from components/form.py)
    sample_forms = [
        {
            "name": "IPO Data Scraper",
            "data": {
                'data_description': 'Current IPOs listed on Indian stock market with their grey market premium',
                'data_source': 'chittorgarh.com',
                'desired_fields': 'company_name\nlisting_date\nissue_price\ngrey_market_premium',
                'response_structure': '',
                'update_frequency': 'Daily'
            }
        },
        {
            "name": "News Headlines Scraper", 
            "data": {
                'data_description': 'Latest technology news headlines and summaries',
                'data_source': '',
                'desired_fields': 'headline\nsummary\npublished_date\nauthor',
                'response_structure': '{"articles": [{"title": "string", "content": "string"}]}',
                'update_frequency': 'Hourly'
            }
        }
    ]
    
    pipeline = ScriptExecutionPipeline()
    
    for i, sample in enumerate(sample_forms, 1):
        print(f"\n🔄 Demo {i}: {sample['name']}")
        print("-" * 40)
        
        result = await pipeline.execute_from_form_data(sample['data'])
        
        if result['success']:
            data_items = result['data'].get('data', []) if isinstance(result['data'], dict) else result['data']
            print(f"✅ Success! Extracted {len(data_items)} items")
            print(f"📊 Fields: {', '.join(result['metadata']['fields_extracted'])}")
            print(f"⚡ Strategy: {result['metadata']['strategy_used']}")
            print(f"🎯 Confidence: {result['metadata']['confidence_score']:.2f}")
            
            # Show sample data
            if data_items:
                sample_item = data_items[0] if isinstance(data_items, list) else data_items
                print(f"📝 Sample item: {sample_item}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            if 'issues' in result:
                for issue in result['issues']:
                    print(f"   - {issue}")


def demo_script_generation_only():
    """
    Demonstrate just the script generation part.
    """
    print("🤖 DEMO: AI Script Generation Only")
    print("=" * 50)
    
    form_data = {
        'data_description': 'Stock prices and trading volumes for NSE listed companies',
        'data_source': 'moneycontrol.com',
        'desired_fields': 'symbol\ncompany_name\ncurrent_price\nvolume\nchange_percent',
        'response_structure': '',
        'update_frequency': 'Real-time'
    }
    
    generator = AIScriptGenerator()
    script = generator.generate_script_from_form(form_data)
    
    print("\n📋 Generated Script Details:")
    print(f"   ID: {script.script_id}")
    print(f"   Name: {script.name}")
    print(f"   Strategy: {script.strategy.value}")
    print(f"   URL: {script.entry_url}")
    print(f"   Fields: {len(script.fields)}")
    print(f"   Confidence: {script.confidence_score:.2f}")
    
    print("\n🔧 ScriptConfig Conversion:")
    config = script.to_script_config()
    print(f"   Selectors: {list(config.selectors.keys())}")
    print(f"   Cache TTL: {config.cache_ttl}s")
    print(f"   Timeout: {config.timeout}s")
    
    return script


# === ENTRY POINT FOR FUTURE API LAYER ===

async def execute_scraping_request(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for the future API layer.
    This function will be called by the API endpoints.
    
    Args:
        form_data: User input from the form
        
    Returns:
        Scraped data and metadata
    """
    pipeline = ScriptExecutionPipeline()
    return await pipeline.execute_from_form_data(form_data)


if __name__ == "__main__":
    # Run demos
    print("🎬 Running Script Integration Demos")
    print("=" * 60)
    
    # Demo 1: Script generation only
    demo_script_generation_only()
    
    print("\n" + "=" * 60)
    
    # Demo 2: Complete pipeline
    asyncio.run(demo_complete_pipeline())