# json test result

A python test result class which keeps results in json format and something more..

Usage

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