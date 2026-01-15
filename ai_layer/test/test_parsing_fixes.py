"""
Test script to verify parsing fixes for:
1. No duplicate keys with commas (e.g., "race_winner," vs "race_winner")
2. Date fields contain actual dates, not race times/durations
3. Proper field mapping based on semantic meaning
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_layer.parsing_prompt_builder import ParsingPromptBuilder
from ai_layer.parsing_validator import ParsingValidator
from ai_layer.deepseek_client import DeepSeekClient
from ai_layer.config import DeepSeekConfig

# Sample scraped F1 data (from user's actual scraping result)
SCRAPED_DATA = """
venue:Record 12:cla: 12driver: Y. TsunodaRacing Bulls#: 22laps: 57date: +1 Lap1:26'48.029interval: 3.487km/h: 207.995pits: 1points:retirement:chassis: RBengine: Red Bullrace_winner: 12race_runner_up: Y. TsunodaRacing Bullsrace_runner_up_2: 22venue:Record 13:cla: 13driver: Z. GuanyuSauber#: 24laps: 57date: +1 Lap1:26'50.595interval: 2.566km/h: 207.893pits: 2points:retirement:chassis: Sauberengine: Ferrarirace_winner: 13race_runner_up: Z. GuanyuSauberrace_runner_up_2: 24venue:Record 14:cla: 14driver: L. StrollAston Martin Racing#: 18laps: 57date: +1 Lap1:26'51.764interval: 1.169km/h: 207.846pits: 2points:retirement:chassis: Aston Martinengine: Mercedesrace_winner: 14race_runner_up: L. StrollAston Martin Racingrace_runner_up_2: 18venue:Record 15:cla: 15driver: J. DoohanAlpine#: 61laps: 57date: +1 Lap1:26'59.846interval: 8.082km/h: 207.524pits: 1points:retirement:chassis: Alpineengine: Renaultrace_winner: 15race_runner_up: J. DoohanAlpinerace_runner_up_2: 61venue:Record 16:cla: 16driver: K. MagnussenHaas F1 Team#: 20laps: 57date: +1 Lap1:27'50.888interval: 51.042km/h: 205.515pits: 4points:retirement:chassis: Haasengine: Ferrarirace_winner: 16race_runner_up: K. MagnussenHaas F1 Teamrace_runner_up_2: 20venue:Record 17:cla: dnfdriver: L. LawsonRacing Bulls#: 30laps: 55date: +3 Laps1:24'36.949interval: 2 Lapskm/h: 205.876pits: 3points:retirement: Retirementchassis: RBengine: Red Bullrace_winner: dnfrace_runner_up: L. LawsonRacing Bullsrace_runner_up_2: 30venue:Record 18:cla: dnfdriver: V. BottasSauber#: 77laps: 30date: +28 Laps47'27.280interval: 25 Lapskm/h: 200.167pits: 2points:retirement: Collisionchassis: Sauberengine: Ferrarirace_winner: dnfrace_runner_up: V. BottasSauberrace_runner_up_2: 77
From: https://www.bbc.com/sport/formula1/2024/results
------------------------------------------------------------
Record 1:rank: 11driver: Lando NorrisNORMcLarenMcLarennumber: 44grid: 11pits: 11fastest_lap: 1:27.4381:27.438date: 1:26:33.2911:26:33.291points: 2525race_winner: 11race_runner_up: Lando NorrisNORMcLarenMcLarenrace_runner_up_2: 44venue:Record 2:rank: 22driver: Carlos Sainz JnrSAIFerrariFerrarinumber: 5555grid: 33pits: 11fastest_lap: 1:27.7651:27.765date: 5.832 behind+5.832points: 1818race_winner: 22race_runner_up: Carlos Sainz JnrSAIFerrariFerrarirace_runner_up_2: 5555venue:Record 3:rank: 33driver: Charles LeclercLECFerrariFerrarinumber: 1616grid: 1919pits: 11fastest_lap: 1:28.0181:28.018date: 31.928 behind+31.928points: 1515race_winner: 33race_runner_up: Charles LeclercLECFerrariFerrarirace_runner_up_2: 1616
"""

# User requirements with comma-separated fields (the problematic input)
USER_REQUIREMENTS_COMMA = {
    'data_description': 'F1 2024 race results with driver standings',
    'desired_fields': 'race_winner, race_runner_up, race_runner_up_2, venue, date',  # Comma-separated
    'response_structure': '',
    'update_frequency': 'Daily'
}

# User requirements with newline-separated fields
USER_REQUIREMENTS_NEWLINE = {
    'data_description': 'F1 2024 race results with driver standings',
    'desired_fields': 'race_winner\nrace_runner_up\nrace_runner_up_2\nvenue\ndate',  # Newline-separated
    'response_structure': '',
    'update_frequency': 'Daily'
}


def test_field_parsing():
    """Test that fields are correctly parsed from both comma and newline formats."""
    print("=" * 60)
    print("TEST 1: Field Parsing (comma vs newline)")
    print("=" * 60)
    
    prompt_builder = ParsingPromptBuilder()
    
    # Test comma-separated
    fields_comma = prompt_builder._parse_desired_fields('race_winner, race_runner_up, venue, date')
    print(f"\nComma-separated input: 'race_winner, race_runner_up, venue, date'")
    print(f"Parsed fields: {fields_comma}")
    
    # Test newline-separated
    fields_newline = prompt_builder._parse_desired_fields('race_winner\nrace_runner_up\nvenue\ndate')
    print(f"\nNewline-separated input: 'race_winner\\nrace_runner_up\\nvenue\\ndate'")
    print(f"Parsed fields: {fields_newline}")
    
    # Verify no trailing commas
    has_comma_in_fields = any(',' in f for f in fields_comma)
    print(f"\n✓ No commas in parsed fields (comma input): {not has_comma_in_fields}")
    
    has_comma_in_fields_newline = any(',' in f for f in fields_newline)
    print(f"✓ No commas in parsed fields (newline input): {not has_comma_in_fields_newline}")
    
    # Verify same result
    print(f"✓ Both formats produce same fields: {fields_comma == fields_newline}")
    
    return not has_comma_in_fields and not has_comma_in_fields_newline


def test_validator_field_parsing():
    """Test that validator also correctly parses fields."""
    print("\n" + "=" * 60)
    print("TEST 2: Validator Field Parsing")
    print("=" * 60)
    
    validator = ParsingValidator()
    
    # Test comma-separated
    fields_comma = validator._parse_field_list('race_winner, race_runner_up, venue, date')
    print(f"\nComma-separated: {fields_comma}")
    
    # Test newline-separated
    fields_newline = validator._parse_field_list('race_winner\nrace_runner_up\nvenue\ndate')
    print(f"Newline-separated: {fields_newline}")
    
    has_comma = any(',' in f for f in fields_comma)
    print(f"\n✓ Validator parses comma-separated correctly: {not has_comma}")
    
    return not has_comma


def test_prompt_generation():
    """Test that generated prompts don't include duplicate field instructions."""
    print("\n" + "=" * 60)
    print("TEST 3: Prompt Generation")
    print("=" * 60)
    
    prompt_builder = ParsingPromptBuilder()
    
    messages = prompt_builder.build_parsing_prompt(
        scraped_text=SCRAPED_DATA[:500],  # Use truncated data for test
        user_requirements=USER_REQUIREMENTS_COMMA
    )
    
    user_prompt = messages[1]['content']
    system_prompt = messages[0]['content']
    
    print(f"\nSystem prompt length: {len(system_prompt)} chars")
    print(f"User prompt length: {len(user_prompt)} chars")
    
    # Check that fields are listed correctly in prompt
    print("\nChecking field listing in user prompt...")
    if '- race_winner' in user_prompt:
        print("✓ 'race_winner' field listed correctly")
    if '- race_winner,' in user_prompt:
        print("✗ 'race_winner,' with comma found (BAD)")
        return False
    
    # Check semantic correctness instructions
    if 'SEMANTIC CORRECTNESS' in system_prompt:
        print("✓ Semantic correctness instructions present")
    
    if 'date" fields MUST contain actual dates' in system_prompt:
        print("✓ Date field guidance present")
    
    return True


