"""Interactive CLI for JSON Translator."""
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from src.config import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_LANGUAGE,
    DEFAULT_TARGET_LANGUAGES,
    SUPPORTED_LANGUAGES,
    SUPPORTED_SOURCE_LANGUAGES,
    get_input_path,
    get_output_path,
    validate_language_pair,
    validate_source_language,
    get_supported_target_languages,
    MODEL_TEMPLATES
)
from src.logger import log_progress, log_warning, log_error
from src.locale import t, set_locale, get_locale, get_supported_locales


class Colors:
    """ANSI color codes for terminal output."""
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# Display names for supported CLI locale codes
LANG_DISPLAY = {
    "es": "Español",
    "en": "English",
}


def print_header(text: str) -> None:
    """Print a colored header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def print_section(text: str) -> None:
    """Print a section title."""
    print(f"{Colors.BOLD}{Colors.BLUE}▶ {text}{Colors.RESET}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_choice(number: int, text: str, description: str = "") -> None:
    """Print a choice option."""
    desc_str = f" - {Colors.WHITE}{description}{Colors.RESET}" if description else ""
    print(f"  {Colors.YELLOW}{number}{Colors.RESET}. {text}{desc_str}")


def get_file_input(prompt: str, default: Optional[str] = None) -> str:
    """Get a file path from user with validation."""
    while True:
        if default:
            user_input = input(f"{Colors.BOLD}{prompt} [{default}]{Colors.RESET}: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{Colors.BOLD}{prompt}{Colors.RESET}: ").strip()
        
        file_path = Path(user_input)
        
        # If it's a relative path in default dir
        if not file_path.is_absolute() and DEFAULT_INPUT_DIR not in user_input:
            file_path = Path(DEFAULT_INPUT_DIR) / user_input
        
        if file_path.exists():
            print_info(f"{t('file_found')}: {file_path}")
            return str(file_path)
        else:
            print(f"{Colors.RED}✗ {t('file_not_found')}: {file_path}{Colors.RESET}")
            print(f"{Colors.YELLOW}{t('available_files')} {DEFAULT_INPUT_DIR}:{Colors.RESET}")
            try:
                input_dir = Path(DEFAULT_INPUT_DIR)
                json_files = list(input_dir.glob("*.json"))
                if json_files:
                    for json_file in json_files:
                        print(f"  - {json_file.name}")
                else:
                    print(f"  ({t('no_files')})")
            except Exception:
                pass


def choose_language(prompt: str, available_langs: List[str], default: Optional[str] = None) -> str:
    """Let user choose a language from available options."""
    print_section(prompt)
    
    for i, lang in enumerate(available_langs, 1):
        display = f"{lang} - {LANG_DISPLAY.get(lang, lang)}"
        print_choice(i, display)
    
    while True:
        choice = input(f"{Colors.BOLD}{t('select_option')} (1-{len(available_langs)}){Colors.RESET}: ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(available_langs):
                selected = available_langs[idx]
                print_info(f"{t('lang_selected')}: {selected}")
                return selected
            else:
                print(f"{Colors.RED}✗ {t('invalid_device')}{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}✗ {t('enter_number')}{Colors.RESET}")


def choose_multiple_languages(prompt: str, available_langs: List[str], defaults: Optional[List[str]] = None) -> List[str]:
    """Let user choose multiple languages."""
    print_section(prompt)
    
    for i, lang in enumerate(available_langs, 1):
        print_choice(i, lang)
    
    default_str = ""
    if defaults:
        default_indices = [str(available_langs.index(lang) + 1) for lang in defaults if lang in available_langs]
        default_str = f" [{','.join(default_indices)}]"
    
    print(f"{Colors.YELLOW}{t('target_langs_instruction')}{default_str}{Colors.RESET}")
    
    while True:
        choice = input(f"{Colors.BOLD}{t('select_languages')}{Colors.RESET}: ").strip()
        
        if not choice and defaults:
            print_info(f"{t('langs_selected')}: {', '.join(defaults)}")
            return defaults
        
        if not choice:
            print(f"{Colors.RED}✗ {t('langs_required')}{Colors.RESET}")
            continue
        
        # Parse input: handle both spaces and commas
        choice = choice.replace(",", " ")
        selections = choice.split()
        
        try:
            indices = [int(s) - 1 for s in selections]
            
            # Validate all indices
            if not all(0 <= idx < len(available_langs) for idx in indices):
                print(f"{Colors.RED}✗ {t('invalid_numbers')}{Colors.RESET}")
                continue
            
            # Remove duplicates and maintain order
            selected = []
            for idx in indices:
                if available_langs[idx] not in selected:
                    selected.append(available_langs[idx])
            
            if selected:
                print_info(f"{t('langs_selected')}: {', '.join(selected)}")
                return selected
            else:
                print(f"{Colors.RED}✗ {t('langs_required')}{Colors.RESET}")
                
        except ValueError:
            print(f"{Colors.RED}✗ {t('invalid_input')}{Colors.RESET}")


def confirm(prompt: str, default: bool = True) -> bool:
    """Ask user for yes/no confirmation."""
    default_text = "S/n" if default else "s/N"
    response = input(f"{Colors.BOLD}{prompt} [{default_text}]{Colors.RESET}: ").strip().lower()
    
    if not response:
        return default
    
    return response in ("s", "si", "sí", "y", "yes", "ya")


def get_output_directory(default: str = DEFAULT_OUTPUT_DIR) -> str:
    """Get output directory from user."""
    print_section(t('section_output_dir'))
    print(f"{t('output_dir_label')}: {Colors.CYAN}{default}{Colors.RESET}")
    
    custom = confirm(t('custom_output_dir'), default=False)
    
    if custom:
        while True:
            out_dir = input(f"{Colors.BOLD}{t('output_dir_prompt')}{Colors.RESET}: ").strip()
            if not out_dir:
                print(f"{Colors.RED}✗ {t('empty_path')}{Colors.RESET}")
                continue

            # Resolve the path to an absolute path, showing the user where it will be written.
            try:
                candidate = Path(out_dir).expanduser()
                if not candidate.is_absolute():
                    candidate = (Path.cwd() / candidate).resolve()

                print_info(f"{t('using_directory')}: {candidate}")
                # Confirm that the resolved path is desired
                keep = confirm(f"{t('confirm_proceed')} ({candidate})", default=True)
                if keep:
                    return str(candidate)
                else:
                    print(f"{Colors.YELLOW}Reintroduce la ruta de salida{Colors.RESET}")
                    continue
            except Exception:
                print(f"{Colors.RED}✗ {t('invalid_input')}{Colors.RESET}")
                continue
    else:
        print_info(f"{t('using_directory')}: {default}")
        return default


def run_interactive_cli() -> Tuple[str, str, List[str], str, bool, bool, str]:
    """
    Run interactive CLI to gather translation parameters.
    
    Returns:
        Tuple containing:
        - input_file: Path to source JSON file
        - source_lang: Source language code
        - target_langs: List of target language codes
        - output_dir: Output directory path
        - update_source: Whether to update source file
        - output_source: Whether to output cleaned source file
        - device: Device for translation ("cpu", "cuda", or "auto")
    """
    # First, ask which language to use for the CLI itself
    supported_locales = get_supported_locales()
    # Ask user to select the CLI language; default is current locale
    cli_locale = choose_language(t('choose_cli_language'), supported_locales, default=get_locale())
    set_locale(cli_locale)

    # Now print localized header
    print_header(t('header'))
    
    # Step 1: Get input file
    print_section(t('section_input_file'))
    print(f"{t('input_dir_label')}: {Colors.CYAN}{DEFAULT_INPUT_DIR}{Colors.RESET}")
    
    default_input = str(get_input_path())
    input_file = get_file_input(t('input_file_prompt'), default=Path(default_input).name)
    
    # Step 2: Get source language
    print_section(t('section_source_lang'))
    source_lang = choose_language(
        t('choose_source_lang'),
        SUPPORTED_SOURCE_LANGUAGES,
        DEFAULT_SOURCE_LANGUAGE
    )
    
    # Step 3: Get target languages
    supported_targets = get_supported_target_languages(source_lang)
    target_langs = choose_multiple_languages(
        t('section_target_langs'),
        supported_targets,
        defaults=[lang for lang in DEFAULT_TARGET_LANGUAGES if lang in supported_targets]
    )
    
    # Step 4: Get output directory
    output_dir = get_output_directory()
    
    # Step 5: Ask about source file options
    print_section(t('section_source_options'))
    
    update_source = confirm(
        t('update_source_prompt'),
        default=False
    )
    
    output_source = False
    if not update_source:
        output_source = confirm(
            t('save_clean_copy'),
            default=False
        )
    elif update_source:
        print_info(t('saving_to_original'))
    
    # Step 6: Device selection
    print_section(t('section_device'))
    print_choice(1, t('device_auto'), t('device_auto_desc'))
    print_choice(2, t('device_cpu'))
    print_choice(3, t('device_cuda'))
    
    while True:
        device_choice = input(f"{Colors.BOLD}{t('device_prompt')} (1-3){Colors.RESET}: ").strip()
        
        if device_choice == "1":
            device = "auto"
            print_info(t('device_selected_auto'))
            break
        elif device_choice == "2":
            device = "cpu"
            print_info(t('device_selected_cpu'))
            break
        elif device_choice == "3":
            device = "cuda"
            print_info(t('device_selected_cuda'))
            break
        else:
            print(f"{Colors.RED}✗ {t('invalid_device')}{Colors.RESET}")
    
    # Summary
    print_header(t('header_summary'))
    print(f"{t('summary_file')}:            {Colors.CYAN}{input_file}{Colors.RESET}")
    print(f"{t('summary_source_lang')}:      {Colors.CYAN}{source_lang.upper()}{Colors.RESET}")
    print(f"{t('summary_target_langs')}:    {Colors.CYAN}{', '.join([l.upper() for l in target_langs])}{Colors.RESET}")
    print(f"{t('summary_output_dir')}:  {Colors.CYAN}{output_dir}{Colors.RESET}")
    print(f"{t('summary_update_source')}:  {Colors.CYAN}{t('summary_yes') if update_source else t('summary_no')}{Colors.RESET}")
    print(f"{t('summary_save_copy')}:      {Colors.CYAN}{t('summary_yes') if output_source else t('summary_no')}{Colors.RESET}")
    print(f"{t('summary_device')}:        {Colors.CYAN}{device.upper()}{Colors.RESET}")
    
    proceed = confirm(f"\n{t('confirm_proceed')}", default=True)
    
    if not proceed:
        print(f"{Colors.YELLOW}{t('operation_cancelled')}{Colors.RESET}")
        sys.exit(0)
    
    return input_file, source_lang, target_langs, output_dir, update_source, output_source, device
