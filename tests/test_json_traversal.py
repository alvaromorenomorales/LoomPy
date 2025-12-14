"""Unit tests for JSON traversal utilities."""

import pytest
from hypothesis import given, strategies as st
from src.json_traversal import collect_string_paths, set_by_path


class TestCollectStringPaths:
    """Tests for collect_string_paths function."""
    
    def test_simple_dict_with_strings(self):
        """Test extracting strings from a simple dictionary."""
        data = {"name": "John", "city": "Madrid"}
        result = collect_string_paths(data)
        
        assert len(result) == 2
        assert (('name',), 'John') in result
        assert (('city',), 'Madrid') in result
    
    def test_dict_with_mixed_types(self):
        """Test that only strings are extracted, other types ignored."""
        data = {
            "name": "John",
            "age": 30,
            "height": 1.75,
            "active": True,
            "notes": None
        }
        result = collect_string_paths(data)
        
        assert len(result) == 1
        assert (('name',), 'John') in result
    
    def test_nested_objects(self):
        """Test extracting strings from nested objects."""
        data = {
            "user": {
                "name": "John",
                "address": {
                    "city": "Madrid",
                    "country": "Spain"
                }
            }
        }
        result = collect_string_paths(data)
        
        assert len(result) == 3
        assert (('user', 'name'), 'John') in result
        assert (('user', 'address', 'city'), 'Madrid') in result
        assert (('user', 'address', 'country'), 'Spain') in result
    
    def test_arrays_with_strings(self):
        """Test extracting strings from arrays."""
        data = {"items": ["apple", "banana", "cherry"]}
        result = collect_string_paths(data)
        
        assert len(result) == 3
        assert (('items', 0), 'apple') in result
        assert (('items', 1), 'banana') in result
        assert (('items', 2), 'cherry') in result
    
    def test_arrays_with_mixed_types(self):
        """Test that only strings are extracted from arrays."""
        data = {"values": ["text", 42, True, None, "another"]}
        result = collect_string_paths(data)
        
        assert len(result) == 2
        assert (('values', 0), 'text') in result
        assert (('values', 4), 'another') in result
    
    def test_nested_arrays_and_objects(self):
        """Test complex nested structures."""
        data = {
            "users": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ],
            "settings": {
                "theme": "dark",
                "languages": ["en", "es"]
            }
        }
        result = collect_string_paths(data)
        
        assert len(result) == 5
        assert (('users', 0, 'name'), 'John') in result
        assert (('users', 1, 'name'), 'Jane') in result
        assert (('settings', 'theme'), 'dark') in result
        assert (('settings', 'languages', 0), 'en') in result
        assert (('settings', 'languages', 1), 'es') in result
    
    def test_empty_dict(self):
        """Test with empty dictionary."""
        data = {}
        result = collect_string_paths(data)
        assert result == []
    
    def test_empty_array(self):
        """Test with empty array."""
        data = {"items": []}
        result = collect_string_paths(data)
        assert result == []
    
    def test_empty_strings(self):
        """Test that empty strings are collected."""
        data = {"empty": "", "items": ["", "text"]}
        result = collect_string_paths(data)
        
        assert len(result) == 3
        assert (('empty',), '') in result
        assert (('items', 0), '') in result
        assert (('items', 1), 'text') in result


