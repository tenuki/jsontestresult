import json
from unittest import TestResult, TestCase
from unittest.case import _SubTest

RESULT_OK, RESULT_ERROR, RESULT_FAIL, RESULT_SKIP, RESULT_EXPECTED_FAIL, RESULT_UNEXPECTED_SUCCESS = (
                                                'ok', 'error', 'fail', 'skip', 'expected fail', 'unexpected success')
TestResultCategories = {RESULT_OK, RESULT_ERROR, RESULT_FAIL, RESULT_SKIP, RESULT_EXPECTED_FAIL,
                        RESULT_UNEXPECTED_SUCCESS}


def getDescription(test):
    # doc_first_line = test.shortDescription()
    # if self.descriptions and doc_first_line:
    #     return '\n'.join((str(test), doc_first_line))
    # else:
    #     return str(test)
    return str(test)


class TestLineInfo:
    def startTest(self, test):
        raise NotImplemented

    def addNumStat(self, test, name, value):
        raise NotImplemented

    def addSubTest(self, test, subtest, err):
        raise NotImplemented

    def addSuccess(self, test):
        raise NotImplemented

    def addError(self, test, err):
        raise NotImplemented

    def addFailure(self, test, err):
        raise NotImplemented

    def addSkip(self, test, reason):
        raise NotImplemented

    def addExpectedFailure(self, test, err):
        raise NotImplemented

    def addUnexpectedSuccess(self, test):
        raise NotImplemented


class CompositeLineInfo(TestLineInfo):
    def __init__(self, *lineinfos):
        self.lineinfos = lineinfos

    def startTest(self, test):
        for li in self.lineinfos: li.startTest(test)

    def addNumStat(self, test, name, value):
        for li in self.lineinfos: li.addNumStat(test, name, value)

    def addSubTest(self, test, subtest, err):
        for li in self.lineinfos: li.addSubTest(test, subtest, err)

    def addSuccess(self, test):
        for li in self.lineinfos: li.addSuccess(test)

    def addError(self, test, err):
        for li in self.lineinfos: li.addError(test, err)

    def addFailure(self, test, err):
        for li in self.lineinfos: li.addFailure(test, err)

    def addSkip(self, test, reason):
        for li in self.lineinfos: li.addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        for li in self.lineinfos: li.addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        for li in self.lineinfos: li.addUnexpectedSuccess(test)


class TestLineRecorder(TestLineInfo):
    def __init__(self):
        self.raw_results = []
        self.stats = {}
        for category in TestResultCategories:
            self.stats[category] = 0

    @property
    def result(self):
        return {
            'stats': self.stats,
            'raw_results': self.raw_results
        }

    def startTest(self, test):
        pass

    def addSubTest(self, test, subtest, err):
        test_desc = getDescription(test)
        if err is None:
            self.addSuccess(str(subtest))
        else:
            self.addFailure(str(subtest), err)

    def addRawStat(self, category, amount):
        self.stats[category] = self.stats.get(category, 0) + amount

    def genericAddTest(self, category, test, msg):
        self.addRawStat(category, 1)
        self.raw_results.append({getDescription(test): msg})

    def addNumStat(self, test, name, value):
        label = getDescription(test)+'.'+name
        category = label.rsplit('.', 1)[1]
        self.addRawStat(category, value)
        self.raw_results.append({label: value})

    def addSuccess(self, test):
        self.genericAddTest(RESULT_OK, test, 'ok')

    def addError(self, test, err):
        self.genericAddTest(RESULT_ERROR, test, 'ERROR')

    def addFailure(self, test, err):
        self.genericAddTest(RESULT_FAIL, test, 'FAIL')

    def addSkip(self, test, reason):
        self.genericAddTest(RESULT_SKIP, test, "skipped {0!r}".format(reason))

    def addExpectedFailure(self, test, err):
        self.genericAddTest(RESULT_EXPECTED_FAIL, test, "expected fail")

    def addUnexpectedSuccess(self, test):
        self.genericAddTest(RESULT_UNEXPECTED_SUCCESS, test, "unexpected success")


