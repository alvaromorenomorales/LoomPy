"""Unit and property-based tests for file I/O operations."""

import json
import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st

from src.file_io import load_json_file, validate_json_structure, serialize_json, ensure_output_directory


class TestLoadJsonFile:
    """Unit tests for load_json_file function."""
    
    def test_load_valid_json_file(self):
        """Test loading a valid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({"name": "John", "age": 30}, f)
            temp_path = f.name
        
        try:
            data = load_json_file(temp_path)
            assert data == {"name": "John", "age": 30}
        finally:
            Path(temp_path).unlink()
    
    def test_load_file_not_found(self):
        """Test file not found error."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_json_file("nonexistent_file.json")
    
    def test_load_invalid_json(self):
        """Test invalid JSON error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("{invalid json content")
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError, match="Invalid JSON"):
                load_json_file(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_load_json_with_unicode(self):
        """Test loading JSON with Unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({"greeting": "Hola", "emoji": "😀", "chinese": "你好"}, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            data = load_json_file(temp_path)
            assert data["greeting"] == "Hola"
            assert data["emoji"] == "😀"
            assert data["chinese"] == "你好"
        finally:
            Path(temp_path).unlink()


class TestValidateJsonStructure:
    """Unit tests for validate_json_structure function."""
    
    def test_validate_dict(self):
        """Test validation of dictionary structure."""
        assert validate_json_structure({"key": "value"}) is True
    
    def test_validate_list(self):
        """Test validation of list structure."""
        assert validate_json_structure([1, 2, 3]) is True
    
    def test_validate_primitives(self):
        """Test validation of primitive types."""
        assert validate_json_structure("string") is True
        assert validate_json_structure(42) is True
        assert validate_json_structure(3.14) is True
        assert validate_json_structure(True) is True
        assert validate_json_structure(None) is True
    
    def test_validate_nested_structure(self):
        """Test validation of nested structures."""
        data = {
            "users": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ],
            "settings": {
                "theme": "dark"
            }
        }
        assert validate_json_structure(data) is True


class TestSerializeJson:
    """Unit tests for serialize_json function."""
    
    def test_serialize_simple_dict(self):
        """Test serializing a simple dictionary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.json"
            data = {"name": "John", "age": 30}
            
            serialize_json(data, str(output_path))
            
            # Read back and verify
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                loaded = json.loads(content)
            
            assert loaded == data
            # Verify formatting (2-space indent)
            assert '  "name"' in content or '  "age"' in content
    
    def test_serialize_creates_directory(self):
        """Test that serialize_json creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "output.json"
            data = {"key": "value"}
            
            serialize_json(data, str(output_path))
            
            assert output_path.exists()
            with open(output_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            assert loaded == data
    
    def test_serialize_with_unicode(self):
        """Test serializing with Unicode characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.json"
            data = {"greeting": "Hola", "emoji": "😀", "chinese": "你好"}
            
            serialize_json(data, str(output_path))
            
            # Read back and verify Unicode is not escaped
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert "Hola" in content
            assert "😀" in content
            assert "你好" in content
            # Verify it's not escaped
            assert "\\u" not in content


class TestErrorHandling:
    """Unit tests for error handling in file I/O operations."""
    
    def test_file_not_found_error(self):
        """
        Test file not found error.
        Requirements: 4.1
        """
        with pytest.raises(FileNotFoundError) as exc_info:
            load_json_file("nonexistent_file.json")
        
        assert "File not found" in str(exc_info.value)
        assert "nonexistent_file.json" in str(exc_info.value)
    
    def test_invalid_json_error(self):
        """
        Test invalid JSON error.
        Requirements: 4.2
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write('{"key": "value", invalid}')
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError) as exc_info:
                load_json_file(temp_path)
            
            assert "Invalid JSON" in str(exc_info.value)
            assert temp_path in str(exc_info.value)
        finally:
            Path(temp_path).unlink()
    
    def test_empty_file_error(self):
        """Test loading an empty file raises JSONDecodeError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            # Write nothing
            temp_path = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_json_file(temp_path)
        finally:
            Path(temp_path).unlink()


class TestPropertyBasedUnicodePreservation:
    """Property-based tests for Unicode preservation during serialization."""
    
    @given(
        json_data=st.recursive(
            st.one_of(
                st.none(),
                st.booleans(),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                # Generate text with various Unicode characters
                st.text(
                    alphabet=st.characters(
                        blacklist_categories=('Cc', 'Cs'),  # Exclude control chars and surrogates
                        min_codepoint=32  # Start from space character
                    ),
                    min_size=0,
                    max_size=50
                )
            ),
            lambda children: st.one_of(
                st.dictionaries(
                    keys=st.text(
                        min_size=1,
                        max_size=20,
                        alphabet=st.characters(min_codepoint=97, max_codepoint=122)
                    ),
                    values=children,
                    min_size=0,
                    max_size=5
                ),
                st.lists(children, min_size=0, max_size=5)
            ),
            max_leaves=20
        )
    )
    def test_unicode_preservation_property(self, json_data):
        """
        **Feature: json-translator, Property 13: Unicode preservation**
        **Validates: Requirements 7.2**
        
        For any string containing Unicode characters (accents, emojis, non-Latin scripts),
        these characters should be preserved without escaping in the output files.
        
        This test verifies that when we serialize JSON data containing Unicode characters,
        they are written without ASCII escaping and can be read back identically.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.json"
            
            # Serialize the data
            serialize_json(json_data, str(output_path))
            
            # Read back the data
            loaded_data = load_json_file(str(output_path))
            
            # Verify the data is identical
            assert loaded_data == json_data, \
                f"Data was not preserved.\nOriginal: {json_data}\nLoaded: {loaded_data}"
            
            # Additionally verify that Unicode is not escaped in the file
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract all string values from the original data
            string_values = self._extract_all_strings(json_data)
            
            # For each string with non-ASCII characters, verify they're not Unicode-escaped
            for string_value in string_values:
                if string_value and any(ord(c) > 127 for c in string_value):
                    # This string has non-ASCII characters
                    # Check that these Unicode characters are not escaped as \uXXXX
                    for char in string_value:
                        if ord(char) > 127:
                            # This is a Unicode character
                            # It should appear literally in the file, not as \uXXXX
                            unicode_escape = f"\\u{ord(char):04x}"
                            assert unicode_escape not in content.lower(), \
                                f"Unicode character '{char}' (U+{ord(char):04X}) was escaped as {unicode_escape}"
    
    def _extract_all_strings(self, obj):
        """Recursively extract all string values from a JSON structure."""
        strings = []
        
        if isinstance(obj, str):
            strings.append(obj)
        elif isinstance(obj, dict):
            for value in obj.values():
                strings.extend(self._extract_all_strings(value))
        elif isinstance(obj, list):
            for item in obj:
                strings.extend(self._extract_all_strings(item))
        
        return strings


