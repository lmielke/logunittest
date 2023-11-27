# test_unittest.py
# general imports/libs
import colorama as color

color.init()
from contextlib import contextmanager
from datetime import datetime as dt
import json, os, re, shutil, sys
import subprocess

# internal module imports
import logunittest.settings as sts
import logunittest.logger as logger
import logunittest.sys_info as sys_info


class LogUnitTest:
    def __init__(self, *args, pgName=None, **kwargs) -> None:
        self.timeStamp = re.sub(r"([:. ])", r"-", str(dt.now()))
        self.testPackage = Package(*args, **kwargs)
        self.pyTest = False if self.testPackage.pgName == "logunittest" else True
        self.logDir, self.logContent = self._manage_log_dir(*args, **kwargs), dict()
        self.sysInfo = sys_info.SysInfo(*args, pgName=self.testPackage.pgName, **kwargs)
        self.numFails, self.comment, self.caller, self.callerVersion = 0, {}, None, None
        self.hasComment = self._handle_comments(*args, **kwargs)

    def _manage_log_dir(self, *args, logDir=None, **kwargs) -> str:
        if logDir is None:
            logDir = os.path.join(sts.get_testlogsdir(*args, **kwargs), self.testPackage.pgName)
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        else:
            logger.manage_logs(logDir, *args, **kwargs)
        return logDir

    def _handle_comments(self, *args, comment: str = None, **kwargs) -> bool:
        """
        Comments may be provided as runtime parameter from terminal like -m mycomment
        or they might be provided from a superset module like tox.py also using -m comment
        tox.py would use a json string to communicate installation status information
        those have to be extracted to be used in this module
        """
        converts = [self._to_dict, self._to_string]
        if comment:
            for convert in converts:
                try:
                    self.comment = convert(comment, *args, **kwargs)
                    return True
                except Exception as e:
                    print(f"LogUnitTest._handle_comments.Exception: {e}")
        return False

    def _to_dict(self, comment: str, *args, **kwargs) -> dict:
        loaded = json.loads(comment.strip())
        self.caller = list(loaded.keys())[0]
        self.callerVersion = list(loaded[self.caller].keys())[0]
        return loaded

    def _to_string(self, comment: str, *args, **kwargs) -> str:
        loaded = str(comment)
        if len(loaded) >= 1:
            return loaded
        else:
            raise


