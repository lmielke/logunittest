# info.py
import re
import logunittest.settings as sts
from logunittest.logunittest import Coverage
import colorama as color

color.init()


def main(*args, targetDir, **kwargs) -> None:
    found = Coverage()()
    match, stats = re.match('(<@>)(.*)(<@>)', found), str()
    if match:
        for i, m in enumerate(match.group(2).split('!')):
            stats += f'{m} '
            if i == 0:
                print(f"{color.Fore.WHITE}{m}{color.Style.RESET_ALL}", end=' ')
            elif re.search(r'err:0', m):
                print(f"{color.Fore.GREEN}{m}{color.Style.RESET_ALL}")
            elif re.search(r'err:[1-9][0-9]?', m):
                print(f"{color.Fore.RED}{m}{color.Style.RESET_ALL}")
            else:
                print(f"{color.Fore.YELLOW}{m}{color.Style.RESET_ALL}")
    if not stats:
        stats = 'no matching log found'
    return stats.strip()


if __name__ == "__main__":
    main()