class TestEnsureOutputDirectory:
    """Unit tests for ensure_output_directory function."""
    
    def test_create_new_directory(self):
        """Test creating a new directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_output_dir"
            
            # Directory should not exist yet
            assert not new_dir.exists()
            
            # Create the directory
            ensure_output_directory(str(new_dir))
            
            # Directory should now exist
            assert new_dir.exists()
            assert new_dir.is_dir()
    
    def test_create_nested_directory(self):
        """Test creating nested directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "level1" / "level2" / "level3"
            
            # Directory should not exist yet
            assert not nested_dir.exists()
            
            # Create the nested directory
            ensure_output_directory(str(nested_dir))
            
            # All levels should now exist
            assert nested_dir.exists()
            assert nested_dir.is_dir()
    
    def test_existing_directory(self):
        """Test that existing directory is handled gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # temp_dir already exists
            # This should not raise an error
            ensure_output_directory(temp_dir)
            
            # Directory should still exist
            assert Path(temp_dir).exists()
            assert Path(temp_dir).is_dir()
    
    def test_path_is_file_not_directory(self):
        """Test error when path exists but is a file, not a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "file.txt"
            file_path.write_text("content")
            
            # Should raise NotADirectoryError
            with pytest.raises(NotADirectoryError, match="Path exists but is not a directory"):
                ensure_output_directory(str(file_path))
    
    def test_permission_error_on_readonly_parent(self):
        """Test permission error when parent directory is read-only."""
        # This test is platform-specific and may not work on all systems
        # Skip on Windows where permission handling is different
        import platform
        if platform.system() == "Windows":
            pytest.skip("Permission test not reliable on Windows")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            parent_dir = Path(temp_dir) / "readonly_parent"
            parent_dir.mkdir()
            
            # Make parent directory read-only
            parent_dir.chmod(0o444)
            
            try:
                new_dir = parent_dir / "new_dir"
                
                # Should raise PermissionError
                with pytest.raises(PermissionError, match="Cannot create directory"):
                    ensure_output_directory(str(new_dir))
            finally:
                # Restore permissions for cleanup
                parent_dir.chmod(0o755)


class TestPropertyBasedKeyOrderPreservation:
    """Property-based tests for key order preservation during serialization."""
    
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
                    keys=st.text(
                        min_size=1,
                        max_size=20,
                        alphabet=st.characters(min_codepoint=97, max_codepoint=122)
                    ),
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
        
        For any JSON object with keys in order K1, K2, ..., Kn, the serialized
        files should maintain the same key order K1, K2, ..., Kn.
        
        This test verifies that when we serialize and load JSON data,
        the order of keys in all dictionaries is preserved.
        """
        # Skip non-dict/list top-level values
        if not isinstance(json_data, (dict, list)):
            return
        
        # Extract key orders from the original structure
        original_key_orders = self._extract_key_orders(json_data)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test.json"
            
            # Serialize the data
            serialize_json(json_data, str(output_path))
            
            # Read back the data
            loaded_data = load_json_file(str(output_path))
            
            # Extract key orders from the loaded structure
            loaded_key_orders = self._extract_key_orders(loaded_data)
            
            # Verify that all key orders are preserved
            assert original_key_orders == loaded_key_orders, \
                f"Key orders were not preserved.\nOriginal: {original_key_orders}\nLoaded: {loaded_key_orders}"
    
    def _extract_key_orders(self, obj, path=()):
        """
        Recursively extract the order of keys from all dictionaries in a JSON structure.
        
        Returns a set of tuples representing key orders:
        - (path, tuple(keys)) for each dictionary in the structure
        """
        key_orders = set()
        
        if isinstance(obj, dict):
            # Record the key order for this dictionary
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
