"""Main entry point for JSON Translator."""
import argparse
import sys
from pathlib import Path
from typing import List

from src.config import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_FILE,
    DEFAULT_TARGET_LANGUAGES,
    SUPPORTED_LANGUAGES,
    get_input_path,
    get_output_path
)
from src.file_io import load_json_file, ensure_output_directory, serialize_json
from src.translation_engine import load_opus_mt, translate_batch
from src.translation_pipeline import translate_json_values
from src.logger import (
    log_progress,
    log_completion,
    log_error,
    log_language_start,
    log_warning
)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for JSON translation.
    
    Returns:
        argparse.Namespace: Parsed arguments with:
            - input: Path to source JSON file (default from config)
            - langs: List of target languages (default from config)
            - out_dir: Output directory path (default from config)
            - device: Device for inference - "cpu", "cuda", or None for auto-detect (default: None)
    """
    # Build default input path
    default_input = str(get_input_path())
    
    # Build supported languages string
    supported_langs_str = ", ".join(SUPPORTED_LANGUAGES)
    default_langs_str = " ".join(DEFAULT_TARGET_LANGUAGES)
    
    parser = argparse.ArgumentParser(
        description="Translate JSON files from Spanish to multiple languages while preserving structure and placeholders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s                          # Translate {DEFAULT_SOURCE_FILE} to {default_langs_str} in {DEFAULT_OUTPUT_DIR}/
  %(prog)s input.json               # Translate input.json to default languages
  %(prog)s --langs en fr            # Translate only to English and French
  %(prog)s --out-dir ./translations # Output to translations directory
  %(prog)s --device cpu             # Force CPU usage
        """
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        default=default_input,
        help=f"Path to source JSON file in Spanish (default: {default_input})"
    )
    
    parser.add_argument(
        "--langs",
        nargs="+",
        default=DEFAULT_TARGET_LANGUAGES,
        metavar="LANG",
        help=f"Target languages for translation (default: {default_langs_str}). Supported: {supported_langs_str}"
    )
    
    parser.add_argument(
        "--out-dir",
        default=DEFAULT_OUTPUT_DIR,
        metavar="DIR",
        help=f"Output directory for translated files (default: {DEFAULT_OUTPUT_DIR})"
    )
    
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default=None,
        help="Device for translation inference (default: auto-detect GPU/CPU)"
    )
    
    return parser.parse_args()


def main():
    """Main function to orchestrate JSON translation."""
    # Parse CLI arguments
    args = parse_arguments()
    
    log_progress(f"Starting JSON translation from {args.input}")
    log_progress(f"Target languages: {', '.join(args.langs)}")
    log_progress(f"Output directory: {args.out_dir}")
    log_progress(f"Device: {args.device if args.device else 'auto-detect'}")
    
    # Load source JSON file
    try:
        source_data = load_json_file(args.input)
        log_progress(f"✓ Loaded source file: {args.input}")
    except FileNotFoundError as e:
        log_error(f"Source file not found: {args.input}", e)
        sys.exit(1)
    except Exception as e:
        log_error(f"Failed to load source file: {args.input}", e)
        sys.exit(1)
    
    # Create output directory
    try:
        ensure_output_directory(args.out_dir)
        log_progress(f"✓ Output directory ready: {args.out_dir}")
    except Exception as e:
        log_error(f"Failed to create output directory: {args.out_dir}", e)
        sys.exit(1)
    
    # Track successful and failed translations
    successful_translations = []
    failed_translations = []
    
    # Loop through target languages
    for lang in args.langs:
        log_language_start(lang)
        
        try:
            # Load model for this language
            log_progress(f"  Loading translation model for {lang}...")
            model, tokenizer, device = load_opus_mt(lang, args.device)
            log_progress(f"  ✓ Model loaded (using {device})")
            
            # Create translation function for this language
            def translate_func(texts):
                return translate_batch(texts, model, tokenizer, device)
            
            # Translate JSON values
            log_progress(f"  Translating content...")
            translated_data = translate_json_values(source_data, translate_func)
            
            # Save output file
            output_filename = f"{lang}.json"
            output_path = str(Path(args.out_dir) / output_filename)
            serialize_json(translated_data, output_path)
            
            log_completion(lang, output_path)
            successful_translations.append(lang)
            
        except ValueError as e:
            # Unsupported language or invalid configuration
            log_error(f"Configuration error for language '{lang}'", e)
            failed_translations.append((lang, str(e)))
            continue
            
        except RuntimeError as e:
            # Model loading failure
            log_error(f"Failed to load model for language '{lang}'", e)
            failed_translations.append((lang, str(e)))
            continue
            
        except Exception as e:
            # Any other translation error
            log_error(f"Translation failed for language '{lang}'", e)
            failed_translations.append((lang, str(e)))
            continue
    
    # Report final summary
    print("\n" + "="*60)
    log_progress(f"Translation complete!")
    log_progress(f"Successful: {len(successful_translations)}/{len(args.langs)} languages")
    
    if successful_translations:
        log_progress(f"  ✓ {', '.join(successful_translations)}")
    
    if failed_translations:
        log_warning(f"Failed: {len(failed_translations)} languages")
        for lang, error in failed_translations:
            log_error(f"  ✗ {lang}: {error}")
        sys.exit(1)  # Exit with error if any translations failed


if __name__ == "__main__":
    main()
