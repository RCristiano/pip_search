from json import loads
from subprocess import run
from typing import Union

LOCAL_PIP_LIST = loads(
    run(
        ["pip", "list", "--format", "json"], capture_output=True
    ).stdout.decode("utf-8")
)


def check_version(package_name: str) -> Union[str, bool]:
    """Check if package is installed in local pip list
    Args:
        package_name (str): package name

    Returns:
        Union[str, bool]: version or False if not installed
    """
    return next(
        (lp["version"] for lp in LOCAL_PIP_LIST if lp["name"] == package_name),
        False,
    )
