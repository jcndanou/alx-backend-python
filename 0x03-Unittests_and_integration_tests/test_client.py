#!/usr/bin/env python3
"""Test file for client.py & fixtures.py."""
import unittest
from unittest.mock import patch, Mock, PropertyMock
from parameterized import parameterized, parameterized_class
import client
import fixtures


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient.org method."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org:
        1. Makes the right API call
        2. Returns correct result
        """
        test_payload = {
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
        }
        mock_get_json.return_value = test_payload

        github_client = client.GithubOrgClient(org_name)
        result = github_client.org

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """Test that _public_repos_url returns correct URL."""
        with patch.object(client.GithubOrgClient, 'org') as mock_org:
            mock_org.return_value = {
                "repos_url": "https://api.github.com/orgs/google/repos"
            }
            result = client.GithubOrgClient("google")._public_repos_url
            self.assertEqual(
                result,
                "https://api.github.com/orgs/google/repos"
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns correct repo list."""
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/google/repos"
            mock_get_json.return_value = [
                {"name": "repo1", "license": {"key": "mit"}},
                {"name": "repo2", "license": {"key": "apache-2.0"}}
            ]

            result = client.GithubOrgClient("test_org").public_repos()

            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/google/repos"
            )
            mock_url.assert_called_once()
            self.assertEqual(result, ["repo1", "repo2"])

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """Test has_license with different scenarios."""
        result = client.GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class([
    {
        "org_payload": fixtures.TEST_PAYLOAD[0][0],
        "repos_payload": fixtures.TEST_PAYLOAD[0][1],
        "expected_repos": fixtures.TEST_PAYLOAD[0][2],
        "apache2_repos": fixtures.TEST_PAYLOAD[0][3]
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""

    @classmethod
    def setUpClass(cls):
        """Set up test class with mock patcher."""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect_func(url):
            mock_response = Mock()
            a = cls.org_payload['login']
            if url == f"https://api.github.com/orgs/{a}":
                mock_response.json.return_value = cls.org_payload
            elif url == f"https://api.github.com/orgs/{a}/repos":
                mock_response.json.return_value = cls.repos_payload
            return mock_response

        cls.mock_get.side_effect = side_effect_func

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher."""
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        """Test public_repos integration."""
        a = self.org_payload['login']
        github_client = client.GithubOrgClient(a)
        result = github_client.public_repos()

        self.assertEqual(result, self.expected_repos)
        expected_calls = [
            unittest.mock.call(
                f"https://api.github.com/orgs/{a}"
            ),
            unittest.mock.call(
                f"https://api.github.com/orgs/{a}/repos"
            )
        ]
        self.mock_get.assert_has_calls(expected_calls)

    def test_public_repos_with_license(self):
        """
        Test the public_repos method with a license argument
        and ensure the result matches the expected value from the fixtures.
        """
        a = self.org_payload['login']
        github_client = client.GithubOrgClient(a)
        result = github_client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)
        expected_calls = [
            unittest.mock.call(
                f"https://api.github.com/orgs/{a}"
            ),
            unittest.mock.call(
                f"https://api.github.com/orgs/{a}/repos"
            )
        ]
        self.mock_get.assert_has_calls(expected_calls, any_order=True)
        self.mock_get.reset_mock()
