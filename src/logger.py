"""Logging and progress reporting for JSON translation."""

import sys
from typing import Optional


def log_progress(message: str) -> None:
    """
    Log a progress message to stdout.
    
    Args:
        message: The progress message to display
        
    Example:
        >>> log_progress("Processing language: en")
        Processing language: en
    """
    print(message, file=sys.stdout)


def log_completion(language: str, output_path: str) -> None:
    """
    Log a completion message with the output file path.
    
    Args:
        language: The target language code (e.g., "en", "fr", "ca")
        output_path: The path to the generated output file
        
    Example:
        >>> log_completion("en", "./en.json")
        ✓ Translation completed: en.json -> ./en.json
    """
    print(f"✓ Translation completed: {language}.json -> {output_path}", file=sys.stdout)


def log_error(message: str, error: Optional[Exception] = None) -> None:
    """
    Log an error message to stderr with optional exception details.
    
    Args:
        message: The error message to display
        error: Optional exception object for additional context
        
    Example:
        >>> log_error("Failed to load model", ValueError("Model not found"))
        ✗ Error: Failed to load model
        Details: Model not found
    """
    print(f"✗ Error: {message}", file=sys.stderr)
    if error:
        print(f"Details: {error}", file=sys.stderr)


def log_language_start(language: str) -> None:
    """
    Log the start of translation for a specific language.
    
    Args:
        language: The target language code (e.g., "en", "fr", "ca")
        
    Example:
        >>> log_language_start("en")
        → Processing language: en
    """
    print(f"→ Processing language: {language}", file=sys.stdout)


def log_warning(message: str) -> None:
    """
    Log a warning message to stdout.
    
    Args:
        message: The warning message to display
        
    Example:
        >>> log_warning("Text truncated to 512 tokens")
        ⚠ Warning: Text truncated to 512 tokens
    """
    print(f"⚠ Warning: {message}", file=sys.stdout)
