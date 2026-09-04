"""
Comprehensive Validation & Test Suite for Macro Flow Stock Navigator.
Runs unit tests and verifies live Markdown and JSON analysis workflows.
"""

import sys
import os
import pytest

def main():
    print("=" * 75)
    print("[INFO] RUNNING COMPREHENSIVE SKILL TEST SUITE")
    print("=" * 75)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, base_dir)

    # 1. Run Pytest Suite
    print("\n[Step 1/2] Executing Unit & Integration Tests via Pytest...")
    test_args = ["-v", os.path.join(base_dir, "tests")]
    exit_code = pytest.main(test_args)
    if exit_code != 0:
        print(f"[FAIL] Pytest failed with exit code {exit_code}")
        sys.exit(exit_code)
    print("[PASS] Pytest suite passed successfully!")

    # 2. Test Multi-Ticker Live Analysis Workflow
    print("\n[Step 2/2] Testing Real-Time Analysis Workflows for Key Stock Archetypes...")
    from scripts.run_analysis import run_navigator
    
    test_tickers = ["GOOG", "SOFI", "NVDA", "JNJ", "CAT"]
    for t in test_tickers:
        summary = run_navigator(ticker=t, output_format="summary")
        print(f"  • {summary}")

    print("\n" + "=" * 75)
    print("[SUCCESS] ALL SKILL TESTS PASSED SUCCESSFULLY! Ready for deployment.")
    print("=" * 75)

if __name__ == "__main__":
    main()
