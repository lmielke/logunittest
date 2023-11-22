# standard lib imports
import json, os
import colorama as color

color.init()
import yaml
import unittest

# test package imports
import logunittest.settings as sts
from logunittest.general import TestParams


# print(f"\n__file__: {__file__}")


class Test_TestParams(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        sts.verbose = 0
        # cls.testData = cls.mk_test_data(*args, **kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        pass

    def test_get_config_dir(self, *args, **kwargs):
        testParams = TestParams(*args, pgDir=sts.packageDir, **kwargs)
        configDir = testParams.get_config_dir(*args, pgDir=sts.packageDir, **kwargs)
        self.assertEqual(configDir, sts.packageDir)
        testParams = TestParams(*args, pgDir=sts.packageDir, application="application_0", **kwargs)
        configDir = testParams.get_config_dir(
            *args, pgDir=sts.packageDir, application="application_0", **kwargs
        )
        self.assertTrue(configDir.endswith(f"testlogs{os.sep}application_0"))

    def test_load_tox_file(self, *args, **kwargs):
        testParams = TestParams("test_tox.ini", *args, pgDir=sts.testDataDir, **kwargs)
        self.assertEqual(testParams.__dict__["envList"], ["3.7", "3.9", "3.10"])
        testParams = TestParams(
            "tox.ini", *args, pgDir=sts.testDataDir, application="application_0", **kwargs
        )
        # NOTE: this might not work in the future since it uses a non static source
        self.assertEqual(testParams.__dict__["envList"], ["3.10", "3.11", "3.12"])
        self.assertEqual(
            testParams.__dict__["pgList"]["pgList"][0],
            "C:\\Users\\lars\\python_venvs\\packages\\logunittest",
        )

    def test_extend_runtime_cmd(self, *args, **kwargs):
        expected = [
            "pipenv",
            "run",
            "lut",
            "ut",
            "-c",
            "-m",
            '{"errors": "testErrors"}',
            "-i",
            "12345",
        ]
        toBeAdded = ["-m", json.dumps({"errors": "testErrors"}), "-i", "12345"]
        testParams = TestParams("test_tox.ini", *args, pgDir=sts.testDataDir, **kwargs)
        testParams.extend_runtime_cmd(toBeAdded, *args, **kwargs)
        # test that new testCmd is a list that now contains the added params
        self.assertEqual(testParams.testCmd, expected)
        # test that json string can be converted back to dict
        self.assertEqual(type(json.loads(testParams.testCmd[6])), dict)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
