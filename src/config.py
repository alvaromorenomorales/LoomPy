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
DEFAULT_SOURCE_LANGUAGE = "es"  # Spanish

# Supported source languages (ISO 639-1 codes)
SUPPORTED_SOURCE_LANGUAGES = ["es", "en", "fr", "ca", "de"]

# Supported target languages (ISO 639-1 codes) - kept for backwards compatibility
SUPPORTED_LANGUAGES = ["en", "fr", "ca"]  # English, French, Catalan

# Default target languages (when no languages are specified)
DEFAULT_TARGET_LANGUAGES = ["en", "fr", "ca"]

# Model name templates for Helsinki-NLP Opus-MT models
# Structure: {source_lang: {target_lang: model_name}}
MODEL_TEMPLATES = {
    "es": {
        "en": "Helsinki-NLP/opus-mt-es-en",  # Spanish to English
        "fr": "Helsinki-NLP/opus-mt-es-fr",  # Spanish to French
        "ca": "Helsinki-NLP/opus-mt-es-ca",  # Spanish to Catalan
        "de": "Helsinki-NLP/opus-mt-es-de",  # Spanish to German
    },
    "en": {
        "es": "Helsinki-NLP/opus-mt-en-es",  # English to Spanish
        "fr": "Helsinki-NLP/opus-mt-en-fr",  # English to French
        "de": "Helsinki-NLP/opus-mt-en-de",  # English to German
        "ca": "Helsinki-NLP/opus-mt-en-ca",  # English to Catalan
    },
    "fr": {
        "es": "Helsinki-NLP/opus-mt-fr-es",  # French to Spanish
        "en": "Helsinki-NLP/opus-mt-fr-en",  # French to English
        "de": "Helsinki-NLP/opus-mt-fr-de",  # French to German
    },
    "ca": {
        "es": "Helsinki-NLP/opus-mt-ca-es",  # Catalan to Spanish
        "en": "Helsinki-NLP/opus-mt-ca-en",  # Catalan to English
    },
    "de": {
        "es": "Helsinki-NLP/opus-mt-de-es",  # German to Spanish
        "en": "Helsinki-NLP/opus-mt-de-en",  # German to English
        "fr": "Helsinki-NLP/opus-mt-de-fr",  # German to French
    },
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

# Sort keys alphabetically
JSON_SORT_KEYS = True

# Allow duplicate keys (if True, keeps last occurrence; if False, raises error)
JSON_ALLOW_DUPLICATES = True


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
    Get the Hugging Face model name for a target language (legacy function).
    Assumes Spanish as source language for backwards compatibility.
    
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
    return get_model_name_for_pair(DEFAULT_SOURCE_LANGUAGE, target_language)


def get_model_name_for_pair(source_language: str, target_language: str) -> str:
    """
    Get the Hugging Face model name for a language pair.
    
    Args:
        source_language: ISO 639-1 source language code (e.g., "es", "en", "fr")
        target_language: ISO 639-1 target language code (e.g., "en", "fr", "ca")
        
    Returns:
        Model name string
        
    Raises:
        ValueError: If the language pair is not supported
        
    Example:
        >>> get_model_name_for_pair("es", "en")
        'Helsinki-NLP/opus-mt-es-en'
        >>> get_model_name_for_pair("en", "fr")
        'Helsinki-NLP/opus-mt-en-fr'
    """
    if source_language not in MODEL_TEMPLATES:
        raise ValueError(
            f"Unsupported source language: {source_language}. "
            f"Supported source languages: {', '.join(SUPPORTED_SOURCE_LANGUAGES)}"
        )
    
    if target_language not in MODEL_TEMPLATES[source_language]:
        available_targets = ', '.join(MODEL_TEMPLATES[source_language].keys())
        raise ValueError(
            f"Unsupported language pair: {source_language} -> {target_language}. "
            f"Available target languages for {source_language}: {available_targets}"
        )
    
    return MODEL_TEMPLATES[source_language][target_language]


def validate_language(language: str) -> bool:
    """
    Check if a language code is supported as a target language (legacy function).
    Assumes Spanish as source language for backwards compatibility.
    
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


def validate_language_pair(source_language: str, target_language: str) -> bool:
    """
    Check if a language pair is supported.
    
    Args:
        source_language: ISO 639-1 source language code
        target_language: ISO 639-1 target language code
        
    Returns:
        True if the language pair is supported, False otherwise
        
    Example:
        >>> validate_language_pair("es", "en")
        True
        >>> validate_language_pair("en", "es")
        True
        >>> validate_language_pair("es", "ja")
        False
    """
    return (source_language in MODEL_TEMPLATES and 
            target_language in MODEL_TEMPLATES.get(source_language, {}))


def validate_source_language(language: str) -> bool:
    """
    Check if a language code is supported as a source language.
    
    Args:
        language: ISO 639-1 language code
        
    Returns:
        True if the language is supported as source, False otherwise
        
    Example:
        >>> validate_source_language("es")
        True
        >>> validate_source_language("en")
        True
        >>> validate_source_language("ja")
        False
    """
    return language in SUPPORTED_SOURCE_LANGUAGES


def get_supported_target_languages(source_language: str) -> list:
    """
    Get list of supported target languages for a given source language.
    
    Args:
        source_language: ISO 639-1 source language code
        
    Returns:
        List of supported target language codes
        
    Example:
        >>> get_supported_target_languages("es")
        ['en', 'fr', 'ca', 'de']
        >>> get_supported_target_languages("en")
        ['es', 'fr', 'de', 'ca']
    """
    if source_language not in MODEL_TEMPLATES:
        return []
    return list(MODEL_TEMPLATES[source_language].keys())
