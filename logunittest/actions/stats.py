# stats.py
import re
import logunittest.settings as sts
from logunittest.logunittest import Coverage
import colorama as color

color.init()


def main(*args, pgDir=None, **kwargs) -> None:
    c = Coverage()
    testId, header, _ = c.get_stats(*args, **kwargs)
    match = re.match("(<@>)(.*)(<@>)", header)
    stats = evaluate_match(match, *args, **kwargs)
    return stats


def evaluate_match(match, *args, **kwargs):
    if not match:
        stats = "no matching log found"
    else:
        stats = str()
        for i, m in enumerate(match.group(2).split("!")):
            stats += f"{m} "
    if sts.verbose >= 2:
        colorized_print(stats, *args, **kwargs)
    return stats.strip()


def colorized_print(stats, *args, **kwargs):
    if re.search(r"err:0", stats):
        print(f"{color.Fore.GREEN}{stats}{color.Style.RESET_ALL}")
    elif re.search(r"err:[1-9][0-9]?", stats):
        print(f"{color.Fore.RED}{stats}{color.Style.RESET_ALL}")
    else:
        print(f"{color.Fore.YELLOW}{stats}{color.Style.RESET_ALL}")


if __name__ == "__main__":
    main()
