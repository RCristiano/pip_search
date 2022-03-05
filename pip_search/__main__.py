import sys
from argparse import ArgumentParser

from . import __version__
from .pip_search import PipSearch

ap = ArgumentParser(
    prog="pip_search", description="Search for packages on PyPI"
)
ap.add_argument(
    "-s",
    "--sort",
    type=str,
    const="name",
    nargs="?",
    choices=["name", "version", "released"],
    help="sort results by package name, version or release date \
        (default: %(const)s)",
)
ap.add_argument(
    "query",
    nargs="*",
    type=str,
    help="terms to search pypi.org package repository",
)
ap.add_argument(
    "--version",
    action="version",
    version=f"%(prog)s {__version__}",
)
ap.add_argument(
    "--date_format",
    type=str,
    default="%b %-d, %Y",
    nargs="?",
    help="format for release date, (default: %(default)s)",
)
ap.add_argument(
    "--format",
    type=str,
    const="rich",
    nargs="?",
    choices=["rich", "plain", "json"],
    help="format for output, (default: %(const)s)",
    default="rich",
)


def main():
    args = ap.parse_args()
    if not args.query:
        ap.print_help()
        return 1
    ps = PipSearch()
    query = " ".join(args.query)
    package_set = ps.query(query)
    package_set.sort_by(args.sort)
    ps.render_set(package_set, query, args.format)


if __name__ == "__main__":
    sys.exit(main())
