# standard lib imports
import os, re, shutil, subprocess, sys, time
from subprocess import STDOUT, check_output
import colorama as color

color.init()
import yaml
import unittest

# test package imports
import logunittest.settings as sts
from logunittest.logger import remove_logs


# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        sts.verbose = 0
        cls.logunittestLogsDir = cls.mk_test_data(*args, **kwargs)
        cls.logPreserveThreshold_0 = {"days": None, "count": 5}
        cls.logPreserveThreshold_1 = {"days": 0, "count": None}

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        # remove residuals
        if os.path.isdir(cls.logunittestLogsDir):
            shutil.rmtree(cls.logunittestLogsDir)

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        logunittestLogsDir = os.path.join(sts.testDataDir, "test_logunittest_logs_1")
        # if any residuals exist due to a earlier failed test, remove it here
        if os.path.isdir(logunittestLogsDir):
            shutil.rmtree(logunittestLogsDir)
        # create a copy of the test_logunittest_logs directory to allow deletion of logs
        shutil.copytree(
            os.path.join(sts.testDataDir, "test_logunittest_logs"),
            logunittestLogsDir,
            copy_function=shutil.copy2,
        )
        return logunittestLogsDir

    def test_remove_logs(self, *args, **kwargs):
        """
        test remove_logs function
        """
        sts.deleteRatio = 1
        self.assertTrue(os.path.isdir(self.logunittestLogsDir))
        # first remove logs using _0 threshold, this should result in 5 logs remaining
        remove_logs(self.logunittestLogsDir, self.logPreserveThreshold_0)
        self.assertTrue(os.path.isdir(self.logunittestLogsDir))
        self.assertTrue(len(os.listdir(self.logunittestLogsDir)) == 5)

        # NOTE: test of _1 currently not possible since shutl.copytree changes ctime to today
        # now remove logs using _1 threshold, this should result in 1 log remaining
        # remove_logs(self.logunittestLogsDir, self.logPreserveThreshold_1)
        # self.assertTrue(os.path.isdir(self.logunittestLogsDir))
        # self.assertTrue(len(os.listdir(self.logunittestLogsDir)) == 1)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
