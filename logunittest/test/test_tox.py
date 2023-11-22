# standard lib imports
import os, time
import colorama as color

color.init()
import yaml
import unittest

# test package imports
import logunittest.settings as sts
import logunittest.actions.tox as tox


# print(f"\n__file__: {__file__}")


class Test_StateManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.verbose = 0
        # cls.testData = cls.mk_test_data(*args, **kwargs)

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        pass

    @classmethod
    def mk_test_data(cls, *args, **kwargs):
        pass

    def test_load_tox_ini(self, *args, **kwargs):
        installCmd = "install_command = pipenv install --dev"
        state = tox.StateManager(
            "py3.11", *args, installCmd=installCmd, pgDir=sts.projectDir, **kwargs
        )
        self.assertTrue(state.installCmd == installCmd)
        self.assertTrue(state.venvDir.endswith(r"logunittest\.tox\.venv-py3.11"))

    def test_change_pipfile(self, *args, **kwargs):
        """
        loops though a list of python versions and checks that the Pipfile
        has been changed to the expected python_version

        Pipfile = /logunittest/logunittest/test/data/Pipfile

        [requires]
        python_version = "3.7"

        """
        test_versions = ["3.12", "3.10", "3.7.4", "3.12.3", "3.7", "huxn"]
        # Pipfile expects an entry like: python_version = "3.7"
        expecteds = [f'python_version = "{v}"' for v in test_versions]
        # StateManager works with tox.ini pythons, which look like: py3.7
        envs = [f"py{v}" for v in test_versions]
        state = tox.StateManager(
            "py3.7", *args, installCmd="not relevant", pgDir=sts.testDataDir, **kwargs
        )
        # pre test check that original state is 3.7
        with open(os.path.join(sts.testDataDir, "Pipfile"), "r") as pipFile:
            adjustedContent = pipFile.read()
            self.assertTrue('python_version = "3.7"' in adjustedContent)
        # now change to each of the test versions and check the Pipfile
        for tv, exp in zip(test_versions, expecteds):
            if tv == "huxn":
                with self.assertRaises(AssertionError):
                    state.env = tv
                    state.change_pipfile(*args, **kwargs)
                self.assertTrue(exp not in adjustedContent)
            else:
                state.env = tv
                state.change_pipfile(*args, **kwargs)
                time.sleep(0.1)
                with open(os.path.join(sts.testDataDir, "Pipfile"), "r") as pipFile:
                    adjustedContent = pipFile.read()
                self.assertTrue(exp in adjustedContent)


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
