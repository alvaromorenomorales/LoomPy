"""Core translation pipeline for orchestrating JSON translation."""

import copy
from typing import Any, Dict, List, Tuple

from src.json_traversal import collect_string_paths, set_by_path
from src.placeholder_protection import extract_placeholders, restore_placeholders


def translate_json_values(
    json_data: Any,
    translate_func: callable,
    progress_callback: callable = None,
    **translate_kwargs
) -> Any:
    """
    Orchestrate full translation of JSON values.
    
    This function coordinates the entire translation pipeline:
    1. Extract all string values with their paths
    2. Protect placeholders before translation
    3. Translate the protected texts
    4. Restore placeholders in translated texts
    5. Apply translations back to JSON structure
    
    Args:
        json_data: The source JSON structure (dict, list, or primitive)
        translate_func: Function to translate a list of texts
                       Should accept List[str] and return List[str]
        progress_callback: Optional callback function to report progress.
                          Called with (processed_count, total_count)
        **translate_kwargs: Additional keyword arguments to pass to translate_func
        
    Returns:
        New JSON structure with translated string values
        
    Example:
        >>> data = {"greeting": "Hola {name}", "count": 5}
        >>> def mock_translate(texts): return ["Hello {name}"]
        >>> translate_json_values(data, mock_translate)
        {'greeting': 'Hello {name}', 'count': 5}
    """
    # Step 1: Extract all string values with their paths
    string_paths = collect_string_paths(json_data)
    
    # If no strings to translate, return a deep copy of the original
    if not string_paths:
        return copy.deepcopy(json_data)
    
    # Step 2: Protect placeholders before translation
    protected_texts = []
    placeholder_mappings = []
    
    for path, original_text in string_paths:
        protected_text, mapping = extract_placeholders(original_text)
        protected_texts.append(protected_text)
        placeholder_mappings.append(mapping)
    
    # Step 3: Translate the protected texts
    translated_texts = translate_func(protected_texts, **translate_kwargs)
    
    # Report progress after translation
    if progress_callback:
        progress_callback(len(protected_texts), len(protected_texts))
    
    # Ensure we got the same number of translations back
    if len(translated_texts) != len(protected_texts):
        raise ValueError(
            f"Translation function returned {len(translated_texts)} texts "
            f"but expected {len(protected_texts)}"
        )
    
    # Step 4: Restore placeholders in translated texts
    restored_texts = []
    for translated_text, mapping in zip(translated_texts, placeholder_mappings):
        restored_text = restore_placeholders(translated_text, mapping)
        restored_texts.append(restored_text)
    
    # Step 5: Apply translations back to JSON structure
    # Create a deep copy to avoid modifying the original
    result = copy.deepcopy(json_data)
    
    for (path, _), restored_text in zip(string_paths, restored_texts):
        if path:  # Non-empty path
            set_by_path(result, path, restored_text)
        else:  # Empty path means root is a string
            # For root-level strings, we need to return the translated value directly
            result = restored_text
    
    return result


def translate_json_to_multi_languages(
    json_data: Any,
    target_langs: List[str],
    translate_func: callable,
    progress_callback: callable = None,
    **translate_kwargs
) -> Dict[str, Any]:
    """
    Orchestrate translation of JSON values to multiple languages at once.
    
    Args:
        json_data: The source JSON structure
        target_langs: List of target language codes
        translate_func: Function accepting (texts, target_langs) and 
                       returning {lang: List[str]}
        progress_callback: Optional progress reporter (processed, total)
        
    Returns:
        Dict mapping lang_code to translated JSON structure
    """
    # 1. Extract strings
    string_paths = collect_string_paths(json_data)
    if not string_paths:
        return {lang: copy.deepcopy(json_data) for lang in target_langs}
    
    # 2. Protect placeholders
    protected_texts = []
    placeholder_mappings = []
    for _, text in string_paths:
        p_text, mapping = extract_placeholders(text)
        protected_texts.append(p_text)
        placeholder_mappings.append(mapping)
    
    # 3. Translate all at once
    # translate_func is expected to return Dict[lang, List[str]]
    all_translated = translate_func(protected_texts, target_langs, **translate_kwargs)
    
    # 4. Restore and Reconstruct for each language
    results = {}
    for lang in target_langs:
        lang_translated_texts = all_translated[lang]
        
        # Restore placeholders
        restored_texts = []
        for trans, mapping in zip(lang_translated_texts, placeholder_mappings):
            restored_texts.append(restore_placeholders(trans, mapping))
            
        # Reconstruct JSON
        lang_json = copy.deepcopy(json_data)
        for (path, _), restored in zip(string_paths, restored_texts):
            if path:
                set_by_path(lang_json, path, restored)
            else:
                lang_json = restored
        
        results[lang] = lang_json
        
    if progress_callback:
        # Just mark as done here, progress is handled inside translate_func
        progress_callback(len(protected_texts) * len(target_langs), len(protected_texts) * len(target_langs))
        
    return results
