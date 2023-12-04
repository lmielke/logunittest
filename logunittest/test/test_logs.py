# standard lib imports
import os, time
import colorama as color

color.init()
import yaml
import unittest

# test package imports
import logunittest.settings as sts
import logunittest.actions.logs as logs
from logunittest.logunittest import Package, Coverage


# print(f"\n__file__: {__file__}")


class Test_Unittest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.mk_test_data(*args, **kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        pass

    def test_get_logs(self, *args, **kwargs):
        logPath = os.path.join(sts.testDataDir, "logunittest_2023-11-27-10-58-31_py3.11.6.log")
        testId = "2023-11-27-10-58-31"
        logList = logs.get_logs(*args, testId=testId, logDir=sts.testDataDir, **kwargs)
        self.assertEqual(logList[0], logPath)

    def test_get_logs_by_logId(self, *args, **kwargs):
        cov = Coverage()
        logPath = os.path.join(sts.testDataDir, "logunittest_2023-11-27-10-58-31_py3.11.6.log")
        testId = "2023-11-27-10-58-31"
        logDict = logs.get_logs_by_logId(
            cov, *args, testId=testId, logDir=sts.testDataDir, **kwargs
        )
        self.assertEqual(list(logDict.keys())[0], logPath)

    def test_get_log_results(self, *args, **kwargs):
        cov = Coverage()
        logPath = os.path.join(sts.testDataDir, "logunittest_2023-11-27-10-58-31_py3.11.6.log")
        testId = "2023-11-27-10-58-31"
        outTestId = logs.get_log_results(cov, *args, testId=testId, logPath=logPath, **kwargs)
        self.assertEqual(outTestId, testId)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