class UnitTestWithLogging(LogUnitTest):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pyVersion = self.get_runntime_version(*args, **kwargs)
        self.log = logger.mk_logger(self.logDir, self.logFileName, __name__, *args, **kwargs)

    @property
    def logFileName(self, *args, **kwargs):
        # logTime has no milliseconds
        return f"{sts.appName}_" f"{self.timeStamp.rsplit('-', 1)[0]}_py" f"{self.pyVersion}.log"

    def get_runntime_version(self, *args, **kwargs) -> str:
        sysVersion = sys.version.split(" ")[0].strip()
        if self.callerVersion is not None:
            if self.callerVersion[:4] != sysVersion[:4]:
                msg = (
                    f"Version mismatch, {self.caller}Version: {self.callerVersion[:4]} "
                    f"!= sysVersion: {sysVersion[:4]}"
                )
                self.comment[self.caller][self.callerVersion] += f"\n{msg}"
                print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
                return self.callerVersion
        return sysVersion

    def run_unittest(self, *args, **kwargs) -> None:
        """
        main unittest funciton which runs unittest using pipenv
        and logs the results in self.logDir
        """
        # pytest returns into stdout while unittest returns into stderr
        stdout, stderr = subprocess.Popen(
            sts.cmdsPt if self.pyTest else sts.cmdsUt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.testPackage.pgDir,
        ).communicate()
        if self.pyTest:
            return stdout.decode("utf-8")
        else:
            return stderr.decode("utf-8")

    def prep_log_results(self, results, *args, testId=None, comment=None, **kwargs):
        # log test results
        if self.pyTest:
            numTests, numOk, self.numFails = self.extract_stats_pytest(results)
        else:
            numTests, numOk, self.numFails = self.extract_stats_unittest(results)
        # prep log data
        self.logContent["head"] = (
            f"{self.testPackage.pgName}"
            f"\nunittest summary: [all:{numTests} ok:{numOk} err:{self.numFails}]"
        )
        # this info is added to the log latter after test is finished
        results = (
            "\n".join([l for l in results.replace("\r", "").replace("\n\n", "\n").split("\n")])
            + f"\n{sys.executable}"
        )
        self.logContent["sysInfo"] = f"{self.sysInfo.data.yaml_data}\n"
        self.logContent["stats"] = f"all:{numTests}\nok:{numOk}\nerr:{self.numFails}\n"
        self.logContent["results"] = f"\n{results}"
        if self.hasComment:
            caller = "typed comment" if self.caller is None else self.caller
            self.logContent["comment"] = f"{self.comment}"
        if testId is not None:
            self.logContent["testId"] = f"{testId}"
        self.log.info(self.logContent["head"])
        self.log.info(self.logContent["results"])

    def post_logging(self, *args, **kwargs):
        """
        logs undergo some post processing after the test is finished
        """
        logFilePath = os.path.join(self.logDir, self.logFileName)
        msg = self.check_logs(*args, **kwargs)
        if msg != "":
            logFilePath = self.rename_logs(msg, logFilePath, *args, **kwargs)
        self.log_results(logFilePath, *args, **kwargs)

    def log_results(self, logFilePath, *args, **kwargs):
        with open(logFilePath, "a") as f:
            # jsonStr = json.dumps(self.logContent, ensure_ascii=False)
            f.write("\n\n" + sts.logStart + "\n")
            json.dump(self.logContent, f, ensure_ascii=False)
            # f.write(jsonStr)

    def check_logs(self, *args, **kwargs):
        msg = str()
        if self.numFails != 0:
            msg += f"_test-err-{self.numFails}_"
        # logs have to be closed before renaming
        logger.close_logging(self.log)
        if self.caller == "logunittest.actions.tox":
            if self.comment[self.caller][self.callerVersion] != "OK":
                msg += "_tox-env-err_"
        return msg

    def rename_logs(self, msg, logFilePath, *args, **kwargs):
        """
        renames the log files to indicate errors
        """
        newLogFileName = self.logFileName.replace(".log", f"{msg}.log")
        newLogFilePath = os.path.join(self.logDir, newLogFileName)
        if os.path.exists(logFilePath):
            shutil.move(logFilePath, newLogFilePath)
        return newLogFilePath

    def extract_stats_pytest(self, results):
        # print(f"\nresults: {results}")
        # Regex pattern with optional non-capturing groups
        regexStr = r"(\d+) passed|(\d+) failed|(\d+) skipped"

        # Find all matches
        matches = re.findall(regexStr, results)
        # print(f"matches: {matches}")
        # Default values
        total = pass_count = fail_count = skip_count = 0

        # Sum up the counts
        for passed, failed, skipped in matches:
            if passed:
                pass_count += int(passed)
            if failed:
                fail_count += int(failed)
            if skipped:
                skip_count += int(skipped)

        total = pass_count + fail_count + skip_count

        # Format the output
        outStr = f"all:{total} ok:{pass_count} err:{fail_count}"
        # print(f"outStr: {outStr}")
        return total, pass_count, fail_count

    def extract_stats_unittest(self, results):
        """summerizes test results to add to the log header like [all:12 ok:11 err:1]
        NOTE: the log header is read by powershell, so treat with care
        """
        # print(f"\nresults: {results}")
        self.numFails, numTests, numOk = 0, 0, 0
        regex = r"(Ran )(\d{1,3})( tests?.*)"
        match = re.search(regex, results)
        # tet total number of tests
        # print(f"match: {match}")
        if match:
            numTests = match.group(2)
            if numTests.isnumeric():
                numTests = int(numTests)
        # get fails
        if "FAILED" in results:
            errRegex = r"(FAILED \(failures=|errors=)(\d{1,3})\)"
            errMatch = re.search(errRegex, results)
            if errMatch:
                self.numFails = errMatch.group(2)
                if self.numFails.isnumeric():
                    self.numFails = int(self.numFails)
        numOk = numTests - self.numFails
        return numTests, numOk, self.numFails


