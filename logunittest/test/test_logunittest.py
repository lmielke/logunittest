# standard lib imports
import os, re, shutil, subprocess, sys, time
from subprocess import STDOUT, check_output
import colorama as color

color.init()
import yaml
import unittest

# test package imports
import logunittest.settings as sts
from logunittest.logunittest import UnitTestWithLogging

# from logunittest.logunittest import extract_stats
from logunittest.logunittest import Coverage


# print(f"\n__file__: {__file__}")


class Test_UnitTestWithLogging(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.testData = cls.mk_test_data(*args, **kwargs)
        cls.logFile = os.path.join(sts.testDataDir, "logunittest_2022-12-01-10-06-10-162984.txt")

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        with open(os.path.join(sts.testDataDir, "logunittest.yml"), "r") as f:
            out = yaml.safe_load(f)
        return out

    def test_extract_stats(self, *args, **kwargs):
        expected = (20, 19, 1)
        with open(self.logFile, "r") as f:
            results = f.read()
        test = UnitTestWithLogging(*args, createLog=False, **kwargs)
        self.assertEqual(test.extract_stats_unittest(results, *kwargs), expected)

    def test___call__(self, *args, **kwargs):
        # print(f"\n__call__ in {sys.version, sys.executable} ...")
        expected = r"<@>\d\d-\d\d \d\d:\d\d!\[all:\d+ ok:\d+ err:\d+\]<@>"
        cov = Coverage()
        cov.logDir = sts.testDataDir
        cmds = [
            "python",
            "-c",
            "from logunittest.logunittest import Coverage; Coverage()()",
            "2>&1",
        ]
        if os.name == "nt":
            out = subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE)
            self.assertTrue(re.match(expected, out.communicate(timeout=5)[0].decode("utf-8")))
        else:
            print(f"__call__ in {os.name} not tested...")


class Test_Coverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        cls.testData = cls.mk_test_data(*args, **kwargs)
        cls.logDir = sts.testDataDir

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        return Coverage(*args, **kwargs)

    def test_get_stats(self, *args, **kwargs):
        expected = r"<@>\d\d-\d\d \d\d:\d\d!\[all:\d+ ok:\d+ err:\d+\]<@>"
        testId, stats, results = self.testData.get_stats(*args, **kwargs)
        self.assertTrue(re.match(expected, stats))


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
