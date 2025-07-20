#!/usr/bin/env python3
""" Test file for client.py & fixtures.py """
import unittest
import client
import fixtures
from unittest.mock import patch, Mock
from parameterized import parameterized, parameterized_class


class TestGithubOrgClient(unittest.TestCase):
    """ Tests for GithubOrgClient.org method """

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """ Test que GithubOrgClient.org:
        1. Fait bien l'appel à get_json avec la bonne URL
        2. Retourne le bon résultat """

        mock_get_json.return_value = {"login": org_name, "id": 123, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"}
        github_client = client.GithubOrgClient(org_name)
        result = github_client.org
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, {"login": org_name, "id": 123, "repos_url": f"https://api.github.com/orgs/{org_name}/repos"})

    def test_public_repos_url(self):
        """ Test que _public_repos_url retourne la bonne URL """

        with unittest.mock.patch('client.GithubOrgClient.org', new_callable=unittest.mock.PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "https://api.github.com/orgs/test_org/repos"}
            result = client.GithubOrgClient("test_org")._public_repos_url
            self.assertEqual(result, "https://api.github.com/orgs/test_org/repos")

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test que public_repos retourne la bonne liste de dépôts"""
        
        with patch('client.GithubOrgClient._public_repos_url', new_callable=client.PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = "https://api.github.com/orgs/test_org/repos"
            mock_get_json.return_value = [
                {"name": "repo1", "license": {"key": "mit"}}, 
                {"name": "repo2", "license": {"key": "apache-2.0"}}
            ]
            
            result = client.GithubOrgClient("test_org").public_repos()
            
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/test_org/repos")
            mock_public_repos_url.assert_called_once()
            self.assertEqual(result, ["repo1", "repo2"])
    
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """Test la méthode has_license dans différents scénarios"""
        result = client.GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected_result)


@parameterized_class([
    {
        "org_payload": fixtures.org_payload,
        "repos_payload": fixtures.repos_payload,
        "expected_repos": fixtures.expected_repos,
        "apache2_repos": fixtures.apache2_repos
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Tests d'intégration pour GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Configure le mock pour requests.get"""

        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect_func(url):
            mock_response = Mock()
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                mock_response.json.return_value = cls.org_payload
            elif url == f"https://api.github.com/orgs/{cls.org_payload['login']}/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}
            return mock_response

        cls.mock_get.side_effect = side_effect_func

    @classmethod
    def tearDownClass(cls):
        """Arrête le patcher"""
        cls.get_patcher.stop()

    def test_public_repos_integration(self):
        """Test d'intégration de public_repos"""

        github_client = client.GithubOrgClient(self.org_payload['login'])
        result = github_client.public_repos()
        self.assertEqual(result, self.expected_repos)
        expected_calls = [
            unittest.mock.call(f"https://api.github.com/orgs/{self.org_payload['login']}"),
            unittest.mock.call(f"https://api.github.com/orgs/{self.org_payload['login']}/repos")
        ]
        self.mock_get.assert_has_calls(expected_calls)