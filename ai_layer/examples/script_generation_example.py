"""
Example usage of the Scraper Script Generator.

This example demonstrates how to:
1. Configure the script generator
2. Generate a scraper script from form inputs
3. Validate the generated script
4. Handle errors
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_layer import (
    DeepSeekConfig,
    DeepSeekClient,
    ScraperScriptGenerator,
    ScriptGenerationError,
    ScriptValidationError
)
from scraping_layer.config import ScrapingConfig


def main():
    """Main example function."""
    
    print("=" * 60)
    print("Scraper Script Generator Example")
    print("=" * 60)
    
    # Step 1: Load configuration
    print("\n1. Loading configuration...")
    try:
        deepseek_config = DeepSeekConfig.from_env()
        scraping_config = ScrapingConfig.from_env()
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        print("\nMake sure DEEPSEEK_API_KEY is set in your environment")
        return
    
    # Step 2: Initialize components
    print("\n2. Initializing components...")
    deepseek_client = DeepSeekClient(
        api_key=deepseek_config.api_key,
        base_url=deepseek_config.base_url
    )
    
    script_generator = ScraperScriptGenerator(
        deepseek_client=deepseek_client,
        scraping_config=scraping_config
    )
    print("✓ Components initialized")
    
    # Step 3: Prepare form input
    print("\n3. Preparing form input...")
    form_input = {
        'data_description': 'Current IPOs listed on Indian stock market with their grey market premium',
        'data_source': 'https://www.chittorgarh.com/ipo/ipo_grey_market_premium.asp',
        'desired_fields': 'company_name\nlisting_date\nissue_price\ngrey_market_premium',
        'response_structure': '',  # Let AI decide structure
        'update_frequency': 'Daily'
    }
    
    print(f"  Data Description: {form_input['data_description']}")
    print(f"  Target URL: {form_input['data_source']}")
    print(f"  Required Fields: {form_input['desired_fields'].replace(chr(10), ', ')}")
    
    # Step 4: Generate script
    print("\n4. Generating scraper script...")
    print("  (This may take 10-30 seconds...)")
    
    try:
        generated_script = script_generator.generate_script(
            form_input=form_input,
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=4000
        )
        
        print("✓ Script generated successfully")
        
        # Step 5: Display results
        print("\n5. Script Generation Results:")
        print("-" * 60)
        
        # Metadata
        print(f"\nMetadata:")
        print(f"  Model: {generated_script.metadata.model}")
        print(f"  Generation Time: {generated_script.metadata.generation_time_ms}ms")
        print(f"  Tokens Used: {generated_script.metadata.tokens_used}")
        print(f"  Target URL: {generated_script.metadata.target_url}")
        print(f"  Required Fields: {', '.join(generated_script.metadata.required_fields)}")
        
        # Validation results
        print(f"\nValidation Results:")
        print(f"  Valid: {generated_script.validation_result.is_valid}")
        print(f"  Syntax Valid: {generated_script.validation_result.syntax_valid}")
        print(f"  Imports Valid: {generated_script.validation_result.imports_valid}")
        print(f"  No Forbidden Ops: {generated_script.validation_result.no_forbidden_ops}")
        print(f"  Function Signature Valid: {generated_script.validation_result.function_signature_valid}")
        
        if generated_script.validation_result.errors:
            print(f"\n  Errors:")
            for error in generated_script.validation_result.errors:
                print(f"    - {error}")
        
        if generated_script.validation_result.warnings:
            print(f"\n  Warnings:")
            for warning in generated_script.validation_result.warnings:
                print(f"    - {warning}")
        
        # Generated code
        print(f"\nGenerated Script:")
        print("-" * 60)
        print(generated_script.script_code)
        print("-" * 60)
        
        # Step 6: Save script to file (optional)
        output_file = "generated_scraper.py"
        with open(output_file, 'w') as f:
            f.write(generated_script.script_code)
        print(f"\n✓ Script saved to: {output_file}")
        
        # Step 7: Usage instructions
        print("\n6. Next Steps:")
        print("  1. Review the generated script")
        print("  2. Test it manually: python generated_scraper.py")
        print("  3. Integrate with the scraping layer for automated execution")
        
    except ScriptGenerationError as e:
        print(f"✗ Script generation failed: {e}")
        if hasattr(e, 'form_input'):
            print(f"  Form input: {e.form_input}")
    
    except ScriptValidationError as e:
        print(f"✗ Script validation failed: {e}")
        if hasattr(e, 'validation_result'):
            print(f"  Validation errors: {e.validation_result.errors}")
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