class TestSetByPath:
    """Tests for set_by_path function."""
    
    def test_set_simple_dict_value(self):
        """Test setting a value in a simple dictionary."""
        data = {"name": "John", "city": "Madrid"}
        set_by_path(data, ('name',), 'Jane')
        
        assert data['name'] == 'Jane'
        assert data['city'] == 'Madrid'
    
    def test_set_nested_dict_value(self):
        """Test setting a value in nested dictionaries."""
        data = {
            "user": {
                "name": "John",
                "address": {
                    "city": "Madrid"
                }
            }
        }
        set_by_path(data, ('user', 'address', 'city'), 'Barcelona')
        
        assert data['user']['address']['city'] == 'Barcelona'
        assert data['user']['name'] == 'John'
    
    def test_set_array_value(self):
        """Test setting a value in an array."""
        data = {"items": ["apple", "banana", "cherry"]}
        set_by_path(data, ('items', 1), 'orange')
        
        assert data['items'] == ["apple", "orange", "cherry"]
    
    def test_set_nested_array_value(self):
        """Test setting a value in nested arrays."""
        data = {
            "users": [
                {"name": "John", "items": ["a", "b"]},
                {"name": "Jane", "items": ["c", "d"]}
            ]
        }
        set_by_path(data, ('users', 0, 'items', 1), 'modified')
        
        assert data['users'][0]['items'][1] == 'modified'
        assert data['users'][0]['items'][0] == 'a'
    
    def test_set_different_type(self):
        """Test that we can change the type of a value."""
        data = {"value": "text"}
        set_by_path(data, ('value',), 42)
        
        assert data['value'] == 42
    
    def test_set_with_empty_path_raises_error(self):
        """Test that setting with empty path raises ValueError."""
        data = {"key": "value"}
        
        with pytest.raises(ValueError, match="Cannot set value at empty path"):
            set_by_path(data, (), "new_value")
    
    def test_set_with_invalid_key_raises_error(self):
        """Test that setting with non-existent key raises KeyError."""
        data = {"key": "value"}
        
        with pytest.raises(KeyError):
            set_by_path(data, ('nonexistent', 'nested'), "value")
    
    def test_set_with_invalid_index_raises_error(self):
        """Test that setting with out-of-range index raises IndexError."""
        data = {"items": ["a", "b"]}
        
        with pytest.raises(IndexError):
            set_by_path(data, ('items', 10), "value")
    
    def test_set_in_primitive_raises_error(self):
        """Test that trying to index into a primitive raises TypeError."""
        data = {"value": "text"}
        
        with pytest.raises(TypeError):
            set_by_path(data, ('value', 'nested'), "new")


class TestRoundTrip:
    """Test that collect and set work together correctly."""
    
    def test_collect_and_restore(self):
        """Test collecting paths and restoring values."""
        original = {
            "name": "John",
            "age": 30,
            "items": ["apple", "banana"],
            "nested": {
                "city": "Madrid"
            }
        }
        
        # Collect all string paths
        paths = collect_string_paths(original)
        
        # Modify all strings
        for path, value in paths:
            set_by_path(original, path, value.upper())
        
        # Verify modifications
        assert original['name'] == 'JOHN'
        assert original['items'][0] == 'APPLE'
        assert original['items'][1] == 'BANANA'
        assert original['nested']['city'] == 'MADRID'
        assert original['age'] == 30  # Non-string unchanged



class TestPropertyBasedKeysPreservation:
    """Property-based tests for keys preservation during translation."""
    
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
    def test_keys_preservation_property(self, json_data):
        """
        **Feature: json-translator, Property 2: Keys preservation**
        **Validates: Requirements 1.2**
        
        For any JSON structure with keys at any nesting level, all keys in the 
        translated files should be identical to the keys in the source file.
        
        This test verifies that when we collect string paths and modify values,
        the keys in the JSON structure remain unchanged.
        """
        # Skip non-dict/list top-level values as they don't have keys
        if not isinstance(json_data, (dict, list)):
            return
        
        # Extract all keys from the original structure
        original_keys = self._extract_all_keys(json_data)
        
        # Collect string paths
        string_paths = collect_string_paths(json_data)
        
        # Create a deep copy to simulate translation
        import copy
        translated_data = copy.deepcopy(json_data)
        
        # Simulate translation by modifying all string values
        for path, original_value in string_paths:
            if isinstance(original_value, str):
                # Simulate translation by uppercasing
                set_by_path(translated_data, path, original_value.upper())
        
        # Extract all keys from the translated structure
        translated_keys = self._extract_all_keys(translated_data)
        
        # Verify that all keys are preserved
        assert original_keys == translated_keys, \
            f"Keys were not preserved. Original: {original_keys}, Translated: {translated_keys}"
    
    def _extract_all_keys(self, obj, path=()):
        """
        Recursively extract all keys from a JSON structure with their paths.
        
        Returns a set of (path, key) tuples representing all keys in the structure.
        """
        keys = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Add this key with its path
                keys.add((path, key))
                # Recursively extract keys from nested structures
                if isinstance(value, (dict, list)):
                    keys.update(self._extract_all_keys(value, path + (key,)))
        
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                # Recursively extract keys from nested structures
                if isinstance(value, (dict, list)):
                    keys.update(self._extract_all_keys(value, path + (index,)))
        
        return keys



