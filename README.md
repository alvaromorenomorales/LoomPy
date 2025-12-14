# JSON Translator

A command-line tool that translates JSON files from Spanish to multiple languages (English, French, and Catalan) while preserving structure, keys, and placeholders.

## Features

- **Structure Preservation**: Maintains exact JSON structure including nested objects and arrays
- **Key Preservation**: All JSON keys remain unchanged, only values are translated
- **Placeholder Protection**: Automatically detects and preserves placeholders in text
- **Multiple Languages**: Supports English (en), French (fr), and Catalan (ca)
- **Line-by-Line Consistency**: Output files maintain the same line count and key positions as source
- **GPU Acceleration**: Automatically uses GPU when available for faster translation
- **Batch Processing**: Efficiently processes multiple texts in batches
- **Error Recovery**: Continues with other languages if one fails

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
- `transformers>=4.30.0` - Hugging Face transformers library
- `torch>=2.0.0` - PyTorch for model inference
- `sentencepiece>=0.1.99` - Tokenization for translation models

**Development Dependencies:**
- `pytest>=7.4.0` - Testing framework
- `hypothesis>=6.82.0` - Property-based testing
- `pytest-cov>=4.1.0` - Test coverage

### GPU Support (Optional)

For GPU acceleration, install CUDA-compatible PyTorch:

