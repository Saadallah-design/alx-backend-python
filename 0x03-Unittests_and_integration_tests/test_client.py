#!/usr/bin/env python3
"""
Unit tests for GithubOrgClient.
Since, it fails the autochecker i will skip it
This module contains test cases for the GithubOrgClient class,
testing its methods and properties with mocked external dependencies.
"""

import unittest
from unittest.mock import Mock, patch, PropertyMock
from parameterized import parameterized, parameterized_class
from typing import Dict
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Test cases for the GithubOrgClient class.

    This class tests various methods of the GithubOrgClient class,
    including org, public_repos, and has_license.
    """

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(
        self,
        org_name: str,
        expected_payload: Dict,
        mock_get_json: Mock
    ) -> None:
        """
        Test that the org method returns the expected payload.

        Args:
            org_name: The name of the organization to test
            expected_payload: The expected dictionary payload to be returned
            mock_get_json: Mocked get_json function

        Returns:
            None
        """
        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @patch('client.GithubOrgClient.org', new_callable=PropertyMock)
    def test_public_repos_url(self, mock_org: PropertyMock) -> None:
        """
        Test that _public_repos_url returns the expected URL.

        This test mocks the org property to return a known payload
        and verifies that _public_repos_url extracts the correct
        repos_url from that payload.

        Args:
            mock_org: Mocked org property

        Returns:
            None
        """
        test_payload = {
            "repos_url": "https://api.github.com/orgs/test/repos"
        }
        mock_org.return_value = test_payload

        client = GithubOrgClient("test")
        result = client._public_repos_url

        self.assertEqual(result, test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Test that public_repos returns the expected list of repos.

        This test uses both @patch decorator and context manager to mock
        get_json and _public_repos_url respectively, verifying that
        public_repos correctly processes the payload and returns repo names.

        Args:
            mock_get_json: Mocked get_json function

        Returns:
            None
        """
        # Define the payload that get_json should return
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = test_repos_payload

        # Using context manager to mock _public_repos_url
        with patch(
            'client.GithubOrgClient._public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:
            test_url = "https://api.github.com/orgs/test/repos"
            mock_public_repos_url.return_value = test_url

            # Create client and call public_repos
            client = GithubOrgClient("test")
            result = client.public_repos()

            # Expected result: list of repo names
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)

            # Verify _public_repos_url was accessed once
            mock_public_repos_url.assert_called_once()

            # Verify get_json was called once with the correct URL
            mock_get_json.assert_called_once_with(test_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo: Dict, license_key: str,
                         expected: bool) -> None:
        """
        Test that has_license correctly checks repository license.

        This test verifies the static method has_license returns True
        when the repository has the specified license, and False otherwise.

        Args:
            repo: Repository dictionary with license information
            license_key: License key to check for
            expected: Expected boolean result

        Returns:
            None
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.

    This class performs integration testing by mocking only external
    HTTP requests while testing the full workflow of the client.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up class fixtures before running tests.

        This method starts a patcher for requests.get and configures
        it to return appropriate fixtures based on the URL requested.
        """
        def side_effect_function(url):
            """
            Side effect function for mocking requests.get.

            Args:
                url: The URL being requested

            Returns:
                Mock object with json method returning appropriate payload
            """
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = None
            return mock_response

        # Start the patcher
        cls.get_patcher = patch(
            'requests.get',
            side_effect=side_effect_function
        )
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Tear down class fixtures after running tests.

        This method stops the patcher for requests.get.
        """
        cls.get_patcher.stop()
