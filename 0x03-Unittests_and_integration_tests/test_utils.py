#!/usr/bin/env python3
"""
Unit tests for utils module.

This module contains test cases for utility functions including
access_nested_map, get_json, and memoize decorator.
"""
import unittest
from parameterized import parameterized
from typing import Dict, Tuple, Any
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
