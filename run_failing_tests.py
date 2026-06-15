
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tests.test_safety_pipeline import SafetyPipelineTests
from tests.test_evaluation_harness import EvaluationHarnessTests

if __name__ == "__main__":
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(SafetyPipelineTests('test_explicit_denial_does_not_trigger_emergency_alert'))
    suite.addTest(EvaluationHarnessTests('test_versioned_evaluation_corpus'))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