class TestPropertyBasedNonStringPreservation:
    """Property-based tests for non-string value preservation during translation."""
    
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
    def test_only_strings_translated_property(self, json_data):
        """
        **Feature: json-translator, Property 3: Only strings translated**
        **Validates: Requirements 1.3**
        
        For any JSON structure containing mixed types (strings, numbers, booleans, null),
        only the string values should be modified in the translation, while all other
        types remain unchanged.
        
        This test verifies that when we collect string paths and modify values,
        only strings are affected and all non-string values remain identical.
        """
        # Skip non-dict/list top-level values as they are primitives
        if not isinstance(json_data, (dict, list)):
            return
        
        # Extract all non-string values from the original structure
        original_non_strings = self._extract_non_string_values(json_data)
        
        # Collect string paths
        string_paths = collect_string_paths(json_data)
        
        # Create a deep copy to simulate translation
        import copy
        translated_data = copy.deepcopy(json_data)
        
        # Simulate translation by modifying all string values
        for path, original_value in string_paths:
            if isinstance(original_value, str):
                # Simulate translation by uppercasing
                set_by_path(translated_data, path, original_value.upper())
        
        # Extract all non-string values from the translated structure
        translated_non_strings = self._extract_non_string_values(translated_data)
        
        # Verify that all non-string values are preserved
        assert original_non_strings == translated_non_strings, \
            f"Non-string values were not preserved.\nOriginal: {original_non_strings}\nTranslated: {translated_non_strings}"
    
    def _extract_non_string_values(self, obj, path=()):
        """
        Recursively extract all non-string values from a JSON structure with their paths.
        
        Returns a set of (path, value, type) tuples representing all non-string values.
        """
        non_strings = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = path + (key,)
                if isinstance(value, str):
                    # Skip strings
                    pass
                elif isinstance(value, (dict, list)):
                    # Recursively extract from nested structures
                    non_strings.update(self._extract_non_string_values(value, new_path))
                else:
                    # This is a non-string primitive (int, float, bool, None)
                    # Store as (path, value, type) to handle None and bool correctly
                    non_strings.add((new_path, value, type(value).__name__))
        
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                new_path = path + (index,)
                if isinstance(value, str):
                    # Skip strings
                    pass
                elif isinstance(value, (dict, list)):
                    # Recursively extract from nested structures
                    non_strings.update(self._extract_non_string_values(value, new_path))
                else:
                    # This is a non-string primitive (int, float, bool, None)
                    non_strings.add((new_path, value, type(value).__name__))
        
        return non_strings



class TestPropertyBasedKeyOrderPreservation:
    """Property-based tests for key order preservation during translation."""
    
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
    def test_key_order_preservation_property(self, json_data):
        """
        **Feature: json-translator, Property 14: Key order preservation**
        **Validates: Requirements 7.3**
        
        For any JSON object with keys in order K1, K2, ..., Kn, the translated files
        should maintain the same key order K1, K2, ..., Kn.
        
        This test verifies that when we collect string paths and modify values,
        the order of keys in all dictionaries remains unchanged.
        """
        # Skip non-dict/list top-level values as they don't have keys
        if not isinstance(json_data, (dict, list)):
            return
        
        # Extract key orders from the original structure
        original_key_orders = self._extract_key_orders(json_data)
        
        # Collect string paths
        string_paths = collect_string_paths(json_data)
        
        # Create a deep copy to simulate translation
        import copy
        translated_data = copy.deepcopy(json_data)
        
        # Simulate translation by modifying all string values
        for path, original_value in string_paths:
            if isinstance(original_value, str):
                # Simulate translation by uppercasing
                set_by_path(translated_data, path, original_value.upper())
        
        # Extract key orders from the translated structure
        translated_key_orders = self._extract_key_orders(translated_data)
        
        # Verify that all key orders are preserved
        assert original_key_orders == translated_key_orders, \
            f"Key orders were not preserved.\nOriginal: {original_key_orders}\nTranslated: {translated_key_orders}"
    
    def _extract_key_orders(self, obj, path=()):
        """
        Recursively extract the order of keys from all dictionaries in a JSON structure.
        
        Returns a set of tuples representing key orders:
        - (path, tuple(keys)) for each dictionary in the structure
        """
        key_orders = set()
        
        if isinstance(obj, dict):
            # Record the key order for this dictionary
            # Using tuple to make it hashable for set storage
            key_orders.add((path, tuple(obj.keys())))
            
            # Recursively extract from nested structures
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    key_orders.update(self._extract_key_orders(value, path + (key,)))
        
        elif isinstance(obj, list):
            # Recursively extract from nested structures in lists
            for index, value in enumerate(obj):
                if isinstance(value, (dict, list)):
                    key_orders.update(self._extract_key_orders(value, path + (index,)))
        
        return key_orders


