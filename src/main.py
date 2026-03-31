"""Main entry point for JSON Translator."""
import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

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
# NLLBTranslationProvider is imported inside main() to improve startup time
from src.translation_pipeline import translate_json_to_multi_languages
from src.json_traversal import collect_string_paths
from src.progress_bar import ProgressBar
from src.logger import (
    log_progress,
    log_completion,
    log_error,
    log_language_start,
    log_warning
)
from src.interactive_cli import run_interactive_cli


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for JSON translation.
    """
    default_input = str(get_input_path())
    supported_source_langs_str = ", ".join(SUPPORTED_SOURCE_LANGUAGES)
    supported_langs_str = ", ".join(SUPPORTED_LANGUAGES)
    default_langs_str = " ".join(DEFAULT_TARGET_LANGUAGES)
    
    parser = argparse.ArgumentParser(
        description="Translate JSON files between multiple languages while preserving structure and placeholders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s --interactive                      # Run interactive CLI mode
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
        help=f"Path to source JSON file (default: {default_input})"
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

    args = parser.parse_args()
    args.interactive = len(sys.argv) == 1
    return args


def main():
    """Main function to orchestrate JSON translation."""
    log_progress(">>> LoomPy: Bootstrapping application...")
    
    args = parse_arguments()
    
    if args.interactive:
        input_file, source_lang, target_langs, output_dir, update_source, output_source, device = run_interactive_cli()
        args.input = input_file
        args.source_lang = source_lang
        args.langs = target_langs
        args.out_dir = output_dir
        args.update_source = update_source
        args.output_source = output_source
        args.device = None if device == "auto" else device
    
    # Validation
    if not validate_source_language(args.source_lang):
        log_error(f"Unsupported source language: {args.source_lang}", ValueError(f"Supported lists: {SUPPORTED_SOURCE_LANGUAGES}"))
        sys.exit(1)
    
    invalid_targets = [lang for lang in args.langs if not validate_language_pair(args.source_lang, lang)]
    if invalid_targets:
        log_error(f"Unsupported target language(s): {', '.join(invalid_targets)}", ValueError("Invalid language pair"))
        sys.exit(1)
    
    log_progress(f"Starting JSON translation from {args.input}")
    log_progress(f"Source language: {args.source_lang}")
    log_progress(f"Target languages: {', '.join(args.langs)}")
    log_progress(f"Device: {args.device if args.device else 'auto-detect'}")
    
    # Load source file
    try:
        source_data = load_json_file(args.input)
        log_progress(f"V Loaded source file: {args.input}")
    except Exception as e:
        log_error(f"Failed to load source file: {args.input}", e)
        sys.exit(1)
    
    # Ensure output directory exists
    try:
        ensure_output_directory(args.out_dir)
        log_progress(f"V Output directory ready: {args.out_dir}")
    except Exception as e:
        log_error(f"Failed to create output directory: {args.out_dir}", e)
        sys.exit(1)

    # Handle source file options
    if args.update_source:
        serialize_json(source_data, args.input)
        log_progress(f"V Source file updated")

    if args.output_source:
        source_filename = Path(args.input).name
        output_source_path = str(Path(args.out_dir) / source_filename)
        serialize_json(source_data, output_source_path)
        log_progress(f"V Source copy saved to output")
    
    if not args.langs:
        sys.exit(0)
    
    # --- MULTI-LANGUAGE TRANSLATION PROCESS ---
    
    from src.translation_engine import NLLBTranslationProvider
    provider = NLLBTranslationProvider()
    
    # Load model once using first target language as reference (NLLB is multilingual)
    provider.load_model(args.source_lang, args.langs[0], args.device)
    
    progress_bar = ProgressBar(bar_width=40, enable_colors=True)
    
    # Count unique string values to translate
    total_strings = len(collect_string_paths(source_data))
    total_work = total_strings * len(args.langs)
    
    task_name = f"Translating to {len(args.langs)} languages"
    print() # Add newline to separate from previous logs/download bars
    progress_bar.start_task(task_name, total_work)
    
    log_progress(f"  Starting massive multi-language translation...")
    
    def multi_translate_func(texts, target_langs):
        return provider.translate_multi_target_batch(
            texts, 
            target_langs,
            progress_callback=lambda current, total: progress_bar.update(current)
        )
    
    try:
        # One call to rule them all
        results_dict = translate_json_to_multi_languages(
            source_data,
            args.langs,
            multi_translate_func
        )
        
        progress_bar.complete()
        
        # Save results
        for lang, translated_json in results_dict.items():
            output_filename = f"{lang}.json"
            output_path = str(Path(args.out_dir) / output_filename)
            serialize_json(translated_json, output_path)
            log_completion(lang, output_path)
            
        print("\n" + "="*60)
        log_progress(f"Translation complete! Successfully processed {len(args.langs)} languages.")
        
    except Exception as e:
        log_error("Massive translation failed", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
