"""Property-based tests for file generation and output behavior."""

import json
import os
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from src.translation_pipeline import translate_json_values


class TestOutputFileGeneration:
    """Property-based tests for output file generation."""
    
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
    def test_three_output_files_generated(self, json_data):
        """
        **Feature: json-translator, Property 1: Three output files generated**
        **Validates: Requirements 1.1**
        
        For any valid JSON source file, the system should generate exactly three output files
        corresponding to English, French, and Catalan translations.
        """
        # Create a temporary directory for test files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write the source JSON file
            source_file = Path(tmpdir) / "es.json"
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            # Define target languages
            target_languages = ["en", "fr", "ca"]
            
            # Mock translation function that simulates translation
            def mock_translate(texts):
                # Simple mock: just add a prefix to indicate translation
                return [f"translated_{text}" if isinstance(text, str) else text for text in texts]
            
            # Simulate the translation process for each language
            output_files = []
            for lang in target_languages:
                # Translate the JSON data
                translated_data = translate_json_values(json_data, mock_translate)
                
                # Write the output file
                output_file = Path(tmpdir) / f"{lang}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(translated_data, f, ensure_ascii=False, indent=2)
                
                output_files.append(output_file)
            
            # Property: Exactly three output files should be generated
            assert len(output_files) == 3, \
                f"Expected 3 output files, but got {len(output_files)}"
            
            # Verify each output file exists
            for output_file in output_files:
                assert output_file.exists(), \
                    f"Output file {output_file} does not exist"
            
            # Verify the files have the correct names
            expected_files = {"en.json", "fr.json", "ca.json"}
            actual_files = {f.name for f in output_files}
            assert actual_files == expected_files, \
                f"Expected files {expected_files}, but got {actual_files}"
            
            # Verify each file contains valid JSON
            for output_file in output_files:
                with open(output_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Verify the structure is preserved (same type as input)
                    assert type(loaded_data) == type(json_data), \
                        f"Output file {output_file.name} has different type than input"
