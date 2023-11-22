# logger.py
import os, re, time
import logging
from datetime import datetime as dt
import logunittest.settings as sts
import colorama as color

color.init()


def mk_logger(logDir, fileName, loggerName, *args, createLog=True, **kwargs):
    # logging config to put somewhere before calling functions
    # call like: logger.debug(f"logtext: {anyvar}")
    if not createLog:
        return None
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.INFO)
    logformat = "%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s"
    datefmt = "%m-%d %H:%M"
    logForm = logging.Formatter(fmt=logformat, datefmt=datefmt)
    logPath = os.path.join(logDir, fileName)
    logHandler = logging.FileHandler(logPath, mode="a")
    logHandler.setFormatter(logForm)
    logger.addHandler(logHandler)
    return logger


def manage_logs(logDir, *args, cleanup=False, **kwargs) -> None:
    """
    checks if number of logs or age of logs exceeds threshold
    NOTE: warnings will only be issued on verbose -v
    """
    if cleanup:
        remove_logs(logDir, sts.logPreserveThreshold, *args, **kwargs)
    else:
        issue_warnings(logDir, sts.logPreserveThreshold, *args, **kwargs)


def issue_warnings(logDir: str, threshold: dict, *args, **kwargs) -> None:
    if sts.verbose >= 2 and threshold["count"] is not None:
        files = os.listdir(logDir)
        if len(files) > threshold["count"] * sts.warningTolerance:
            print(
                f"{color.Fore.YELLOW}",
                f"WARNING: {len(files)} logfiles found in {logDir} !\n",
                f" Use -c to cleanup !{color.Style.RESET_ALL}",
            )
    elif sts.verbose >= 2 and threshold["days"] is not None:
        fileAge = dt.now().day - dt.fromtimestamp(os.path.getctime(file)).day
        if fileAge > threshold["days"] * sts.warningTolerance:
            print(
                f"{color.Fore.YELLOW}",
                f"WARNING: logfiles in {logDir} are older {threshold['days']} days !\n",
                f" Use -c to cleanup !{color.Style.RESET_ALL}",
            )


def remove_logs(logDir: str, threshold: dict, *args, **kwargs) -> None:
    """
    Scans the logDir and removes all logfiles that excede the threshold
    as defined in sts.logPreserveThreshold
    example: sts.logPreserveThreshold = {"days": 30, "count": None}
    NOTE: This runs at the beginning of the test, so you will end up having more than what
    is defined by the threshold. This is because the logfiles are created during the test.
    NOTE: if sts.warningTolerance is set to value != 1 then warnings will always appear
    """
    for i, file in enumerate(sorted(os.listdir(logDir), reverse=True)):
        if file.endswith(".log"):
            file = os.path.join(logDir, file)
            if threshold["count"] is not None:
                if i + 1 > threshold["count"]:
                    os.remove(file)
            elif threshold["days"] is not None:
                fileAge = dt.now().day - dt.fromtimestamp(os.path.getctime(file)).day
                if fileAge > threshold["days"]:
                    time.sleep(1)
                    os.remove(file)


def close_logging(log, *args, **kwargs):
    handlers = log.handlers[:]
    for handler in handlers:
        handler.close()
        log.removeHandler(handler)
