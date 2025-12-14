# Configuration Guide

This document explains how to configure the JSON Translator using the centralized configuration file.

## Configuration File

All configuration settings are centralized in `src/config.py`. This makes it easy to modify the behavior of the translator without changing code in multiple places.

## Configuration Sections

### 1. Directory Configuration

Control where input and output files are located:

```python
# Default input directory for source JSON files
DEFAULT_INPUT_DIR = "input"

# Default output directory for translated JSON files
DEFAULT_OUTPUT_DIR = "output"

# Default source file name (when no input file is specified)
DEFAULT_SOURCE_FILE = "es.json"

# Test data directory
TEST_DATA_DIR = "test_data"
```

**Usage:**
- Place your Spanish JSON files in the `input/` directory
- Translated files will be generated in the `output/` directory
- When you run `python -m src.main` without arguments, it looks for `input/es.json`

### 2. Translation Configuration

Configure supported languages and translation behavior:

```python
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
```

**To add a new language:**
1. Add the language code to `SUPPORTED_LANGUAGES`
2. Add the Hugging Face model name to `MODEL_TEMPLATES`
3. Optionally add it to `DEFAULT_TARGET_LANGUAGES`

Example - Adding German:
```python
SUPPORTED_LANGUAGES = ["en", "fr", "ca", "de"]

MODEL_TEMPLATES = {
    "en": "Helsinki-NLP/opus-mt-es-en",
    "fr": "Helsinki-NLP/opus-mt-es-fr",
    "ca": "Helsinki-NLP/opus-mt-es-ca",
    "de": "Helsinki-NLP/opus-mt-es-de",  # Add this
}
```

### 3. Model Configuration

Control translation model behavior:

```python
# Maximum sequence length for translation models (in tokens)
MAX_SEQUENCE_LENGTH = 512

# Batch size for translation (number of texts to translate at once)
TRANSLATION_BATCH_SIZE = 32

# Device selection: "cpu", "cuda", or None for auto-detect
DEFAULT_DEVICE = None  # Auto-detect GPU/CPU
```

**Performance tuning:**
- Increase `TRANSLATION_BATCH_SIZE` for faster translation (requires more memory)
- Decrease `TRANSLATION_BATCH_SIZE` if you encounter out-of-memory errors
- `MAX_SEQUENCE_LENGTH` is limited by the model architecture (512 tokens for Opus-MT)

### 4. File Format Configuration

Control JSON output formatting:

```python
# JSON indentation (number of spaces)
JSON_INDENT = 2

# File encoding
FILE_ENCODING = "utf-8"

# Ensure ASCII is False (preserve Unicode characters)
JSON_ENSURE_ASCII = False
```

**Customization:**
- Change `JSON_INDENT` to 4 for wider indentation
- `JSON_ENSURE_ASCII = False` ensures Unicode characters (é, ñ, 中, etc.) are preserved
- `FILE_ENCODING` should remain "utf-8" for maximum compatibility

### 5. Placeholder Configuration

Configure how placeholders are detected and protected:

```python
# Placeholder token used during translation to protect original placeholders
PLACEHOLDER_TOKEN = "PLACEHOLDER"

# Supported placeholder patterns (regex patterns)
PLACEHOLDER_PATTERNS = {
    "brace": r"\{[a-zA-Z_][a-zA-Z0-9_]*\}",  # {variable}
    "printf": r"%[sdifgcr]",  # %s, %d, %i, %f, %g, %c, %r
    "named": r"%\([a-zA-Z_][a-zA-Z0-9_]*\)[sdifgcr]",  # %(name)s
}
```

**To add a new placeholder format:**
Add a new entry to `PLACEHOLDER_PATTERNS` with a regex pattern.

Example - Adding Angular placeholders:
```python
PLACEHOLDER_PATTERNS = {
    "brace": r"\{[a-zA-Z_][a-zA-Z0-9_]*\}",
    "printf": r"%[sdifgcr]",
    "named": r"%\([a-zA-Z_][a-zA-Z0-9_]*\)[sdifgcr]",
    "angular": r"\{\{[a-zA-Z_][a-zA-Z0-9_]*\}\}",  # {{variable}}
}
```

### 6. Logging Configuration

Control console output:

```python
# Enable colored output in console
ENABLE_COLORED_OUTPUT = True

# Log level: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_LEVEL = "INFO"
```

## Helper Functions

The config module provides helper functions for common operations:

### `get_input_path(filename=None)`

Get the full path for an input file.

