# standard lib imports
import os, re, shutil, subprocess, sys, time

import colorama as color

color.init()
import yaml
import unittest

# test package imports
import logunittest.settings as sts
from logunittest.logunittest import UnitTestWithLogging as LUT
from logunittest.logunittest import Coverage


# print(f"\n__file__: {__file__}")


class UnitTest(unittest.TestCase):
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
        expected = "logunittest summary: [all:20 ok:19 err:1]"
        with open(self.logFile, "r") as f:
            results = f.read()
        t = LUT(*args, **kwargs)
        self.assertEqual(t.extract_stats(results, *kwargs), expected)

    def test___call__(self, *args, **kwargs):
        expected = r"<@>\d\d-\d\d \d\d:\d\d!\[all:\d ok:\d err:\d\]<@>"
        cov = Coverage()
        cov.logDir = sts.testDataDir
        cmds = [
            "python",
            "-c",
            "from logunittest.logunittest import Coverage; Coverage()()",
            "2>&1",
        ]
        out = subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE)
        self.assertTrue(re.match(expected, out.communicate()[0].decode("utf-8")))


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
