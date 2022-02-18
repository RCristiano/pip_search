from unittest import main, TestCase

from pip_search import PipSearch, Config


class TestPipSearch(TestCase):
    """Test the pip_search module"""

    def test_pip_search_not_implemented_api(self):
        class NotImplementedApiConfig(Config):
            api_url = "not_implemented"

        with self.assertRaises(NotImplementedError):
            self.ps = PipSearch(NotImplementedApiConfig())

    def test_query_for_nothing_return_a_empty_list(self):
        ps = PipSearch()
        self.assertEqual(list(ps.query("")), [])

    def test_query_for_return_self(self):
        ps = PipSearch()
        self.assertNotEqual(list(ps.query("pip_search")), [])


if __name__ == "__main__":
    main()
