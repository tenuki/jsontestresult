import os
import sys
from contextlib import contextmanager
from unittest import TestCase, TextTestRunner, TestLoader

from jsontestresult import JsonTestResult, TestCaseWithNumStats


class MyBasicTest(TestCaseWithNumStats):
    def testSomething(self):
        self.addNumStat('speed', 66)
        self.addNumStat('gas', 42)
        self.assertEqual(4, 2 * 2)

    def testSomethingFailed(self):
        self.assertEqual(5, 2 * 2)

    def testSomethingError(self):
        raise Exception("oops")


@contextmanager
def PreventOutput():
    f = open(os.devnull, 'w')
    sys.stdout, out = f, sys.stdout
    sys.stderr, err = f, sys.stderr
    try:
        yield
    finally:
        sys.stdout = out
        sys.stderr = err


class TestTest(TestCase):
    def test_BasicTestShouldWork(self):
        with PreventOutput():
            runner = TextTestRunner()
            suite = TestLoader().loadTestsFromTestCase(MyBasicTest)
            results = runner.run(suite)
        self.assertEqual(1, len(results.errors))
        self.assertEqual(1, len(results.failures))
        self.assertEqual(3, results.testsRun)
        self.assertEqual([], results.skipped)
        self.assertEqual([], results.unexpectedSuccesses)
        self.assertEqual([], results.expectedFailures)

    def test_JsonResultShouldWorkToo(self):
        with PreventOutput():
            runner = TextTestRunner(resultclass=JsonTestResult)
            suite = TestLoader().loadTestsFromTestCase(MyBasicTest)
            results = runner.run(suite)
        expected = {
            'stats': {
                'error': 1,
                'unexpected success': 0,
                'ok': 1,
                'skip': 0,
                'expected fail': 0,
                'fail': 1,
                'speed': 66,
                'gas': 42
            },
            'raw_results': {
                'testSomething (__main__.MyBasicTest)': 'ok',
                'testSomething (__main__.MyBasicTest).speed': 66,
                'testSomething (__main__.MyBasicTest).gas': 42,
                'testSomethingError (__main__.MyBasicTest)': 'ERROR',
                'testSomethingFailed (__main__.MyBasicTest)': 'FAIL'
            }
        }
        self.maxDiff = None
        self.assertEqual(expected, results.json())


if __name__ == "__main__":
    runner = TextTestRunner(verbosity=2)
    suite = TestLoader().loadTestsFromTestCase(TestTest)
    runner.run(suite)