def test_full_parsing_with_api():
    """Test full parsing with actual DeepSeek API call."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Parsing with DeepSeek API")
    print("=" * 60)
    
    try:
        config = DeepSeekConfig.from_env()
        client = DeepSeekClient(config.api_key, config.base_url)
    except Exception as e:
        print(f"\n⚠️ Skipping API test - configuration error: {e}")
        return None
    
    prompt_builder = ParsingPromptBuilder()
    validator = ParsingValidator()
    
    # Build prompt
    messages = prompt_builder.build_parsing_prompt(
        scraped_text=SCRAPED_DATA,
        user_requirements=USER_REQUIREMENTS_COMMA
    )
    
    print("\nCalling DeepSeek API...")
    
    try:
        ai_output = client.generate_completion(
            messages=messages,
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=4000
        )
        
        print(f"✓ API response received ({len(ai_output)} chars)")
        
        # Validate response
        parsed_data = validator.validate_parsed_response(
            ai_output=ai_output,
            user_requirements=USER_REQUIREMENTS_COMMA
        )
        
        print(f"✓ Response validated successfully")
        
        # Check for duplicate keys with commas
        json_str = json.dumps(parsed_data)
        
        issues = []
        
        if '"race_winner,"' in json_str:
            issues.append("Found 'race_winner,' with trailing comma")
        if '"race_runner_up,"' in json_str:
            issues.append("Found 'race_runner_up,' with trailing comma")
        if '"date,"' in json_str:
            issues.append("Found 'date,' with trailing comma")
        if '"_source_url"' in json_str:
            issues.append("Found '_source_url' in records (should be in metadata only)")
        
        # Check date field values
        if 'data' in parsed_data and isinstance(parsed_data['data'], list):
            for i, record in enumerate(parsed_data['data'][:3]):  # Check first 3
                date_val = record.get('date')
                if date_val:
                    # Check if it looks like a time (contains colons and looks like duration)
                    if isinstance(date_val, str) and ':' in date_val and ('.' in date_val or "'" in date_val):
                        if not any(month in date_val.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
                            issues.append(f"Record {i+1}: 'date' field contains time value: {date_val}")
        
        if issues:
            print("\n⚠️ Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✓ No duplicate keys or semantic issues found!")
        
        # Print sample output
        print("\n--- Sample Parsed Output (first 2 records) ---")
        if 'data' in parsed_data and parsed_data['data']:
            for record in parsed_data['data'][:2]:
                print(json.dumps(record, indent=2))
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"\n✗ API test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PARSING FIXES VERIFICATION TESTS")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Field parsing
    results['field_parsing'] = test_field_parsing()
    
    # Test 2: Validator field parsing
    results['validator_parsing'] = test_validator_field_parsing()
    
    # Test 3: Prompt generation
    results['prompt_generation'] = test_prompt_generation()
    
    # Test 4: Full API test (optional)
    results['api_test'] = test_full_parsing_with_api()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "⚠️ SKIPPED"
        elif result:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        print(f"{test_name}: {status}")
    
    # Overall result
    passed = all(r for r in results.values() if r is not None)
    print("\n" + ("=" * 60))
    print(f"OVERALL: {'✓ ALL TESTS PASSED' if passed else '✗ SOME TESTS FAILED'}")
    print("=" * 60)
    
    return passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
