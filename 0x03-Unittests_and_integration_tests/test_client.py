#!/usr/bin/env python3
"""
Unit tests for GithubOrgClient.

This module contains test cases for the GithubOrgClient class,
testing its methods and properties with mocked external dependencies.
"""

import unittest
from unittest.mock import Mock, patch, PropertyMock
from parameterized import parameterized
from typing import Dict
from client import GithubOrgClient


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
