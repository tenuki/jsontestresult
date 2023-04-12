# json test result

A python test result class which keeps results in json format. Also allow to track custom stat reports from tests.

## Basic Json result usage

```python
from jsontestresult import JsonTestResult

runner = TextTestRunner(resultclass=JsonTestResult)
suite = TestLoader().loadTestsFromTestCase(MyBasicTest)
results = runner.run(suite)
```

Sample output:

```json
{
    "stats": {
        "expected fail": 0,
        "ok": 1,
        "unexpected success": 0,
        "error": 1,
        "fail": 1,
        "skip": 0
    },
    "raw_results": [
        {
            "testSomething (__main__.MyTest.testSomething)": "ok"
        },
        {
            "testSomethingError (__main__.MyTest.testSomethingError)": "ERROR"
        },
        {
            "testSomethingFailed (__main__.MyTest.testSomethingFailed)": "FAIL"
        }
    ]
}
```

## Report a few stats usage

```python
from jsontestresult import JsonTestResult, TestCaseWithNumStats


class MyBasicTest(TestCaseWithNumStats):
    def testSomething(self):
        self.addNumStat('speed', 66)
        self.addNumStat('gas', 42)
        self.assertEqual(4, 2 * 2)

[...]

runner = TextTestRunner(resultclass=JsonTestResult)
suite = TestLoader().loadTestsFromTestCase(MyBasicTest)
results = runner.run(suite)
```


Sample output:

```json
{
    "stats": {
        "expected fail": 0,
        "error": 1,
        "fail": 1,
        "skip": 0,
        "unexpected success": 0,
        "ok": 1,
        "speed": 66,
        "gas": 42
    },
    "raw_results": [
        {
            "testSomething (__main__.MyBasicTest)": "ok"
        },
        {
            "testSomething (__main__.MyBasicTest).speed": 66
        },
        {
            "testSomething (__main__.MyBasicTest).gas": 42
        },
        {
            "testSomethingError (__main__.MyBasicTest)": "ERROR"
        },
        {
            "testSomethingFailed (__main__.MyBasicTest)": "FAIL"
        }
    ]
}
```