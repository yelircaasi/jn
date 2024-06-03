from sys import argv

from .dispatcher import dispatch_from_arguments


def main() -> None:
    args = argv[1:]
    dispatch_from_arguments()
