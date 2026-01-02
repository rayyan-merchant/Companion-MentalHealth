import sys
import os
import uuid
from typing import List, Dict

# Add the current directory to sys.path to allow imports
sys.path.append(os.getcwd())

from reasoning.orchestrator import run_krr_pipeline

def run_tests():
    test_cases = [
        ("I can't sleep", "NeedsMoreContext"),
        ("I feel stressed", "NeedsMoreContext"),
        ("I am depressed", "DepressiveSpectrum"),
        ("I panic when I have exams", "PanicRisk (if acute) or Anxiety"),
        ("My heart races and I can't breathe", "PanicRisk"),
        ("Finals are next week", "NeedsMoreContext (if no emotion)"),
        ("I feel stressed about finals", "AcademicStress")
    ]

    print(f"{'Input':<40} | {'Expected':<30} | {'Actual State':<20} | {'Concerns':<30}")
    print("-" * 130)

    for text, expected in test_cases:
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        student_id = "test_student"
        
        try:
            result = run_krr_pipeline(session_id, student_id, text)
            
            # Extract relevant info
            # The 'ranked_concerns' list contains the identified states
            actual_concerns = result.get("ranked_concerns", [])
            # In the current implementation, 'riskState' from sparql extraction is what determines the single state logic often
            # We will inspect that but sticking to the public output 'ranked_concerns' is better for end-to-end test.
            
            concerns_str = ", ".join(actual_concerns) if actual_concerns else "None"
            
            # Determine primary state (simplified for this table)
            primary_state = actual_concerns[0] if actual_concerns else "Unknown"
            
            print(f"{text:<40} | {expected:<30} | {primary_state:<20} | {concerns_str:<30}")
            
        except Exception as e:
            print(f"{text:<40} | {expected:<30} | {'ERROR':<20} | {str(e):<30}")

if __name__ == "__main__":
    run_tests()
