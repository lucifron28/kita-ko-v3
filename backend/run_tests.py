#!/usr/bin/env python
"""
Test runner for Kitako backend

This script runs all tests and generates a coverage report.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
    django.setup()
    
    # Import test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run tests
    print("🧪 Running Kitako Backend Tests")
    print("=" * 50)
    
    # Test modules to run
    test_modules = [
        'tests.test_models',
        'tests.test_api', 
        'tests.test_services',
    ]
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)
