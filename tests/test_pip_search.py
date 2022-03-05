import json
from unittest import TestCase, main

from pip_search import Config, Package, PackageSet, PipSearch


class TestPipSearch(TestCase):
    """Test the pip_search module"""

    def setUp(self) -> None:
        self.ps = PipSearch()

    def test_pip_search_not_implemented_api(self):
        class NotImplementedApiConfig(Config):
            api_url = "not_implemented"

        with self.assertRaises(NotImplementedError):
            PipSearch(NotImplementedApiConfig())

    def test_query_return_is_a_pacakgeset(self):
        pkgs_result = self.ps.query("pip-search")
        self.assertIsInstance(pkgs_result, PackageSet)

    def test_query_for_nothing_return_a_empty_list(self):
        self.assertEqual(list(self.ps.query("")), [])

    def test_query_for_return_self(self):
        pkgs_result = list(self.ps.query("pip-search"))
        pip_search = [pkg for pkg in pkgs_result if pkg.name == "pip-search"]
        self.assertIsInstance(pip_search[0], Package)
        self.assertEqual(len(pip_search), 1)

    def test_json_format_return_a_string(self):
        pkgs_result = self.ps.query("pip-search")
        self.assertIsInstance(pkgs_result.json(), str)

    def test_json_format_return_a_valid_empty_list_json(self):
        pkgs_result = self.ps.query("")
        self.assertEqual(pkgs_result.json(), json.dumps([]))

    def test_json_format_return_a_valid_json(self):
        pkgs_result = self.ps.query("pip-search")
        expected_json = json.dumps([vars(pkg) for pkg in list(pkgs_result)])
        self.assertEqual(pkgs_result.json(), expected_json)


if __name__ == "__main__":
    main()
