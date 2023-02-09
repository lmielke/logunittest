# test_unittest.py
#
from datetime import datetime as dt
import os, re, sys
import subprocess
from contextlib import contextmanager
import logunittest.settings as sts
import logunittest.logger as logger


class UnitTestWithLogging:
    def __init__(self, *args, **kwargs) -> None:
        self.pgPath, self.pgName = get_package(*args, **kwargs)
        self.timeStamp = re.sub(r"([:. ])", r"-", str(dt.now()))
        self.logDir = self.mk_log_dir(*args, **kwargs)
        # self.logDir = Coverage.get_log_dir(self.pgName, **kwargs)
        assert os.path.isdir(self.logDir), f"logDir: {self.logDir} does not exist !"
        self.logDefaultName = f"{os.path.basename(__file__)[:-3]}_{self.timeStamp}.log"
        self.log = logger.mk_logger(self.logDir, self.logDefaultName, __name__)

    def mk_log_dir(self, *args, **kwargs) -> str:
        logDir = os.path.join(sts.testLogsDir, self.pgName)
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        return logDir

    def run_unittest(self, *args, **kwargs) -> None:
        """
        main unittest funciton which runs unittest using pipenv
        and logs the results in self.logDir
        Note: a logDir must exist in the package directory to be tested
        """
        if not os.path.exists(self.logDir):
            raise Exception(f"Unknow logDir: {self.logDir}! Check {self.pgPath} !")
        cmds = ["pipenv", "run", "python", "-m", "unittest"]
        results = (
            subprocess.Popen(cmds, stderr=subprocess.PIPE, cwd=self.pgPath)
            .stderr.read()
            .decode("utf-8")
        )
        summary = self.extract_stats(results)
        body = results.replace("\r", "").replace("\n\n", "\n")
        results = "\n".join([l for l in body.split("\n")])
        results += f"\n{sys.executable}"
        self.log.info(f"{summary}\n{results}")

    def extract_stats(self, results):
        """summerizes test results to add to the log header like [all:12 ok:11 err:1]
        NOTE: the log header is read by powershell, so treat with care
        """
        numFails, numTests, numOk = 0, 0, 0
        regex = r"(Ran )(\d{1,3})( tests?.*)"
        match = re.search(regex, results)
        # tet total number of tests
        if match:
            numTests = match.group(2)
            if numTests.isnumeric():
                numTests = int(numTests)
        # get fails
        if "FAILED" in results:
            errRegex = r"(FAILED \(failures=|errors=)(\d{1,3})\)"
            errMatch = re.search(errRegex, results)
            if errMatch:
                numFails = errMatch.group(2)
                if numFails.isnumeric():
                    numFails = int(numFails)
        numOk = numTests - numFails
        return f"{self.pgName} summary: [all:{numTests} ok:{numOk} err:{numFails}]"


class Coverage:
    """
    gets unittest get_stats from logfile and returns it as a parsable string
    output can be used to display test status
    NOTE: this module is used by powershell to display test result in header
    HANDLE WITH CARE
    """

    def __init__(self, *args, logDir: str = None, **kwargs):
        self.pgPath, self.pgName = get_package(*args, **kwargs)
        self.logDir = os.path.join(os.path.expanduser("~/.testlogs"), self.pgName)
        # self.logDir = Coverage.get_log_dir(self.pgName, **kwargs)
        self.regex = r"([0-9 :-]*)( INFO logunittest .* summary: )(\[.*\])"
        self.latest = ["Nothing", "Nothing"]

    def __call__(self, *args, **kwargs):
        sys.stderr.write(self.get_stats())

    @staticmethod
    def get_log_dir(pgName=None, *args, **kwargs) -> str:
        """uses a keyfile such as setup.cfg to derrive
        the location of the log files directory
        the log files dir has a fixed position relative to the key files
        returns the full path to the log files directory
        """
        projectKeyFile, packageKeyFile = "setup.cfg", "__main__.py"
        files = os.listdir()
        if not projectKeyFile in files and not packageKeyFile in files:
            return None
        elif projectKeyFile in files:
            logDir = os.path.join(os.getcwd(), pgName, "test", "logs")
        elif packageKeyFile in files:
            logDir = os.path.join(os.getcwd(), "test", "logs")
        return logDir

    def get_stats(self, *args, **kwargs) -> str:
        """
        loops all files.log in self.logDir from old to new and tries
        to find the test summary line using regex (self.regex)
        this ensures, that there is always the latest summary returned,
        however files.log which do not have a summary are ignared
        if a summary is found, its immmediately returned
        """
        default = f"<@><{dt.today()}>!{'logdir not found'}<@>"
        if self.logDir is None or not os.path.exists(self.logDir):
            sys.stderr.write(default)
        logFilePaths = self.get_sorted_logfiles()
        for logFilePath in logFilePaths:
            with open(logFilePath, "r") as t:
                text = t.read()
                match = re.search(self.regex, text)
            if match:
                stats = f"<@>{match.group(1)}!{match.group(3)}<@>"
                self.latest = text.split("\n", 1)
                break
        else:
            stats = default
        # sys.stderr.write(stats)
        return stats

    def get_sorted_logfiles(self, *args, **kwargs):
        files = [
            os.path.join(self.logDir, f)
            for f in os.listdir(self.logDir)
            if re.match(r"^logunittest.*\.log$", f)
            and os.path.isfile(os.path.join(self.logDir, f))
        ]
        sorteds = sorted(files, key=os.path.getctime, reverse=True)
        return sorteds

    def main(self, *args, **kwargs):
        return self.get_stats()


def get_package(*args, pgPath: str = None, **kwargs) -> str:
    pgPath = get_package_path(*args, pgPath, **kwargs)
    pgName = get_package_name(*args, pgPath=pgPath, **kwargs)
    return pgPath, pgName


def get_package_path(*args, pgName: str = None, pgPath: str = None, **kwargs) -> str:
    if (pgPath is None or pgPath == ".") and pgName is None:
        pgPath = sts.unalias_path(".")
    elif pgName is not None:
        pgPath = os.path.expanduser(sts.availableApps.get(pgName)[1])
    return pgPath


def get_package_name(*args, pgPath: str = None, **kwargs):
    setupFile, match = os.path.join(pgPath, "setup.cfg"), None
    if os.path.exists(setupFile):
        with open(setupFile, "r") as s:
            setupText = s.read()
        match = re.search(r"(name = )(.*)", setupText)
    else:
        msg = f"File not found: {setupFile}"
    if match:
        out = match.group(2)
        return out
    else:
        raise Exception(
            f"logunittest.UnitTestWithLogging.get_package_path, "
            f"Package name could not be derrived! "
            f"\n{msg}"
        )


@contextmanager
def temp_chdir(*args, pgPath: str, **kwargs) -> None:
    """Sets the cwd within the context

    Args:
        pgPath (Path): The pgPath to the cwd

    Yields:
        None
    """

    origin = os.getcwd()
    pgPath = sts.unalias_path(workPath=pgPath)
    try:
        os.chdir(pgPath)
        yield
    finally:
        os.chdir(origin)


def ut(*args, **kwargs):
    with temp_chdir(*args, **kwargs):
        import logunittest.logger as logger

        UnitTestWithLogging(logger, *args, **kwargs).run_unittest(*args, **kwargs)


if __name__ == "__main__":
    ut()