class TestPropertyBasedStructurePreservation:
    """Property-based tests for structure preservation during translation."""
    
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
    def test_object_hierarchy_preservation_property(self, json_data):
        """
        **Feature: json-translator, Property 7: Object hierarchy preservation**
        **Validates: Requirements 3.1**
        
        For any JSON structure with nested objects at depth D, the translated files
        should maintain the same nesting depth D with identical object structure.
        
        This test verifies that when we collect string paths and modify values,
        the object hierarchy (nesting depth and structure) remains unchanged.
        """
        # Skip non-dict/list top-level values as they don't have hierarchy
        if not isinstance(json_data, (dict, list)):
            return
        
        # Extract object hierarchy from the original structure
        original_hierarchy = self._extract_object_hierarchy(json_data)
        
        # Collect string paths
        string_paths = collect_string_paths(json_data)
        
        # Create a deep copy to simulate translation
        import copy
        translated_data = copy.deepcopy(json_data)
        
        # Simulate translation by modifying all string values
        for path, original_value in string_paths:
            if isinstance(original_value, str):
                # Simulate translation by uppercasing
                set_by_path(translated_data, path, original_value.upper())
        
        # Extract object hierarchy from the translated structure
        translated_hierarchy = self._extract_object_hierarchy(translated_data)
        
        # Verify that the object hierarchy is preserved
        assert original_hierarchy == translated_hierarchy, \
            f"Object hierarchy was not preserved.\nOriginal: {original_hierarchy}\nTranslated: {translated_hierarchy}"
    
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
    def test_array_structure_preservation_property(self, json_data):
        """
        **Feature: json-translator, Property 8: Array structure preservation**
        **Validates: Requirements 3.2**
        
        For any array in the source JSON with N elements, the corresponding array
        in each translated file should contain exactly N elements in the same positions.
        
        This test verifies that when we collect string paths and modify values,
        all arrays maintain their length and element positions.
        """
        # Skip non-dict/list top-level values as they don't have arrays
        if not isinstance(json_data, (dict, list)):
            return
        
        # Extract array structures from the original
        original_arrays = self._extract_array_structures(json_data)
        
        # Collect string paths
        string_paths = collect_string_paths(json_data)
        
        # Create a deep copy to simulate translation
        import copy
        translated_data = copy.deepcopy(json_data)
        
        # Simulate translation by modifying all string values
        for path, original_value in string_paths:
            if isinstance(original_value, str):
                # Simulate translation by uppercasing
                set_by_path(translated_data, path, original_value.upper())
        
        # Extract array structures from the translated
        translated_arrays = self._extract_array_structures(translated_data)
        
        # Verify that all array structures are preserved
        assert original_arrays == translated_arrays, \
            f"Array structures were not preserved.\nOriginal: {original_arrays}\nTranslated: {translated_arrays}"
    
    def _extract_object_hierarchy(self, obj, path=()):
        """
        Recursively extract the object hierarchy from a JSON structure.
        
        Returns a set of tuples representing the structure:
        - (path, 'dict', frozenset(keys)) for dictionaries
        - (path, 'list', length) for lists
        """
        hierarchy = set()
        
        if isinstance(obj, dict):
            # Record this dictionary with its keys
            hierarchy.add((path, 'dict', frozenset(obj.keys())))
            # Recursively extract from nested structures
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    hierarchy.update(self._extract_object_hierarchy(value, path + (key,)))
        
        elif isinstance(obj, list):
            # Record this list with its length
            hierarchy.add((path, 'list', len(obj)))
            # Recursively extract from nested structures
            for index, value in enumerate(obj):
                if isinstance(value, (dict, list)):
                    hierarchy.update(self._extract_object_hierarchy(value, path + (index,)))
        
        return hierarchy
    
    def _extract_array_structures(self, obj, path=()):
        """
        Recursively extract all array structures from a JSON structure.
        
        Returns a set of tuples representing arrays:
        - (path, length, tuple(types)) where types is the type of each element
        """
        arrays = set()
        
        if isinstance(obj, dict):
            # Recursively extract from nested structures
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    arrays.update(self._extract_array_structures(value, path + (key,)))
        
        elif isinstance(obj, list):
            # Record this array with its length and element types
            element_types = tuple(type(elem).__name__ for elem in obj)
            arrays.add((path, len(obj), element_types))
            
            # Recursively extract from nested structures
            for index, value in enumerate(obj):
                if isinstance(value, (dict, list)):
                    arrays.update(self._extract_array_structures(value, path + (index,)))
        
        return arrays
