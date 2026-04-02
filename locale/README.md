# CLI Localizations

This directory contains the localization files for the LoomPy v2 CLI.

## Adding a New Language to the CLI

To add support for a new language in the CLI:

1.  Identify the FLORES-200 code for the language (e.g., `spa_Latn` for Spanish, `eng_Latn` for English). You can find these in `SUPPORTED_LANGUAGES.md`.
2.  Create a new JSON file in this directory with that code (e.g., `deu_Latn.json` for German).
3.  Copy the keys from `eng_Latn.json` and translate the values.
4.  Ensure the language is also configured in the main `config.json` file in the root directory.

The system will automatically detect any `.json` file in this directory and offer it as an option in the interactive CLI.

## Current Locales

- `eng_Latn.json`: English (Default)
- `spa_Latn.json`: Spanish
- `fra_Latn.json`: French

## Technical Details

The localization system in `src/locale.py` scans this directory at startup. It uses the file's base name (stem) as the locale code. If your system locale matches one of the available codes, it will be selected automatically.
