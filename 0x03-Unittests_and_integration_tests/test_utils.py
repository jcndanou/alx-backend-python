#!/usr/bin/env python3
"""Test file for utils.py"""
import unittest
from unittest.mock import patch
from parameterized import parameterized
import utils


class TestAccessNestedMap(unittest.TestCase):
    """Classe de test pour la fonction access_nested_map."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected_result):
        """Teste que la fonction renvoie le bon résultat."""
        result = utils.access_nested_map(nested_map, path)
        self.assertEqual(result, expected_result)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_e(self, nested_map, path, expected_message):
        """Teste que KeyError est levée avec le bon message."""
        with self.assertRaises(KeyError) as cm:
            utils.access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), f"'{expected_message}'")


class TestGetJson(unittest.TestCase):
    """Classe de test pour la fonction get_json."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """
        Teste que get_json renvoie le bon résultat et fait bien un appel
        à requests.get.
        """
        mock_get.return_value.json.return_value = test_payload
        result = utils.get_json(test_url)
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Classe de test pour le décorateur memoize."""

    def test_memoize(self):
        """Teste que memoize cache bien le résultat."""
        class TestClass:
            """Classe de test pour memoize."""
            def a_method(self):
                """Méthode simple retournant 42."""
                return 42

            @utils.memoize
            def a_property(self):
                """Propriété décorée par memoize."""
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock_a_method:
            mock_a_method.return_value = 42
            test_instance = TestClass()
            result1 = test_instance.a_property()
            result2 = test_instance.a_property()
            mock_a_method.assert_called_once()
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            self.assertIs(result1, result2)
