import unittest
import test.all_tests
import coverage

testSuite = test.all_tests.create_test_suite()

# Create a coverage object
cov = coverage.Coverage()
cov.start()

result = unittest.TextTestRunner().run(testSuite)

# Stop and save the coverage data
cov.stop()
cov.save()

if not result.wasSuccessful():
    sys.exit(1)
