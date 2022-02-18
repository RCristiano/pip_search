from abc import ABC, abstractmethod
import json
from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import Any, Iterable, Iterator, List
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup, Tag
from rich.console import Console as RichConsole
from rich.table import Table as RichTable

from .utils import check_version


class Config:
    """Configuration class"""

    api_url: str = "https://pypi.org/search/"
    page_size: int = 2
    sort_by: str = "name"
    date_format: str = "%b %-d, %Y"
    link_default_format: str = "https://pypi.org/project/{package.name}"
    api_released_date_format: str = "%Y-%m-%dT%H:%M:%S%z"


config = Config()


@dataclass
class Package:
    """Package class"""

    name: str
    version: str
    released: str = None
    description: str = None
    link: InitVar[str] = None

    def __post_init__(self, link: str = None) -> None:
        self.link = link or config.link_default_format.format(package=self)
        self.released_date = (
            datetime.strptime(self.released, config.api_released_date_format)
            if self.released
            else None
        )


class PackageSet(Iterable[Package]):
    """PackageSet class"""

    def __init__(self, packages: List[Package]) -> None:
        self.packages = packages
        self.packages = packages

    def __iter__(self) -> Iterator[Package]:
        return iter(self.packages)

    def sort_by(self, sort_by: str = None) -> None:
        """Sort packages by name, version or released date

        Args:
            sort_by (str): Sort by name, version or released date
            (default: None)
        """
        if sort_by == "name":
            self.packages.sort(key=lambda p: p.name.lower())
        elif sort_by == "released":
            self.packages.sort(key=lambda p: p.released_date)
        elif sort_by == "version":
            from pkg_resources import parse_version

            self.packages.sort(key=lambda p: parse_version(p.version))
        elif sort_by is not None:
            raise ValueError(f"Invalid sort_by: {sort_by}")

    @property
    def json(self) -> str:
        """Return package list as json string

        Returns:
            str: json string
        """
        return json.dumps([pkg.__dict__ for pkg in list(self.packages)])


class BaseAPI(ABC):
    """Base API class"""

    @abstractmethod
    def search(self, query: str) -> Iterator:
        """Search API for packages

        Args:
            query (str): query string

        Returns:
            Iterator: Iterator of search results
        """

    @abstractmethod
    def parser(self, item: Any) -> Package:
        """Parser for search results from API response item

        Args:
            item (Any): item from API response

        Returns:
            Package: package object
        """


class PyPiAPI(BaseAPI):
    """PyPi API class"""

    def __init__(self, config: Config = None) -> None:
        self.config = config or Config()

    def parser(self, item: Tag) -> Package:
        """Parser for search results from API response item

        Args:
            item (Tag): item from API response

        Returns:
            Package: package object
        """
        link = urljoin(config.api_url, item.get("href"))
        package = item.select_one('span[class*="name"]').text.strip()
        version = item.select_one('span[class*="version"]').text.strip()
        released = item.select_one('span[class*="released"]').find("time")[
            "datetime"
        ]
        description = item.select_one('p[class*="description"]').text.strip()
        return Package(package, version, released, description, link)

    def search(self, query: str = None) -> Iterator[Tag]:
        """Search for packages on pypi

        Args:
            query (str, optional): Query string (default: None)

        Returns:
            Iterator[Tag]: Iterator of search results snippets
        """
        for page in range(1, self.config.page_size + 1):
            params = {"q": query, "page": page}
            r = requests.get(self.config.api_url, params=params)
            soup = BeautifulSoup(r.text, "html.parser")
            yield from soup.select('a[class*="snippet"]')


class PipSearch:
    """PipSearch class"""

    def __init__(self, config: Config = config):
        self.config = config
        if self.config.api_url == "https://pypi.org/search/":
            self.api = PyPiAPI(self.config)
        else:
            raise NotImplementedError(
                "Currently only PyPi API is supported, "
                "but you can contribute to add support for other APIs"
            )

    def query(self, query: str) -> PackageSet:
        """Search for packages matching the query

        Args:
            query (str): query string

        Returns:
            PackageSet: package set
        """
        return PackageSet(
            [self.api.parser(snippet) for snippet in self.api.search(query)]
        )

    def render_set(
        self, package_set: PackageSet, query: str, format: str = "rich"
    ) -> None:
        """Render package set

        Args:
            format (str, optional): Format for output (default: "rich")
        """
        if format == "rich":
            _rich_table(package_set, query, self.config)
        elif format == "json":
            print(package_set.json)


def local_packages(self) -> PackageSet:
    """Search for local packages

    Returns:
        PackageSet: package set
    """
    from subprocess import run

    pip_command = ["pip", "list", "--format", "json"]
    local_pip_list = json.loads(
        run(pip_command, capture_output=True).stdout.decode("utf-8")
    )
    self.package_set = PackageSet([Package(**pkg) for pkg in local_pip_list])
    return self.package_set


def _rich_table(
    package_set: PackageSet, query: str, config: Config = config
) -> RichTable:
    """Return a RichTable object

    Args:
        package_set (PackageSet): Package set
        config (Config, optional): Configuration object (default: config)

    Returns:
        Table: RichTable object with package set data as rows and columns as
               headers (name, version, released, Description) and links
    """
    table = RichTable(
        title=(
            "[not italic]:snake:[/] [bold][magenta]"
            f"{config.api_url}?{urlencode({'q': query})}"
            "[/] [not italic]:snake:[/]"
        )
    )
    table.add_column("Package", style="cyan", no_wrap=True)
    table.add_column("Version", style="bold yellow")
    table.add_column("Released", style="bold green")
    table.add_column("Description", style="bold blue")
    emoji = ":open_file_folder:"
    for package in package_set:
        checked_version = check_version(package.name)
        if checked_version == package.version:
            package.version = f"[bold cyan]{package.version} ==[/]"
        elif checked_version is not False:
            package.version = (
                f"{package.version} > [bold purple]{checked_version}[/]"
            )
        table.add_row(
            f"[link={package.link}]{emoji}[/link] {package.name}",
            package.version,
            package.released_date.strftime(config.date_format),
            package.description,
        )
    RichConsole().print(table)