```bash
# For CUDA 11.8
pip install torch --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

See [PyTorch installation guide](https://pytorch.org/get-started/locally/) for more options.

## Project Structure

The project uses a configuration-based approach with dedicated directories:

```
.
├── input/          # Place your source JSON files here (e.g., es.json)
├── output/         # Translated files are generated here
├── src/
│   ├── config.py   # Centralized configuration (directories, languages, models)
│   ├── main.py     # CLI entry point
│   └── ...         # Other modules
└── test_data/      # Example JSON files for testing
```

### Configuration

All important settings are centralized in `src/config.py`:

- **Directories**: `DEFAULT_INPUT_DIR`, `DEFAULT_OUTPUT_DIR`
- **Languages**: `SUPPORTED_LANGUAGES`, `DEFAULT_TARGET_LANGUAGES`
- **Models**: `MODEL_TEMPLATES` (Hugging Face model names)
- **Translation**: `MAX_SEQUENCE_LENGTH`, `TRANSLATION_BATCH_SIZE`
- **File Format**: `JSON_INDENT`, `FILE_ENCODING`

You can modify these settings to customize the behavior of the translator.

## Usage

### Basic Usage

Translate `input/es.json` to English, French, and Catalan:

```bash
python -m src.main
```

This will create `output/en.json`, `output/fr.json`, and `output/ca.json`.

### Specify Input File

```bash
python -m src.main input/custom.json
```

### Select Target Languages

Translate only to English and French:

```bash
python -m src.main --langs en fr
```

Translate only to Catalan:

```bash
python -m src.main --langs ca
```

### Specify Output Directory

```bash
python -m src.main --out-dir ./translations
```

The output directory will be created automatically if it doesn't exist.

### Force CPU Usage

```bash
python -m src.main --device cpu
```

### Complete Example

```bash
python -m src.main input/es.json --langs en fr --out-dir custom_output --device cuda
```

## Supported Placeholder Formats

The translator automatically detects and preserves the following placeholder formats:

### 1. Brace Format `{variable}`

Python/JavaScript style placeholders:

```json
{
  "greeting": "Hola {name}, bienvenido"
}
```

Output:
```json
{
  "greeting": "Hello {name}, welcome"
}
```

### 2. Printf Format `%s`, `%d`, `%f`, etc.

C-style format specifiers:

```json
{
  "message": "Tienes %s mensajes nuevos",
  "count": "Total: %d items"
}
```

Supported specifiers: `%s` (string), `%d` (decimal), `%i` (integer), `%f` (float), `%g` (general), `%c` (character), `%r` (repr)

### 3. Named Format `%(name)s`

Python named format strings:

```json
{
  "status": "Usuario %(username)s tiene %(count)d mensajes"
}
```

Output:
```json
{
  "status": "User %(username)s has %(count)d messages"
}
```

### Multiple Placeholders

Multiple placeholders in a single string are preserved in their correct positions:

```json
{
  "complex": "Hola {user}, tienes %d mensajes de %(sender)s"
}
```

## Input File Format

### Requirements

- Valid JSON format
- UTF-8 encoding
- Spanish text in string values

### Supported Structures

**Simple objects:**
```json
{
  "key1": "valor1",
  "key2": "valor2"
}
```

**Nested objects:**
```json
{
  "user": {
    "name": "Nombre",
    "profile": {
      "bio": "Biografía"
    }
  }
}
```

**Arrays:**
```json
{
  "items": [
    "primero",
    "segundo",
    "tercero"
  ]
}
```

**Mixed types:**
```json
{
  "text": "Hola",
  "count": 42,
  "active": true,
  "data": null
}
```

Only string values are translated. Numbers, booleans, and null values remain unchanged.

## Output Format

Output files maintain:
- **Same structure** as input
- **Same key names** (untranslated)
- **Same line count** as input
- **Same key order** as input
- **2-space indentation**
- **UTF-8 encoding** without escaping Unicode characters

## Examples

### Example 1: Simple Translation

**Input (`input/es.json`):**
```json
{
  "greeting": "Hola",
  "farewell": "Adiós"
}
```

**Command:**
```bash
python -m src.main --langs en
```

**Output (`output/en.json`):**
```json
{
  "greeting": "Hello",
  "farewell": "Goodbye"
}
```

### Example 2: With Placeholders

**Input (`input/es.json`):**
```json
{
  "welcome": "Bienvenido {name}",
  "messages": "Tienes %d mensajes nuevos"
}
```

**Output (`output/en.json`):**
```json
{
  "welcome": "Welcome {name}",
  "messages": "You have %d new messages"
}
```

### Example 3: Nested Structure

**Input (`input/es.json`):**
```json
{
  "app": {
    "title": "Mi Aplicación",
    "menu": {
      "home": "Inicio",
      "settings": "Configuración"
    }
  }
}
```

**Output (`output/en.json`):**
```json
{
  "app": {
    "title": "My Application",
    "menu": {
      "home": "Home",
      "settings": "Settings"
    }
  }
}
```

## Troubleshooting

### Issue: "Source file not found"

**Problem:** The input file doesn't exist or path is incorrect.

**Solution:**
- Check the file path is correct
- Use absolute path if needed: `python -m src.main /full/path/to/es.json`
- Ensure file has `.json` extension

### Issue: "Failed to load source file: Invalid JSON"

**Problem:** The input file contains malformed JSON.

**Solution:**
- Validate JSON syntax using a JSON validator
- Check for:
  - Missing commas between items
  - Trailing commas (not allowed in JSON)
  - Unquoted keys
  - Single quotes instead of double quotes
- Use a JSON formatter to fix formatting

### Issue: "Failed to load model"

**Problem:** Translation model cannot be downloaded or loaded.

**Solution:**
- Check internet connection (models download on first use)
- Verify disk space (models are ~300MB each)
- Try forcing CPU: `python -m src.main --device cpu`
- Check Hugging Face status: https://status.huggingface.co/

### Issue: "CUDA out of memory"

**Problem:** GPU doesn't have enough memory for the model.

**Solution:**
- Force CPU usage: `python -m src.main --device cpu`
- Close other GPU-intensive applications
- Process smaller files
- Upgrade GPU memory if possible

### Issue: "Text truncated" warning

**Problem:** Some text exceeds the model's maximum length (512 tokens).

**Solution:**
- This is a warning, not an error - translation continues
- Long texts are automatically truncated
- Consider splitting very long strings into smaller parts in your JSON
- Note: Most translation strings are well under this limit

### Issue: Placeholders not preserved correctly

**Problem:** Placeholders appear translated or corrupted in output.

**Solution:**
- Verify placeholder format is supported (see Supported Placeholder Formats)
- Check placeholder syntax is correct
- Report issue with example if format should be supported

### Issue: Output directory permission denied

**Problem:** Cannot create output directory or write files.

**Solution:**
- Check write permissions for output directory
- Use a different output directory: `--out-dir ~/translations`
- Run with appropriate permissions
- On Windows, avoid system directories

### Issue: Slow translation speed

**Problem:** Translation takes longer than expected.

**Solution:**
- Enable GPU if available (automatic by default)
- Check GPU is being used (look for "using cuda" in output)
- First run is slower (downloads models)
- Subsequent runs use cached models
- Large files naturally take longer

### Issue: Translation quality issues

**Problem:** Translations are incorrect or awkward.

**Solution:**
- The tool uses Helsinki-NLP Opus-MT models
- Translation quality depends on the model
- For critical translations, consider:
  - Manual review and editing
  - Professional translation services
  - Fine-tuning models for your domain
- Report systematic issues to the Opus-MT project

### Issue: Unicode characters corrupted

**Problem:** Special characters (accents, emojis) appear incorrectly.

**Solution:**
- Ensure input file is UTF-8 encoded
- Check terminal supports UTF-8 output
- Output files are always UTF-8 with proper Unicode preservation
- Use a UTF-8 compatible text editor to view files

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_translation_pipeline.py

# Run property-based tests
pytest tests/test_line_count_property.py
```

