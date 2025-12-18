"""Main entry point for JSON Translator."""
import argparse
import sys
from pathlib import Path
from typing import List

from src.config import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_FILE,
    DEFAULT_SOURCE_LANGUAGE,
    DEFAULT_TARGET_LANGUAGES,
    SUPPORTED_LANGUAGES,
    SUPPORTED_SOURCE_LANGUAGES,
    get_input_path,
    get_output_path,
    validate_language_pair,
    validate_source_language,
    get_supported_target_languages
)
from src.file_io import load_json_file, ensure_output_directory, serialize_json
from src.translation_engine import OpusMTProvider
from src.translation_pipeline import translate_json_values
from src.json_traversal import collect_string_paths
from src.progress_bar import ProgressBar
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
            - source_lang: Source language code (default from config)
            - langs: List of target languages (default from config)
            - out_dir: Output directory path (default from config)
            - device: Device for inference - "cpu", "cuda", or None for auto-detect (default: None)
    """
    # Build default input path
    default_input = str(get_input_path())
    
    # Build supported languages string
    supported_source_langs_str = ", ".join(SUPPORTED_SOURCE_LANGUAGES)
    supported_langs_str = ", ".join(SUPPORTED_LANGUAGES)
    default_langs_str = " ".join(DEFAULT_TARGET_LANGUAGES)
    
    parser = argparse.ArgumentParser(
        description="Translate JSON files between multiple languages while preserving structure and placeholders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s                                    # Translate {DEFAULT_SOURCE_FILE} from {DEFAULT_SOURCE_LANGUAGE} to {default_langs_str}
  %(prog)s input.json                         # Translate input.json to default languages
  %(prog)s --source-lang en --langs es fr     # Translate from English to Spanish and French
  %(prog)s --langs en fr                      # Translate only to English and French
  %(prog)s --out-dir ./translations           # Output to translations directory
  %(prog)s --device cpu                       # Force CPU usage
        """
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        default=default_input,
        help=f"Path to source JSON file in Spanish (default: {default_input})"
    )
    
    parser.add_argument(
        "--source-lang",
        default=DEFAULT_SOURCE_LANGUAGE,
        metavar="LANG",
        help=f"Source language for translation (default: {DEFAULT_SOURCE_LANGUAGE}). Supported: {supported_source_langs_str}"
    )
    
    parser.add_argument(
        "--langs",
        "--target-langs",
        nargs="+",
        default=DEFAULT_TARGET_LANGUAGES,
        metavar="LANG",
        dest="langs",
        help=f"Target languages for translation (default: {default_langs_str}). Available targets depend on source language."
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

    parser.add_argument(
        "--update-source",
        action="store_true",
        help="Update the source file with sorted keys and cleaned duplicates (overwrites input file)"
    )

    parser.add_argument(
        "--output-source",
        action="store_true",
        help="Save the clean and sorted source file to the output directory"
    )
    
    return parser.parse_args()


def main():
    """Main function to orchestrate JSON translation."""
    # Parse CLI arguments
    args = parse_arguments()
    
    # Validate source language
    if not validate_source_language(args.source_lang):
        log_error(
            f"Unsupported source language: {args.source_lang}",
            ValueError(f"Supported source languages: {', '.join(SUPPORTED_SOURCE_LANGUAGES)}")
        )
        sys.exit(1)
    
    # Validate target languages
    supported_targets = get_supported_target_languages(args.source_lang)
    invalid_targets = [lang for lang in args.langs if not validate_language_pair(args.source_lang, lang)]
    
    if invalid_targets:
        log_error(
            f"Unsupported target language(s) for source '{args.source_lang}': {', '.join(invalid_targets)}",
            ValueError(f"Available target languages for {args.source_lang}: {', '.join(supported_targets)}")
        )
        sys.exit(1)
    
    log_progress(f"Starting JSON translation from {args.input}")
    log_progress(f"Source language: {args.source_lang}")
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
    except Exception as e:
        log_error(f"Failed to create output directory: {args.out_dir}", e)
        sys.exit(1)

    # Handle source file updates/output if requested
    if args.update_source:
        try:
            log_progress(f"Updating source file: {args.input}")
            serialize_json(source_data, args.input)
            log_progress(f"✓ Source file updated (sorted and cleaned)")
        except Exception as e:
            log_error(f"Failed to update source file: {args.input}", e)

    if args.output_source:
        try:
            source_filename = Path(args.input).name
            output_source_path = str(Path(args.out_dir) / source_filename)
            log_progress(f"Saving source copy to: {output_source_path}")
            serialize_json(source_data, output_source_path)
            log_progress(f"✓ Source file saved to output")
        except Exception as e:
            log_error(f"Failed to save source file to output", e)
    
    # If no languages specified and only cleaning requested, exit early
    if not args.langs and (args.update_source or args.output_source):
        log_completion("Cleanup", "Finished")
        sys.exit(0)
    
    # Track successful and failed translations
    successful_translations = []
    failed_translations = []
    
    # Initialize progress bar
    progress_bar = ProgressBar(bar_width=40, enable_colors=True)
    
    # Loop through target languages
    for lang in args.langs:
        log_language_start(lang)
        
        try:
            # Count total strings to translate
            total_strings = len(collect_string_paths(source_data))
            
            # Start progress tracking for this language
            task_name = f"Traduciendo a {lang.upper()}"
            progress_bar.start_task(task_name, total_strings)
            
            # Load model for this language
            log_progress(f"  Cargando modelo de traducción {args.source_lang} → {lang}...")
            
            # Dependency Injection: Instantiate provider (in a real DI container this would be injected)
            provider = OpusMTProvider()
            device_used = provider.load_model(args.source_lang, lang, args.device)
            
            log_progress(f"  ✓ Modelo cargado (usando {device_used})")
            
            # Create translation function with progress callback
            def translate_func(texts):
                return provider.translate_batch(
                    texts, 
                    progress_callback=lambda count: progress_bar.update(count)
                )
            
            # Translate JSON values with progress tracking
            log_progress(f"  Traduciendo contenido...")
            translated_data = translate_json_values(
                source_data, 
                translate_func,
                progress_callback=lambda processed, total: progress_bar.update(processed)
            )
            
            # Mark task as complete
            progress_bar.complete()
            
            # Save output file
            output_filename = f"{lang}.json"
            output_path = str(Path(args.out_dir) / output_filename)
            serialize_json(translated_data, output_path)
            
            log_completion(lang, output_path)
            successful_translations.append(lang)
            
        except ValueError as e:
            # Unsupported language or invalid configuration
            log_error(f"Error de configuración para el idioma '{lang}'", e)
            failed_translations.append((lang, str(e)))
            continue
            
        except RuntimeError as e:
            # Model loading failure
            log_error(f"Error al cargar el modelo para el idioma '{lang}'", e)
            failed_translations.append((lang, str(e)))
            continue
            
        except Exception as e:
            # Any other translation error
            log_error(f"Error en la traducción para el idioma '{lang}'", e)
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
