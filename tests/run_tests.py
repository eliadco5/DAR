#!/usr/bin/env python
"""
Test runner script for the application.
This script runs all test cases related to the continue functionality
and check failure modes.
"""

import unittest
import sys
import os

# Add parent directory to path to allow imports from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from test_continue_functionality import TestContinueFunctionality
from test_check_failure_mode import TestCheckFailureMode

if __name__ == "__main__":
    # Create a test suite combining all tests
    suite = unittest.TestSuite()
    
    # Add test cases for continue functionality
    suite.addTest(unittest.makeSuite(TestContinueFunctionality))
    
    # Add test cases for check failure mode
    suite.addTest(unittest.makeSuite(TestCheckFailureMode))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful()) 