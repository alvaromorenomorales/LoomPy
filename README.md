# 🌐 LoomPy

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

A professional command-line tool that translates JSON files between multiple languages while preserving structure, keys, and placeholders. Built with SOLID principles in mind.

## Features

- **Structure Preservation**: Maintains exact JSON structure including nested objects and arrays
- **Key Preservation**: All JSON keys remain unchanged, only values are translated
- **Placeholder Protection**: Automatically detects and preserves placeholders in text
- **Multiple Languages**: Supports translation between multiple language pairs (Spanish, English, French, Catalan, German)
- **Real-time Progress Bar**: Visual progress tracking with percentage, item counts, and ETA
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

LoomPy can be used in two ways:

### Method 1: Standalone Script (Recommended)

Use the `loompy_translate.py` script directly:

```bash
python loompy_translate.py input/es.json --out-dir output --langs en fr ca
```

### Method 2: Module Usage

Use as a Python module with the full feature set:

```bash
python -m src.main
```

### Basic Usage

Translate `input/es.json` from Spanish to English, French, and Catalan:

**Standalone:**
```bash
python loompy_translate.py input/es.json --out-dir output --langs en fr ca
```

**Module:**
```bash
python -m src.main
```

This will create `output/en.json`, `output/fr.json`, and `output/ca.json`.

### Specify Source Language

Translate from English to Spanish and French:

```bash
python -m src.main input/en.json --source-lang en --langs es fr
```

Translate from French to English:

```bash
python -m src.main input/fr.json --source-lang fr --langs en
```

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
python -m src.main input/es.json --source-lang es --langs en fr --out-dir custom_output --device cuda
```

Translate from English to German:

```bash
python -m src.main input/en.json --source-lang en --langs de --device cpu
```

### Progress Bar

During translation, you'll see a real-time progress bar showing:

```
▶ Translating to EN
  Total items: 1902
  [████████████████████░░░░░░░░░░░░░░░░░░░░] 47.1% | 896/1902 items | ETA: 02:30
```

The progress bar displays:
- **Task name**: Current language being translated
- **Visual bar**: Graphical representation of progress
- **Percentage**: Completion percentage
- **Item count**: Number of strings processed / total strings
- **ETA**: Estimated time remaining (calculated dynamically based on processing speed)

When translation completes:
```
✓ Completado en 5m 0s
```

## Workflow: From Raw to Translated

The recommended workflow for processing your JSON files (e.g. `input/es.json`) to obtain a final translated version (e.g. `output/en.json`) is as follows:

### 1. File Preparation (Sort and Clean)
Before translation, your input file (`es.json`) should be valid.
The tool automatically handles sorting and cleaning of duplicates.

**To clean and sort your input file:**
1.  **Duplicates:** If your file has duplicate keys, the tool will automatically clean them (keeping the last occurrence) without error.
2.  **Sorting:** The tool automatically sorts all keys alphabetically in the output.
3.  If you want to "normalize" your input file (sort and clean it) before translation, you can run a dummy translation or just rely on the output being clean.

### 2. Translation
Once your input file is clean, run the translation command. The output file (`en.json`) will be:
*   Translated.
*   **Sorted alphabetically by key** (for consistent diffs).
*   **Clean of duplicates** (guaranteed by the input validation).

**Example Command:**
```bash
python -m src.main input/es.json --langs en
```

This will produce `output/en.json`, which is the final, clean, sorted, and translated version.

### 3. Clean and Sort Source File (Recommended)

You can use the tool to "normalize" your source file (sort keys and remove duplicates) without running a translation.

**Option A: Update the source file in-place (Risky but convenient)**
This will overwrite `input/es.json` with the sorted and cleaned version.
```bash
python -m src.main input/es.json --update-source
```

**Option B: Generate a clean copy in output (Safe)**
This will create `output/es.json` (sorted and clean) without modifying your original file.
```bash
python -m src.main input/es.json --output-source
```

You can also combine these with translation:
```bash
# Translate to English AND update the source file
python -m src.main input/es.json --langs en --update-source
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

The tool supports translation between the following language pairs:

| Source Language | Target Languages | Notes |
|----------------|------------------|-------|
| **Spanish (es)** | English (en), French (fr), Catalan (ca), German (de) | Default source language |
| **English (en)** | Spanish (es), French (fr), German (de), Catalan (ca) | |
| **French (fr)** | Spanish (es), English (en), German (de) | |
| **Catalan (ca)** | Spanish (es), English (en) | |
| **German (de)** | Spanish (es), English (en), French (fr) | |

All translations use Helsinki-NLP Opus-MT models from Hugging Face.

### Usage Examples by Language Pair

```bash
# Spanish to English
python -m src.main input/es.json --source-lang es --langs en

# English to Spanish and French
python -m src.main input/en.json --source-lang en --langs es fr

# French to English
python -m src.main input/fr.json --source-lang fr --langs en

# German to Spanish
python -m src.main input/de.json --source-lang de --langs es
```

## Performance

Typical performance on a modern CPU:

- **Small files** (<100 strings): <10 seconds per language
- **Medium files** (100-1000 strings): 30-60 seconds per language
- **Large files** (>1000 strings): 1-5 minutes per language

GPU acceleration can provide 3-10x speedup depending on hardware.

## Limitations

- **Model availability**: Not all language pairs have Opus-MT models available
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
│   ├── progress_bar.py            # Real-time progress tracking and visualization
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The translation models used are from Helsinki-NLP and may have their own licenses.

## Acknowledgments

- Translation models: [Helsinki-NLP Opus-MT](https://github.com/Helsinki-NLP/Opus-MT)
- Transformers library: [Hugging Face](https://huggingface.co/transformers/)
- Property-based testing: [Hypothesis](https://hypothesis.readthedocs.io/)
