import json
from pathlib import Path

# ============================================================================
# USER CONFIGURATION LOADING
# ============================================================================

def load_user_config_from_file() -> dict:
    """
    Load configuration from config.json if it exists.
    """
    config_path = Path("config.json")
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

_USER_CONFIG = load_user_config_from_file()

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

# Model directory (for local models like CTranslate2)
MODEL_DIR = "models"
NLLB_MODEL_NAME = "nllb-200-600M-ct2"


# ============================================================================
# TRANSLATION CONFIGURATION
# ============================================================================

# Default source language (ISO 639-1 code or NLLB code)
DEFAULT_SOURCE_LANGUAGE = _USER_CONFIG.get("default_source_language", "es")

def _get_fallback_names() -> dict:
    """Extract language names from SUPPORTED_LANGUAGES.md if available."""
    mapping = {}
    md_path = Path("SUPPORTED_LANGUAGES.md")
    if md_path.exists():
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line and "`" in line:
                        parts = [p.strip() for p in line.split("|")]
                        if len(parts) >= 3:
                            code = parts[1].replace("`", "").strip()
                            name = parts[2].strip()
                            if code and name:
                                mapping[code] = name
        except Exception:
            pass
    return mapping

# Load names from database
_FALLBACK_NAMES = _get_fallback_names()

# All 200+ supported languages from our database
ALL_SUPPORTED_LANGUAGES = sorted(list(_FALLBACK_NAMES.keys()))

# Use defaults from config as the primary list for UX (Quick list)
_SOURCE_DEF = _USER_CONFIG.get("default_source_language", "spa_Latn")
_TARGET_DEFS = _USER_CONFIG.get("default_target_languages", ["eng_Latn", "fra_Latn"])

# Primary CLI list (union of defaults)
_UNION = sorted(list(set([_SOURCE_DEF] + _TARGET_DEFS)))
SUPPORTED_SOURCE_LANGUAGES = _UNION
SUPPORTED_LANGUAGES = _UNION

# Language name resolver (can resolve any from the 200+)
LANGUAGE_NAMES = _FALLBACK_NAMES

# Export defaults for CLI usage
DEFAULT_TARGET_LANGUAGES = _TARGET_DEFS


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
    """
    if filename is None:
        filename = DEFAULT_SOURCE_FILE
    return Path(DEFAULT_INPUT_DIR) / filename


def get_output_path(filename: str) -> Path:
    """
    Get the full path for an output file.
    """
    return Path(DEFAULT_OUTPUT_DIR) / filename


def get_test_data_path(filename: str) -> Path:
    """
    Get the full path for a test data file.
    """
    return Path(TEST_DATA_DIR) / filename


def get_model_path(model_name: str = None) -> Path:
    """
    Get the full path for a local model.
    """
    if model_name is None:
        model_name = NLLB_MODEL_NAME
    return Path(MODEL_DIR) / model_name


def validate_language_pair(source_language: str, target_language: str) -> bool:
    """
    Check if a language pair is supported.
    """
    return (source_language in SUPPORTED_SOURCE_LANGUAGES and 
            target_language in (SUPPORTED_SOURCE_LANGUAGES + SUPPORTED_LANGUAGES))


def validate_source_language(language: str) -> bool:
    """
    Check if a language code is supported as a source language.
    """
    return language in SUPPORTED_SOURCE_LANGUAGES


def get_supported_target_languages(source_language: str) -> list:
    """
    Get list of supported target languages for a given source language.
    """
    return sorted(list(set(SUPPORTED_SOURCE_LANGUAGES + SUPPORTED_LANGUAGES)))
