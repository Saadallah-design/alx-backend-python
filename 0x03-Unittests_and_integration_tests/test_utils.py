#!/usr/bin/env python3
"""
Unit tests for utils module.

This module contains test cases for utility functions including
access_nested_map, get_json, and memoize decorator.
"""
import unittest
from parameterized import parameterized
from typing import Dict, Tuple, Any

from unittest.mock import patch, Mock
from utils import get_json
from utils import access_nested_map


class TestAccessNestedMap(unittest.TestCase):
    """
    Test cases for the access_nested_map function.

    This class tests the access_nested_map function with various
    nested dictionary structures and path sequences.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict,
        path: Tuple,
        expected: Any
    ) -> None:
        """
        Test that access_nested_map returns correct values for valid inputs.

        Args:
            nested_map: A nested dictionary structure to access
            path: A tuple of keys representing the path to traverse
            expected: The expected value to be returned

        Returns:
            None
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict,
        path: Tuple,
        expected_exception_message: str
    ) -> None:
        """
        Test that access_nested_map raises KeyError for invalid paths.

        Args:
            nested_map: A nested dictionary structure to access
            path: A tuple of keys representing an invalid path
            expected_exception_message: The expected error message

        Returns:
            None
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_exception_message}'")


class TestGetJson(unittest.TestCase):
    """
    Test cases for the get_json function.

    This class tests the get_json function to ensure it correctly
    fetches and returns JSON data from a given URL.
    this process is mocked to avoid actual HTTP requests.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url: str, test_payload: Dict[str, Any], mock_get: Mock) -> None:
        """
        Test that get_json returns the expected payload without making actual HTTP calls, using a mocked requests.get."""
        
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function under test
        result = get_json(test_url)

        # test that the mocked get method was called once with the correct URL
        mock_get.assert_called_once_with(test_url)

        # test that the result matches the expected payload
        self.assertEqual(result, test_payload)