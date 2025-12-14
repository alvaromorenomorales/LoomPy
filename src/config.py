"""Configuration settings for JSON Translator."""

from pathlib import Path

# ============================================================================
# DIRECTORY CONFIGURATION
# ============================================================================

# Default input directory for source JSON files
DEFAULT_INPUT_DIR = "input"

# Default output directory for translated JSON files
DEFAULT_OUTPUT_DIR = "output"

# Default source file name (when no input file is specified)
DEFAULT_SOURCE_FILE = "es.json"

# Test data directory
TEST_DATA_DIR = "test_data"


# ============================================================================
# TRANSLATION CONFIGURATION
# ============================================================================

# Default source language (ISO 639-1 code)
SOURCE_LANGUAGE = "es"  # Spanish

# Supported target languages (ISO 639-1 codes)
SUPPORTED_LANGUAGES = ["en", "fr", "ca"]  # English, French, Catalan

# Default target languages (when no languages are specified)
DEFAULT_TARGET_LANGUAGES = ["en", "fr", "ca"]

# Model name templates for Helsinki-NLP Opus-MT models
MODEL_TEMPLATES = {
    "en": "Helsinki-NLP/opus-mt-es-en",  # Spanish to English
    "fr": "Helsinki-NLP/opus-mt-es-fr",  # Spanish to French
    "ca": "Helsinki-NLP/opus-mt-es-ca",  # Spanish to Catalan
}


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Maximum sequence length for translation models (in tokens)
MAX_SEQUENCE_LENGTH = 512

# Batch size for translation (number of texts to translate at once)
TRANSLATION_BATCH_SIZE = 32

# Device selection: "cpu", "cuda", or None for auto-detect
DEFAULT_DEVICE = None  # Auto-detect GPU/CPU


# ============================================================================
# FILE FORMAT CONFIGURATION
# ============================================================================

# JSON indentation (number of spaces)
JSON_INDENT = 2

# File encoding
FILE_ENCODING = "utf-8"

# Ensure ASCII is False (preserve Unicode characters)
JSON_ENSURE_ASCII = False


# ============================================================================
# PLACEHOLDER CONFIGURATION
# ============================================================================

# Placeholder token used during translation to protect original placeholders
PLACEHOLDER_TOKEN = "PLACEHOLDER"

# Supported placeholder patterns (regex patterns)
PLACEHOLDER_PATTERNS = {
    "brace": r"\{[a-zA-Z_][a-zA-Z0-9_]*\}",  # {variable}
    "printf": r"%[sdifgcr]",  # %s, %d, %i, %f, %g, %c, %r
    "named": r"%\([a-zA-Z_][a-zA-Z0-9_]*\)[sdifgcr]",  # %(name)s
}


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Enable colored output in console
ENABLE_COLORED_OUTPUT = True

# Log level: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = "INFO"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_input_path(filename: str = None) -> Path:
    """
    Get the full path for an input file.
    
    Args:
        filename: Name of the input file. If None, uses DEFAULT_SOURCE_FILE
        
    Returns:
        Path object for the input file
        
    Example:
        >>> get_input_path("es.json")
        Path('input/es.json')
    """
    if filename is None:
        filename = DEFAULT_SOURCE_FILE
    return Path(DEFAULT_INPUT_DIR) / filename


def get_output_path(filename: str) -> Path:
    """
    Get the full path for an output file.
    
    Args:
        filename: Name of the output file
        
    Returns:
        Path object for the output file
        
    Example:
        >>> get_output_path("en.json")
        Path('output/en.json')
    """
    return Path(DEFAULT_OUTPUT_DIR) / filename


def get_test_data_path(filename: str) -> Path:
    """
    Get the full path for a test data file.
    
    Args:
        filename: Name of the test data file
        
    Returns:
        Path object for the test data file
        
    Example:
        >>> get_test_data_path("simple.json")
        Path('test_data/simple.json')
    """
    return Path(TEST_DATA_DIR) / filename


def get_model_name(target_language: str) -> str:
    """
    Get the Hugging Face model name for a target language.
    
    Args:
        target_language: ISO 639-1 language code (e.g., "en", "fr", "ca")
        
    Returns:
        Model name string
        
    Raises:
        ValueError: If the target language is not supported
        
    Example:
        >>> get_model_name("en")
        'Helsinki-NLP/opus-mt-es-en'
    """
    if target_language not in MODEL_TEMPLATES:
        raise ValueError(
            f"Unsupported target language: {target_language}. "
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
        )
    return MODEL_TEMPLATES[target_language]


def validate_language(language: str) -> bool:
    """
    Check if a language code is supported.
    
    Args:
        language: ISO 639-1 language code
        
    Returns:
        True if the language is supported, False otherwise
        
    Example:
        >>> validate_language("en")
        True
        >>> validate_language("de")
        False
    """
    return language in SUPPORTED_LANGUAGES
