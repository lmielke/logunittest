# info.py
import logunittest.settings as sts
from logunittest.logunittest import Package, Coverage
import subprocess
import os, re, sys
import configparser

import colorama as color

color.init()


def get_logs(*args, testId: str = None, **kwargs) -> list:
    cov = Coverage()
    testId = testId if testId is not None else get_log_results(cov, *args, **kwargs)
    if testId is None:
        print(f"{color.Fore.RED}No testId provided and no logs found!{color.Style.RESET_ALL}")
        return None
    logs = get_logs_by_logId(cov, *args, testId=testId, **kwargs)
    if logs:
        show_results(logs, *args, **kwargs)
        return list(logs.keys())
    else:
        return None


def get_logs_by_logId(cov, *args, testId: str = None, logDir: str = None, **kwargs) -> dict:
    logs = dict()
    for _dir, dirs, files in os.walk(sts.defaultLogDir if logDir is None else logDir):
        for file in files:
            logPath = os.path.join(_dir, file)
            with open(logPath, "r") as f:
                logContent = f.read()
            if testId in logContent:
                match, results = cov.load_log_content(*args, logFilePath=logPath, **kwargs)
                logs[logPath] = results
    return logs


def get_log_results(cov, *args, logPath: str = None, **kwargs) -> str:
    logPath = logPath if logPath is not None else cov.get_sorted_logfiles(*args, **kwargs)[-1]
    match, results = cov.load_log_content(*args, logFilePath=logPath, **kwargs)
    return results.get("testId")


def show_results(logs: dict, *args, verbose: int = 0, **kwargs) -> None:
    """
    prints log file Names and/or content based on choosen verbosity level
    """
    if verbose >= 2:
        for i, (k, vs) in enumerate(logs.items()):
            msg = f"\n{i} - {k}"
            if "err" in k:
                print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
            else:
                print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")
            if verbose >= 3:
                for p, v in vs.items():
                    print(f"\t{p}: {v}")


def main(*args, **kwargs):
    return get_logs(*args, **kwargs)


if __name__ == "__main__":
    main()
