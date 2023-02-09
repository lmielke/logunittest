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
        "--packageAlias",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help="alias you call the future package with, if left blank pgName[:6] is used",
    )

    parser.add_argument(
        "-p",
        "--targetDir",
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
        help="if tested suceessfully, the package can be pushed to git with a comment",
    )

    parser.add_argument(
        "-py",
        "--python_version",
        required=False,
        nargs=None,
        const=None,
        type=str,
        default=None,
        help='overwrite python_version = "3.11" with your desired target version, i.e. 3.9"',
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
        "-g",
        "--git_sync",
        required=False,
        nargs="?",
        const=1,
        type=bool,
        default=None,
        help="run git_sync after testing",
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
