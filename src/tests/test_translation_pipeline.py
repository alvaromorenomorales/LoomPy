"""Tests for the translation pipeline."""

import pytest
from hypothesis import given, strategies as st
from src.translation_pipeline import translate_json_values


def test_translate_simple_dict():
    """Test translation of a simple dictionary."""
    data = {"greeting": "Hola", "farewell": "Adiós"}
    
    def mock_translate(texts):
        translations = {"Hola": "Hello", "Adiós": "Goodbye"}
        return [translations.get(t, t) for t in texts]
    
    result = translate_json_values(data, mock_translate)
    
    assert result == {"greeting": "Hello", "farewell": "Goodbye"}


def test_translate_with_placeholders():
    """Test translation preserves placeholders."""
    data = {"message": "Hola {name}, tienes %s mensajes"}
    
    def mock_translate(texts):
        # Simulate translation that might reorder or modify text
        # but should preserve the placeholder tokens
        return [text.replace("Hola", "Hello").replace("tienes", "you have").replace("mensajes", "messages") for text in texts]
    
    result = translate_json_values(data, mock_translate)
    
    # Placeholders should be preserved
    assert "{name}" in result["message"]
    assert "%s" in result["message"]


def test_translate_nested_structure():
    """Test translation of nested JSON structure."""
    data = {
        "user": {
            "name": "Juan",
            "bio": "Desarrollador"
        },
        "items": ["manzana", "naranja"]
    }
    
    def mock_translate(texts):
        translations = {
            "Juan": "John",
            "Desarrollador": "Developer",
            "manzana": "apple",
            "naranja": "orange"
        }
        return [translations.get(t, t) for t in texts]
    
    result = translate_json_values(data, mock_translate)
    
    assert result["user"]["name"] == "John"
    assert result["user"]["bio"] == "Developer"
    assert result["items"][0] == "apple"
    assert result["items"][1] == "orange"


def test_translate_preserves_non_strings():
    """Test that non-string values are preserved."""
    data = {
        "text": "Hola",
        "number": 42,
        "float": 3.14,
        "bool": True,
        "null": None
    }
    
    def mock_translate(texts):
        return ["Hello"]
    
    result = translate_json_values(data, mock_translate)
    
    assert result["text"] == "Hello"
    assert result["number"] == 42
    assert result["float"] == 3.14
    assert result["bool"] is True
    assert result["null"] is None


def test_translate_empty_structure():
    """Test translation of empty structures."""
    # Empty dict
    result = translate_json_values({}, lambda texts: [])
    assert result == {}
    
    # Empty list
    result = translate_json_values([], lambda texts: [])
    assert result == []


def test_translate_no_strings():
    """Test translation when there are no strings."""
    data = {"number": 42, "items": [1, 2, 3]}
    
    def mock_translate(texts):
        # Should not be called
        raise AssertionError("Translate function should not be called")
    
    result = translate_json_values(data, mock_translate)
    
    assert result == data


def test_translate_root_string():
    """Test translation when root is a string."""
    data = "Hola mundo"
    
    def mock_translate(texts):
        return ["Hello world"]
    
    result = translate_json_values(data, mock_translate)
    
    assert result == "Hello world"


def test_translate_multiple_placeholders():
    """Test translation with multiple placeholders in one string."""
    data = {"message": "Hola {name}, tienes {count} mensajes de {sender}"}
    
    def mock_translate(texts):
        # Simulate translation that preserves placeholder tokens
        return [text.replace("Hola", "Hello").replace("tienes", "you have").replace("mensajes de", "messages from") for text in texts]
    
    result = translate_json_values(data, mock_translate)
    
    # All placeholders should be preserved
    assert "{name}" in result["message"]
    assert "{count}" in result["message"]
    assert "{sender}" in result["message"]


def test_translate_function_wrong_count():
    """Test error handling when translate function returns wrong count."""
    data = {"text1": "Hola", "text2": "Adiós"}
    
    def bad_translate(texts):
        # Return wrong number of translations
        return ["Hello"]  # Should return 2
    
    with pytest.raises(ValueError, match="returned 1 texts but expected 2"):
        translate_json_values(data, bad_translate)


def test_translate_does_not_modify_original():
    """Test that original data is not modified."""
    data = {"greeting": "Hola"}
    original_data = {"greeting": "Hola"}
    
    def mock_translate(texts):
        return ["Hello"]
    
    result = translate_json_values(data, mock_translate)
    
    # Original should be unchanged
    assert data == original_data
    # Result should be different
    assert result != data



class TestPropertyBasedNonStringValues:
    """Property-based tests for non-string value preservation in translation pipeline."""
    
    @given(
        json_data=st.recursive(
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text(min_size=0, max_size=50)
            ),
            lambda children: st.one_of(
                st.dictionaries(
                    keys=st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
                    values=children,
                    min_size=0,
                    max_size=5
                ),
                st.lists(children, min_size=0, max_size=5)
            ),
            max_leaves=20
        )
    )
    def test_non_string_values_unchanged_property(self, json_data):
        """
        **Feature: json-translator, Property 9: Non-string values unchanged**
        **Validates: Requirements 3.3**
        
        For any JSON structure containing non-string values (numbers, booleans, null),
        these values should be identical in all translated files.
        
        This test verifies that the full translation pipeline preserves all non-string
        values exactly as they appear in the source, without any modification.
        """
        # Extract all non-string values from the original structure
        original_non_strings = self._extract_non_string_values(json_data)
        
        # Mock translation function that modifies strings
        def mock_translate(texts):
            # Simulate translation by uppercasing all strings
            return [text.upper() if isinstance(text, str) else text for text in texts]
        
        # Translate the JSON data
        translated_data = translate_json_values(json_data, mock_translate)
        
        # Extract all non-string values from the translated structure
        translated_non_strings = self._extract_non_string_values(translated_data)
        
        # Verify that all non-string values are preserved exactly
        assert original_non_strings == translated_non_strings, \
            f"Non-string values were not preserved.\nOriginal: {original_non_strings}\nTranslated: {translated_non_strings}"
    
    def _extract_non_string_values(self, obj, path=()):
        """
        Recursively extract all non-string values from a JSON structure with their paths.
        
        Returns a set of (path, value, type) tuples representing all non-string values.
        We include the type to distinguish between None, False, 0, etc.
        """
        non_strings = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = path + (key,)
                if isinstance(value, str):
                    # Skip strings - they should be translated
                    pass
                elif isinstance(value, (dict, list)):
                    # Recursively extract from nested structures
                    non_strings.update(self._extract_non_string_values(value, new_path))
                else:
                    # This is a non-string primitive (int, float, bool, None)
                    # Store as (path, value, type) to handle None and bool correctly
                    # For floats, we need special handling due to NaN != NaN
                    if isinstance(value, float):
                        non_strings.add((new_path, value, 'float'))
                    else:
                        non_strings.add((new_path, value, type(value).__name__))
        
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                new_path = path + (index,)
                if isinstance(value, str):
                    # Skip strings - they should be translated
                    pass
                elif isinstance(value, (dict, list)):
                    # Recursively extract from nested structures
                    non_strings.update(self._extract_non_string_values(value, new_path))
                else:
                    # This is a non-string primitive (int, float, bool, None)
                    if isinstance(value, float):
                        non_strings.add((new_path, value, 'float'))
                    else:
                        non_strings.add((new_path, value, type(value).__name__))
        
        elif not isinstance(obj, str):
            # Root level non-string primitive
            if isinstance(obj, float):
                non_strings.add((path, obj, 'float'))
            else:
                non_strings.add((path, obj, type(obj).__name__))
        
        return non_strings
