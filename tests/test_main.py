"""Tests for main entry point and CLI argument parsing."""

import pytest
from hypothesis import given, strategies as st
from src.main import parse_arguments
from src.config import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_FILE,
    DEFAULT_TARGET_LANGUAGES,
    SUPPORTED_LANGUAGES,
    get_input_path
)
import sys


def test_parse_arguments_defaults():
    """Test that default arguments are set correctly."""
    # Save original argv
    original_argv = sys.argv
    
    try:
        # Test with no arguments
        sys.argv = ["json_translator"]
        args = parse_arguments()
        
        # Check defaults from config
        assert args.input == str(get_input_path())
        assert args.langs == DEFAULT_TARGET_LANGUAGES
        assert args.out_dir == DEFAULT_OUTPUT_DIR
        assert args.device is None
    finally:
        # Restore original argv
        sys.argv = original_argv


def test_parse_arguments_custom_input():
    """Test parsing custom input file."""
    original_argv = sys.argv
    
    try:
        sys.argv = ["json_translator", "custom.json"]
        args = parse_arguments()
        
        assert args.input == "custom.json"
        assert args.langs == DEFAULT_TARGET_LANGUAGES  # Still defaults from config
    finally:
        sys.argv = original_argv


def test_parse_arguments_custom_langs():
    """Test parsing custom language list."""
    original_argv = sys.argv
    
    try:
        sys.argv = ["json_translator", "--langs", "en", "fr"]
        args = parse_arguments()
        
        assert args.input == str(get_input_path())  # Default from config
        assert args.langs == ["en", "fr"]
    finally:
        sys.argv = original_argv


def test_parse_arguments_single_lang():
    """Test parsing single language."""
    original_argv = sys.argv
    
    try:
        sys.argv = ["json_translator", "--langs", "en"]
        args = parse_arguments()
        
        assert args.langs == ["en"]
    finally:
        sys.argv = original_argv


def test_parse_arguments_custom_out_dir():
    """Test parsing custom output directory."""
    original_argv = sys.argv
    
    try:
        sys.argv = ["json_translator", "--out-dir", "./translations"]
        args = parse_arguments()
        
        assert args.out_dir == "./translations"
    finally:
        sys.argv = original_argv


def test_parse_arguments_device_cpu():
    """Test parsing device argument for CPU."""
    original_argv = sys.argv
    
    try:
        sys.argv = ["json_translator", "--device", "cpu"]
        args = parse_arguments()
        
        assert args.device == "cpu"
    finally:
        sys.argv = original_argv


def test_parse_arguments_device_cuda():
    """Test parsing device argument for CUDA."""
    original_argv = sys.argv
    
    try:
        sys.argv = ["json_translator", "--device", "cuda"]
        args = parse_arguments()
        
        assert args.device == "cuda"
    finally:
        sys.argv = original_argv


def test_parse_arguments_all_custom():
    """Test parsing all custom arguments."""
    original_argv = sys.argv
    
    try:
        sys.argv = [
            "json_translator",
            "input.json",
            "--langs", "en", "ca",
            "--out-dir", "./output",
            "--device", "cpu"
        ]
        args = parse_arguments()
        
        assert args.input == "input.json"
        assert args.langs == ["en", "ca"]
        assert args.out_dir == "./output"
        assert args.device == "cpu"
    finally:
        sys.argv = original_argv


class TestPropertyBasedLanguageSelection:
    """Property-based tests for language selection functionality."""
    
    @given(
        selected_langs=st.lists(
            st.sampled_from(SUPPORTED_LANGUAGES),
            min_size=1,
            max_size=len(SUPPORTED_LANGUAGES),
            unique=True
        )
    )
    def test_language_selection_property(self, selected_langs):
        """
        **Feature: json-translator, Property 11: Language selection**
        **Validates: Requirements 5.2**
        
        For any subset of supported languages specified by the user,
        the system should generate output files only for those languages.
        
        This test verifies that when a user specifies a subset of supported
        languages from config, the argument parser correctly captures that
        selection and only those languages would be processed.
        """
        original_argv = sys.argv
        
        try:
            # Build command line arguments with selected languages
            sys.argv = ["json_translator", "--langs"] + selected_langs
            
            # Parse arguments
            args = parse_arguments()
            
            # Verify that the parsed languages match exactly what was specified
            assert args.langs == selected_langs, \
                f"Expected languages {selected_langs}, but got {args.langs}"
            
            # Verify that the parsed languages list contains only the selected languages
            assert set(args.langs) == set(selected_langs), \
                f"Language set mismatch: expected {set(selected_langs)}, got {set(args.langs)}"
            
            # Verify that no extra languages were added
            assert len(args.langs) == len(selected_langs), \
                f"Expected {len(selected_langs)} languages, but got {len(args.langs)}"
            
            # Verify that all selected languages are in the supported set from config
            supported_langs_set = set(SUPPORTED_LANGUAGES)
            for lang in args.langs:
                assert lang in supported_langs_set, \
                    f"Language '{lang}' is not in supported languages {supported_langs_set}"
        
        finally:
            # Restore original argv
            sys.argv = original_argv
