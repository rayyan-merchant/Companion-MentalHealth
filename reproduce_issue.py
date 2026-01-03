"""
Hybrid Pipeline Verification Script
=====================================
Tests the full agentic system against required test cases.
"""

import sys
import os
import uuid

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.pipeline import process_message


def run_verification():
    """Run all required test cases."""
    
    # Reset singletons to pick up any pattern changes
    import agents.ml_extractor as ml_ext
    import agents.symbolic_reasoner as sym
    import agents.llm_explainer as llm_exp
    ml_ext._extractor_instance = None
    sym._reasoner_instance = None
    llm_exp._explainer_instance = None
    
    print("\n" + "=" * 80)
    print("HYBRID AGENTIC SYSTEM VERIFICATION")
    print("=" * 80)
    
    # Test cases from requirements
    test_cases = [
        ("Anxious today", "ask_clarification", "Ask clarification"),
        ("Finals are killing me", "explain", "Academic Stress"),
        ("I can't sleep and feel restless", "explain", "Anxiety Risk"),
        ("I feel empty and avoid everyone", "explain", "Depressive Spectrum"),
        ("Heart racing, can't breathe", "explain", "Panic Risk")
    ]
    
    session_id = f"verify_{uuid.uuid4().hex[:8]}"
    
    print(f"\nSession: {session_id}")
    print("-" * 80)
    print(f"{'Input':<35} | {'Expected':<25} | {'Actual State':<20} | {'Action':<15} | {'PASS?'}")
    print("-" * 80)
    
    passed = 0
    failed = 0
    
    for text, expected_action, expected_state in test_cases:
        result = process_message(session_id, text)
        
        actual_state = result.get("state", "None")
        actual_action = result.get("action", "unknown")
        
        # Check if test passed
        # For clarification cases, action must be ask_clarification
        # For others, state should match
        if expected_action == "ask_clarification":
            test_passed = actual_action == "ask_clarification"
        else:
            # Flexible matching for state names
            test_passed = (
                expected_state.lower().replace(" ", "") in 
                actual_state.lower().replace(" ", "").replace("_", "")
            )
        
        status = "PASS" if test_passed else "FAIL"
        
        if test_passed:
            passed += 1
        else:
            failed += 1
        
        print(f"{text:<35} | {expected_state:<25} | {actual_state:<20} | {actual_action:<15} | {status}")
    
    print("-" * 80)
    print(f"\nResults: {passed}/{len(test_cases)} passed, {failed} failed")
    
    if failed == 0:
        print("\n[OK] ALL TESTS PASSED - System is functioning correctly.")
    else:
        print("\n[WARN] SOME TESTS FAILED - Review the pipeline.")
    
    # Show a sample response
    print("\n" + "=" * 80)
    print("SAMPLE RESPONSE")
    print("=" * 80)
    
    sample_result = process_message(f"sample_{uuid.uuid4().hex[:8]}", "I've been feeling stressed about my exams")
    
    print(f"\nInput: 'I've been feeling stressed about my exams'")
    print(f"\nResponse:\n{sample_result['response']}")
    print(f"\nState: {sample_result['state']}")
    print(f"Confidence: {sample_result['confidence']}")
    print(f"Evidence: {sample_result['evidence']}")
    
    if sample_result.get('disclaimer'):
        print(f"\nDisclaimer: {sample_result['disclaimer']}")


if __name__ == "__main__":
    run_verification()
