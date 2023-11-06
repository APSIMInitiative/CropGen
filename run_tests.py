import unittest
import test.all_tests

testSuite = test.all_tests.create_test_suite()
result = unittest.TextTestRunner().run(testSuite)

if not result.wasSuccessful():
    sys.exit(1)
