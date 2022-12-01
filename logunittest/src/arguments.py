"""
parses haimdall arguments
"""
import argparse


def mk_args():
    parser = argparse.ArgumentParser(
        description="run: python -m logunittest.src.logunittest info"
    )
    parser.add_argument(
        "action", metavar="action", nargs=None, help="see logunittest_code actions"
    )

    parser.add_argument(
        "-p",
        "--packageName",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help="default parameter to change",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        nargs="?",
        const=1,
        type=int,
        default=0,
        help="0:silent, 1:user, 2:debug",
    )

    parser.add_argument(
        "-y",
        "--yes",
        required=False,
        nargs="?",
        const=1,
        type=bool,
        default=None,
        help="run without confirm, not used",
    )

    return parser.parse_args()
