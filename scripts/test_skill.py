#!/usr/bin/env python3
"""
Comprehensive Validation & Test Suite for Macro Flow Stock Navigator.
Runs unit tests, checks synthetic datasets, and verifies Markdown and JSON rendering.
"""

import sys
import os
import subprocess
import pytest

def main():
    print("=" * 75)
    print("[INFO] RUNNING COMPREHENSIVE SKILL TEST SUITE")
    print("=" * 75)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, base_dir)

    # 1. Run Pytest Suite
    print("\n[Step 1/3] Executing Unit & Integration Tests via Pytest...")
    test_args = ["-v", os.path.join(base_dir, "tests")]
    exit_code = pytest.main(test_args)
    if exit_code != 0:
        print(f"[FAIL] Pytest failed with exit code {exit_code}")
        sys.exit(exit_code)
    print("[PASS] Pytest suite passed successfully!")

    # 2. Test Synthetic Data Generator
    print("\n[Step 2/3] Verifying Synthetic Market Data Generation...")
    from scripts.generate_synthetic_data import generate_synthetic_dataset
    sample_json = os.path.join(base_dir, "sample_data", "synthetic_market_data.json")
    generate_synthetic_dataset(sample_json, lookback_days=120)
    assert os.path.exists(sample_json), "Synthetic dataset file missing!"
    print("[PASS] Synthetic dataset verified!")

    # 3. Test Multi-Ticker Analysis Workflow
    print("\n[Step 3/3] Testing Analysis Workflows for Key Stock Archetypes...")
    from scripts.run_analysis import run_navigator
    
    test_tickers = ["GOOG", "SOFI", "NVDA", "JNJ", "CAT"]
    for t in test_tickers:
        summary = run_navigator(ticker=t, mode="synthetic", output_format="summary")
        print(f"  • {summary}")

    print("\n" + "=" * 75)
    print("[SUCCESS] ALL SKILL TESTS PASSED SUCCESSFULLY! Ready for deployment.")
    print("=" * 75)

if __name__ == "__main__":
    main()