class Dots(TestLineInfo):
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions):
        self.stream = stream
        self.descriptions = descriptions
        self._newline = True

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def startTest(self, test):
        self.stream.write(self.getDescription(test))
        self.stream.write(" ... ")
        self.stream.flush()
        self._newline = False

    def _write_status(self, test, status, extra=''):
        is_subtest = isinstance(test, _SubTest)
        if is_subtest or self._newline:
            if not self._newline:
                self.stream.writeln()
            if is_subtest:
                self.stream.write("  ")
            self.stream.write(self.getDescription(test)+extra)
            self.stream.write(" ... ")
        self.stream.writeln(status)
        self.stream.flush()
        self._newline = True

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self._write_status(subtest, "FAIL" if issubclass(err[0], subtest.failureException) else "ERROR")

    def addNumStat(self, test, name, value):
        self._write_status(test, str(value), '.'+name)

    def addSuccess(self, test):
        self._write_status(test, "ok")

    def addError(self, test, err):
        self._write_status(test, "ERROR")

    def addFailure(self, test, err):
        self._write_status(test, "FAIL")

    def addSkip(self, test, reason):
        self._write_status(test, "skipped {0!r}".format(reason))

    def addExpectedFailure(self, test, err):
        self.stream.writeln("expected failure")
        self.stream.flush()

    def addUnexpectedSuccess(self, test):
        self.stream.writeln("unexpected success")
        self.stream.flush()


class JsonTestResult(TestResult):
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity):
        super(JsonTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.rec = TestLineRecorder()
        self.d = CompositeLineInfo(Dots(stream, descriptions), self.rec)

    def startTest(self, test):
        super(JsonTestResult, self).startTest(test)
        self.d.startTest(test)

    def addSubTest(self, test, subtest, err):
        self.d.addSubTest(test, subtest, err)
        super(JsonTestResult, self).addSubTest(test, subtest, err)

    def addNumStat(self, test, name, value):
        self.d.addNumStat(test, name, value)

    def collectStats(self, test):
        _stats = getattr(test, '_numstat', {})
        for k, v in _stats.items():
            self.addNumStat(test, k, v)

    def addSuccess(self, test):
        super(JsonTestResult, self).addSuccess(test)
        self.d.addSuccess(test)
        self.collectStats(test)

    def addError(self, test, err):
        super(JsonTestResult, self).addError(test, err)
        self.d.addError(test, err)
        self.collectStats(test)

    def addFailure(self, test, err):
        super(JsonTestResult, self).addFailure(test, err)
        self.d.addFailure(test, err)
        self.collectStats(test)

    def addSkip(self, test, reason):
        super(JsonTestResult, self).addSkip(test, reason)
        self.d.addSkip(test, reason)
        self.collectStats(test)

    def addExpectedFailure(self, test, err):
        super(JsonTestResult, self).addExpectedFailure(test, err)
        self.d.addExpectedFailure(test, err)
        self.collectStats(test)

    def addUnexpectedSuccess(self, test):
        super(JsonTestResult, self).addUnexpectedSuccess(test)
        self.d.addUnexpectedSuccess(test)
        self.collectStats(test)

    def json(self):
        return self.rec.result

    def printErrors(self):
        self.stream.writeln()
        self.stream.flush()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)
        unexpectedSuccesses = getattr(self, 'unexpectedSuccesses', ())
        if unexpectedSuccesses:
            self.stream.writeln(self.separator1)
            for test in unexpectedSuccesses:
                self.stream.writeln(f"UNEXPECTED SUCCESS: {getDescription(test)}")
            self.stream.flush()
        for line in json.dumps(self.json(), indent=4).splitlines():
            self.stream.writeln(line)
        self.stream.flush()

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour, getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)
            self.stream.flush()


class ExtendedTestCase(TestCase):
    def setUp(self) -> None:
        self._numstat = {}

    def addNumStat(self, name, value):
        self._numstat[name] = value