class Coverage(LogUnitTest):
    """
    gets unittest get_stats from logfile and returns it as a parsable string
    output can be used to display test status
    NOTE: this module is used by powershell to display test result in header
    HANDLE WITH CARE
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = re.compile(r"(\d\d-\d\d \d\d:\d\d)(.*)\n.*(\[.*\])", re.M)
        self.latest = ["Nothing", "Nothing"]

    def __call__(self, *args, **kwargs):
        sys.stderr.write(self.get_stats()[1])

    def get_stats(self, *args, testId=None, **kwargs) -> str:
        """
        loops all files.log in self.logDir from old to new and tries
        to find the test summary line using regex (self.regex)
        this ensures, that there is always the latest summary returned,
        however files.log which do not have a summary are ignared
        if a summary is found, its immmediately returned
        """
        stats = f"<@><{dt.today()}>!{'log not found'}<@>"
        if self.logDir is None or not os.path.exists(self.logDir):
            sys.stderr.write(stats)
        logFilePaths = reversed(self.get_sorted_logfiles())
        for i, logFilePath in enumerate(logFilePaths):
            # print(f"i: {i}, logFilePath: {logFilePath}")
            match, results = self.load_log_content(logFilePath, *args, **kwargs)
            if match:
                if testId is None:
                    return testId, match, results
                elif results.get("testId") == testId:
                    return results.get("testId"), match, results
            # msg = f"{color.Fore.RED}no match found in {logFilePath}{color.Style.RESET_ALL}"
            # assert match, msg
        return testId, stats, None

    def load_log_content(self, logFilePath, *args, **kwargs):
        with open(logFilePath, "r") as t:
            head, start, results = t.read().partition(sts.logStart)
        try:
            results = json.loads(results)
            match = self.match_test_output(head, *args, **kwargs)
        except:
            return None, {}
        return match, results

    def match_test_output(self, text, *args, **kwargs):
        """
        this is used to match the test output to the regex
        """
        match = re.search(self.regex, text)
        # print(f"<@>{match.group(1)}!{match.group(3)}<@>")
        if match:
            stats = f"<@>{match.group(1)}!{match.group(3)}<@>"
            self.latest = text.split("\n", 1)
            return stats

    def get_sorted_logfiles(self, *args, **kwargs):
        files = [
            os.path.join(self.logDir, f)
            for f in os.listdir(self.logDir)
            if re.match(r"^logunittest.*\.log$", f)
            and os.path.isfile(os.path.join(self.logDir, f))
        ]
        sorteds = sorted(files, reverse=False)
        return sorteds

    def main(self, *args, **kwargs):
        return self.get_stats()


class Package:
    """
    Contains relevant meta data about the package to be tested
    """

    def __init__(self, *args, **kwargs):
        self.pgDir = self.get_package_path(*args, **kwargs)
        self.pgName = self.get_package_name(*args, **kwargs)

    def get_package_path(self, *args, pgName: str = None, pgDir: str = None, **kwargs) -> str:
        if (pgDir is None or pgDir == ".") and pgName is None:
            pgDir = os.getcwd()
        elif pgName is not None:
            pgDir = os.path.expanduser(sts.availableApps.get(pgName)[1])
        return pgDir

    def get_package_name(self, *args, **kwargs):
        setupFile, match = os.path.join(self.pgDir, "setup.cfg"), None
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


# some helper functions come here
@contextmanager
def temp_chdir(*args, pgDir: str, **kwargs) -> None:
    """Sets the cwd within the context

    Args:
        pgDir (Path): The pgDir to the cwd

    Yields:
        None
    """

    origin = os.getcwd()
    try:
        os.chdir(pgDir)
        yield
    finally:
        os.chdir(origin)


def main(*args, **kwargs):
    with temp_chdir(*args, **kwargs):
        import logunittest.logger as logger

        test = UnitTestWithLogging(logger, *args, **kwargs)
        if test.log is not None:
            test.prep_log_results(test.run_unittest(*args, **kwargs), *args, **kwargs)
            test.post_logging(*args, **kwargs)


# if __name__ == "__main__":
#     main()
