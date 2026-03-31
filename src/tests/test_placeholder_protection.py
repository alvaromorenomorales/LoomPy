"""Unit tests for placeholder protection system."""

import pytest
from hypothesis import given, strategies as st
from src.placeholder_protection import extract_placeholders, restore_placeholders


class TestPlaceholderExtraction:
    """Tests for extract_placeholders function."""
    
    def test_brace_placeholder(self):
        """Test extraction of {variable} format placeholders."""
        text = "Hello {name}, welcome!"
        protected, mapping = extract_placeholders(text)
        
        assert "__PH0__" in protected
        assert mapping["__PH0__"] == "{name}"
        assert "Hello __PH0__, welcome!" == protected
    
    def test_printf_placeholder(self):
        """Test extraction of %s format placeholders."""
        text = "You have %s messages"
        protected, mapping = extract_placeholders(text)
        
        assert "__PH0__" in protected
        assert mapping["__PH0__"] == "%s"
        assert "You have __PH0__ messages" == protected
    
    def test_named_placeholder(self):
        """Test extraction of %(name)s format placeholders."""
        text = "Hello %(username)s, you have %(count)d items"
        protected, mapping = extract_placeholders(text)
        
        # Verify both placeholders are extracted
        assert len(mapping) == 2
        assert "%(username)s" in mapping.values()
        assert "%(count)d" in mapping.values()
        
        # Verify tokens are in the protected text
        assert "__PH0__" in protected
        assert "__PH1__" in protected
    
    def test_multiple_placeholders(self):
        """Test extraction of multiple placeholders in one text."""
        text = "Hello {name}, you have %s messages and %(count)d notifications"
        protected, mapping = extract_placeholders(text)
        
        assert len(mapping) == 3
        assert "{name}" in mapping.values()
        assert "%s" in mapping.values()
        assert "%(count)d" in mapping.values()
    
    def test_no_placeholders(self):
        """Test text without placeholders."""
        text = "Hello world"
        protected, mapping = extract_placeholders(text)
        
        assert protected == text
        assert len(mapping) == 0
    
    def test_empty_string(self):
        """Test empty string."""
        text = ""
        protected, mapping = extract_placeholders(text)
        
        assert protected == ""
        assert len(mapping) == 0


class TestPlaceholderRestoration:
    """Tests for restore_placeholders function."""
    
    def test_restore_single_placeholder(self):
        """Test restoration of a single placeholder."""
        text = "Hello __PH0__, welcome!"
        mapping = {"__PH0__": "{name}"}
        restored = restore_placeholders(text, mapping)
        
        assert restored == "Hello {name}, welcome!"
    
    def test_restore_multiple_placeholders(self):
        """Test restoration of multiple placeholders."""
        text = "Hello __PH0__, you have __PH1__ messages"
        mapping = {"__PH0__": "{name}", "__PH1__": "%s"}
        restored = restore_placeholders(text, mapping)
        
        assert restored == "Hello {name}, you have %s messages"
    
    def test_restore_no_placeholders(self):
        """Test restoration with empty mapping."""
        text = "Hello world"
        mapping = {}
        restored = restore_placeholders(text, mapping)
        
        assert restored == text


class TestRoundTrip:
    """Tests for round-trip placeholder protection and restoration."""
    
    def test_roundtrip_preserves_text(self):
        """Test that extract and restore preserve original text."""
        original = "Hello {name}, you have %s messages and %(count)d items"
        protected, mapping = extract_placeholders(original)
        restored = restore_placeholders(protected, mapping)
        
        assert restored == original
    
    def test_roundtrip_with_no_placeholders(self):
        """Test round-trip with text containing no placeholders."""
        original = "Hello world, this is a test"
        protected, mapping = extract_placeholders(original)
        restored = restore_placeholders(protected, mapping)
        
        assert restored == original



class TestPropertyBasedPlaceholderPreservation:
    """Property-based tests for placeholder preservation."""
    
    @given(
        num_placeholders=st.integers(min_value=2, max_value=5),
        placeholder_types=st.lists(
            st.sampled_from([
                '{name}', '{user}', '{count}', '{value}', '{id}',
                '%s', '%d', '%i', '%f', '%g',
                '%(username)s', '%(count)d', '%(value)i', '%(name)s', '%(id)d'
            ]),
            min_size=2,
            max_size=5,
            unique=True  # Ensure placeholders are unique to avoid confusion
        )
    )
    def test_multiple_placeholders_preservation(self, num_placeholders, placeholder_types):
        """
        **Feature: json-translator, Property 6: Multiple placeholders preservation**
        **Validates: Requirements 2.4**
        
        For any string value containing multiple placeholders of any supported format,
        all placeholders should appear in the translated text in their correct relative positions.
        """
        # Use only the number of placeholders we need
        placeholders = placeholder_types[:num_placeholders]
        
        # Build a text with multiple placeholders interspersed with text
        text_parts = [f"text{i} " for i in range(num_placeholders + 1)]
        original_text = ""
        for i in range(len(placeholders)):
            original_text += text_parts[i] + placeholders[i] + " "
        original_text += text_parts[-1]
        
        # Extract placeholders
        protected_text, mapping = extract_placeholders(original_text)
        
        # Simulate translation by modifying the protected text
        # (In real translation, the model would translate the text but preserve tokens)
        simulated_translation = protected_text.upper()
        
        # Restore placeholders
        restored_text = restore_placeholders(simulated_translation, mapping)
        
        # Verify all placeholders are present in the restored text
        for placeholder in placeholders:
            assert placeholder in restored_text, \
                f"Placeholder {placeholder} not found in restored text: {restored_text}"
        
        # Verify the count of each placeholder matches
        for placeholder in placeholders:
            original_count = original_text.count(placeholder)
            restored_count = restored_text.count(placeholder)
            assert original_count == restored_count, \
                f"Placeholder {placeholder} count mismatch. Original: {original_count}, Restored: {restored_count}"
        
        # Verify the relative order of placeholders is preserved
        # Extract placeholder positions from original text
        original_positions = []
        for placeholder in placeholders:
            pos = original_text.find(placeholder)
            original_positions.append((pos, placeholder))
        original_positions.sort(key=lambda x: x[0])
        
        # Extract placeholder positions from restored text
        restored_positions = []
        for placeholder in placeholders:
            pos = restored_text.find(placeholder)
            restored_positions.append((pos, placeholder))
        restored_positions.sort(key=lambda x: x[0])
        
        # The order should be the same
        original_order = [ph for _, ph in original_positions]
        restored_order = [ph for _, ph in restored_positions]
        
        assert original_order == restored_order, \
            f"Placeholder order not preserved. Original: {original_order}, Restored: {restored_order}"