```python
from src.config import get_input_path

# Get default input file path
path = get_input_path()  # Returns: Path('input/es.json')

# Get custom input file path
path = get_input_path("custom.json")  # Returns: Path('input/custom.json')
```

### `get_output_path(filename)`

Get the full path for an output file.

```python
from src.config import get_output_path

path = get_output_path("en.json")  # Returns: Path('output/en.json')
```

### `get_test_data_path(filename)`

Get the full path for a test data file.

```python
from src.config import get_test_data_path

path = get_test_data_path("simple.json")  # Returns: Path('test_data/simple.json')
```

### `get_model_name(target_language)`

Get the Hugging Face model name for a target language.

```python
from src.config import get_model_name

model = get_model_name("en")  # Returns: 'Helsinki-NLP/opus-mt-es-en'
```

### `validate_language(language)`

Check if a language code is supported.

```python
from src.config import validate_language

is_valid = validate_language("en")  # Returns: True
is_valid = validate_language("de")  # Returns: False (if not configured)
```

## Using Configuration in Your Code

### In Application Code

```python
from src.config import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    SUPPORTED_LANGUAGES,
    get_input_path,
    get_output_path
)

# Use configuration values
input_file = get_input_path("es.json")
output_file = get_output_path("en.json")

print(f"Supported languages: {SUPPORTED_LANGUAGES}")
```

### In Tests

```python
from src.config import (
    get_test_data_path,
    SUPPORTED_LANGUAGES,
    MAX_SEQUENCE_LENGTH
)

def test_translation():
    # Use test data path
    test_file = get_test_data_path("simple.json")
    
    # Use configuration values in assertions
    assert len(SUPPORTED_LANGUAGES) >= 3
    assert MAX_SEQUENCE_LENGTH == 512
```

## Best Practices

1. **Don't hardcode paths**: Always use helper functions like `get_input_path()` instead of hardcoding `"input/file.json"`

2. **Don't hardcode language lists**: Use `SUPPORTED_LANGUAGES` from config instead of `["en", "fr", "ca"]`

3. **Don't hardcode model names**: Use `get_model_name(lang)` instead of hardcoding model strings

4. **Centralize changes**: When adding features, update `config.py` first, then use those values in your code

5. **Document changes**: If you modify configuration values, update this document

## Environment-Specific Configuration

For different environments (development, testing, production), you can:

1. **Use environment variables** (recommended):
```python
import os
DEFAULT_INPUT_DIR = os.getenv("TRANSLATOR_INPUT_DIR", "input")
```

2. **Create environment-specific config files**:
- `config.py` - Base configuration
- `config_dev.py` - Development overrides
- `config_prod.py` - Production overrides

3. **Use command-line arguments** (already implemented):
```bash
python -m src.main --out-dir ./custom_output
```

## Troubleshooting

### "Unsupported target language" error

**Problem**: You specified a language that's not in `SUPPORTED_LANGUAGES`.

**Solution**: Add the language to `SUPPORTED_LANGUAGES` and `MODEL_TEMPLATES` in `config.py`.

### Output files in wrong directory

**Problem**: Files are being created in the wrong location.

**Solution**: Check `DEFAULT_OUTPUT_DIR` in `config.py` or use `--out-dir` flag.

### Model not found

**Problem**: Hugging Face can't find the model.

**Solution**: Verify the model name in `MODEL_TEMPLATES` is correct. Check [Hugging Face](https://huggingface.co/Helsinki-NLP) for available models.

## Examples

### Example 1: Change default directories

```python
# In src/config.py
DEFAULT_INPUT_DIR = "translations/source"
DEFAULT_OUTPUT_DIR = "translations/output"
```

### Example 2: Add Italian support

```python
# In src/config.py
SUPPORTED_LANGUAGES = ["en", "fr", "ca", "it"]

MODEL_TEMPLATES = {
    "en": "Helsinki-NLP/opus-mt-es-en",
    "fr": "Helsinki-NLP/opus-mt-es-fr",
    "ca": "Helsinki-NLP/opus-mt-es-ca",
    "it": "Helsinki-NLP/opus-mt-es-it",  # Add Italian
}

DEFAULT_TARGET_LANGUAGES = ["en", "fr", "ca", "it"]
```

### Example 3: Optimize for speed

```python
# In src/config.py
TRANSLATION_BATCH_SIZE = 64  # Increase batch size (requires more memory)
DEFAULT_DEVICE = "cuda"  # Force GPU usage
```

### Example 4: Optimize for memory

```python
# In src/config.py
TRANSLATION_BATCH_SIZE = 8  # Decrease batch size
DEFAULT_DEVICE = "cpu"  # Force CPU usage
```
