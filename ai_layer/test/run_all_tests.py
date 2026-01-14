"""
Run all AI layer tests sequentially.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def run_all_tests():
    """Run all test scripts."""
    
    print("=" * 70)
    print("🧪 RUNNING ALL AI LAYER TESTS")
    print("=" * 70)
    
    tests = [
        ("Connection Test", "test_connection"),
        ("Basic AI Layer Test", "test_ai_layer"),
        ("25 Records Test", "test_25_records"),
        ("10-15 Fields Test", "test_10_15_fields"),
        ("Comprehensive Test", "test_comprehensive"),
    ]
    
    results = []
    
    for test_name, test_module in tests:
        print(f"\n{'=' * 70}")
        print(f"▶️  Running: {test_name}")
        print(f"{'=' * 70}\n")
        
        try:
            # Import and run the test
            module = __import__(f"ai_layer.test.{test_module}", fromlist=[test_module])
            
            # Find the main test function
            if hasattr(module, f"{test_module.replace('test_', 'test_')}"):
                test_func = getattr(module, f"{test_module.replace('test_', 'test_')}")
            elif hasattr(module, "test_connection"):
                test_func = module.test_connection
            elif hasattr(module, "test_ai_layer"):
                test_func = module.test_ai_layer
            elif hasattr(module, "test_25_records"):
                test_func = module.test_25_records
            elif hasattr(module, "test_10_15_fields"):
                test_func = module.test_10_15_fields
            elif hasattr(module, "test_all_features"):
                test_func = module.test_all_features
            else:
                print(f"⚠️  Could not find test function in {test_module}")
                results.append((test_name, "SKIPPED"))
                continue
            
            # Run the test
            test_func()
            results.append((test_name, "PASSED"))
            print(f"\n✅ {test_name} completed successfully")
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Test interrupted by user")
            results.append((test_name, "INTERRUPTED"))
            break
        except Exception as e:
            print(f"\n❌ {test_name} failed: {e}")
            results.append((test_name, "FAILED"))
    
    # Print summary
    print(f"\n{'=' * 70}")
    print("📊 TEST SUMMARY")
    print(f"{'=' * 70}\n")
    
    for test_name, status in results:
        status_icon = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⚠️"
        print(f"   {status_icon} {test_name}: {status}")
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    
    print(f"\n{'=' * 70}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    run_all_tests()
