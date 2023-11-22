"""
    pararses logunittest arguments and keyword arguments
    args are provided by a function call to mk_args()
    
    RUN like:
    import logunittest.arguments
    kwargs.updeate(arguments.mk_args().__dict__)
"""
import argparse


def mk_args():
    parser = argparse.ArgumentParser(description="run: python -m logunittest info")
    parser.add_argument(
        "action", metavar="action", nargs=None, help="see logunittest_code actions"
    )

    parser.add_argument(
        "-n",
        "--pgName",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help="default parameter to change",
    )

    parser.add_argument(
        "-a",
        "--application",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help="alias you call the test package/application with, see .testlogs",
    )

    parser.add_argument(
        "-p",
        "--pgDir",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=".",
        help="package directory to be run",
    )

    parser.add_argument(
        "-m",
        "--comment",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help="comment provided by the user or calling function",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        nargs="?",
        const=1,
        type=int,
        default=1,
        help="0:silent, 1:user, 2:debug",
    )

    parser.add_argument(
        "-i",
        "--testId",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help="testId to group multiple tests together",
    )

    parser.add_argument(
        "-c",
        "--cleanup",
        required=False,
        nargs="?",
        const=True,
        type=bool,
        default=False,
        help="do cleanup outdated and overcounting logs, default is NOT to cleanup",
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