## Supported Languages

Currently supported target languages:

- **English (en)**: Spanish → English
- **French (fr)**: Spanish → French  
- **Catalan (ca)**: Spanish → Catalan

All translations use Helsinki-NLP Opus-MT models optimized for Spanish source text.

## Performance

Typical performance on a modern CPU:

- **Small files** (<100 strings): <10 seconds per language
- **Medium files** (100-1000 strings): 30-60 seconds per language
- **Large files** (>1000 strings): 1-5 minutes per language

GPU acceleration can provide 3-10x speedup depending on hardware.

## Limitations

- **Source language**: Only Spanish is supported as source language
- **Target languages**: Limited to English, French, and Catalan
- **Max text length**: 512 tokens per string (longer texts are truncated with warning)
- **Sequential processing**: Languages are translated one at a time
- **Model quality**: Translation quality depends on Opus-MT models

## Detailed Project Structure

```
.
├── input/                         # Source JSON files directory
│   ├── .gitkeep                   # Keeps directory in git
│   └── es.json                    # Your Spanish source file
├── output/                        # Generated translation files
│   ├── .gitkeep                   # Keeps directory in git
│   ├── en.json                    # English translation (generated)
│   ├── fr.json                    # French translation (generated)
│   └── ca.json                    # Catalan translation (generated)
├── src/
│   ├── config.py                  # Centralized configuration
│   ├── main.py                    # CLI entry point
│   ├── translation_pipeline.py    # Core translation orchestration
│   ├── translation_engine.py      # Model loading and batch translation
│   ├── placeholder_protection.py  # Placeholder detection and restoration
│   ├── json_traversal.py          # JSON structure navigation
│   ├── file_io.py                 # File loading and serialization
│   └── logger.py                  # Logging utilities
├── tests/                         # Test suite
├── test_data/                     # Example JSON files for testing
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Contributing

When contributing, ensure:

1. All tests pass: `pytest`
2. Code follows existing style
3. New features include tests
4. Documentation is updated

## License

This project uses Helsinki-NLP Opus-MT models which are licensed under Apache 2.0.

## Acknowledgments

- Translation models: [Helsinki-NLP Opus-MT](https://github.com/Helsinki-NLP/Opus-MT)
- Transformers library: [Hugging Face](https://huggingface.co/transformers/)
- Property-based testing: [Hypothesis](https://hypothesis.readthedocs.io/)
