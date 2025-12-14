"""Translation engine for loading and using Opus-MT models."""

import torch
from typing import List, Tuple, Optional
from transformers import MarianMTModel, MarianTokenizer

from src.config import (
    MODEL_TEMPLATES,
    MAX_SEQUENCE_LENGTH,
    TRANSLATION_BATCH_SIZE,
    get_model_name,
    validate_language
)
from .logger import log_warning


def load_opus_mt(
    target_language: str,
    device: Optional[str] = None
) -> Tuple[MarianMTModel, MarianTokenizer, str]:
    """
    Load Opus-MT model and tokenizer for Spanish to target language translation.
    
    Args:
        target_language: Target language code (en, fr, ca)
        device: Device to use ('cpu', 'cuda', or None for auto-detect)
        
    Returns:
        Tuple of (model, tokenizer, device_used)
        
    Raises:
        ValueError: If target language is not supported
        RuntimeError: If model cannot be loaded
        
    Example:
        >>> model, tokenizer, device = load_opus_mt("en")
        >>> device in ["cpu", "cuda"]
        True
    """
    # Validate target language using config
    if not validate_language(target_language):
        from src.config import SUPPORTED_LANGUAGES
        supported = ", ".join(SUPPORTED_LANGUAGES)
        raise ValueError(
            f"Unsupported target language: {target_language}. "
            f"Supported languages: {supported}"
        )
    
    # Get model name from config
    model_name = get_model_name(target_language)
    
    # Determine device
    if device is None:
        # Auto-detect: use CUDA if available, otherwise CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
    elif device not in ["cpu", "cuda"]:
        raise ValueError(f"Invalid device: {device}. Must be 'cpu' or 'cuda'")
    
    # Check if CUDA is requested but not available
    if device == "cuda" and not torch.cuda.is_available():
        print(f"Warning: CUDA requested but not available. Falling back to CPU.")
        device = "cpu"
    
    try:
        # Load tokenizer and model
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        
        # Move model to device
        model = model.to(device)
        model.eval()  # Set to evaluation mode
        
        return model, tokenizer, device
        
    except Exception as e:
        raise RuntimeError(
            f"Failed to load model {model_name}: {str(e)}"
        ) from e


def translate_batch(
    texts: List[str],
    model: MarianMTModel,
    tokenizer: MarianTokenizer,
    device: str,
    max_length: int = MAX_SEQUENCE_LENGTH,
    batch_size: int = TRANSLATION_BATCH_SIZE
) -> List[str]:
    """
    Translate a batch of texts using the provided model.
    
    Args:
        texts: List of texts to translate
        model: Loaded MarianMT model
        tokenizer: Loaded MarianTokenizer
        device: Device the model is on ('cpu' or 'cuda')
        max_length: Maximum token length (texts exceeding this will be truncated)
        batch_size: Number of texts to process in each batch
        
    Returns:
        List of translated texts in the same order as input
        
    Example:
        >>> model, tokenizer, device = load_opus_mt("en")
        >>> texts = ["Hola mundo", "Buenos días"]
        >>> translations = translate_batch(texts, model, tokenizer, device)
        >>> len(translations) == len(texts)
        True
    """
    if not texts:
        return []
    
    all_translations = []
    
    # Process in batches
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Check for texts that will exceed max_length before tokenization
        for idx, text in enumerate(batch):
            # Tokenize individual text to check actual length
            test_encoded = tokenizer(
                text,
                return_tensors="pt",
                truncation=False,
                add_special_tokens=True
            )
            actual_length = len(test_encoded["input_ids"][0])
            
            if actual_length > max_length:
                # Create a preview of the text (first 50 chars)
                text_preview = text[:50] + "..." if len(text) > 50 else text
                log_warning(
                    f"Text at index {i + idx} exceeds max_length "
                    f"({actual_length} > {max_length} tokens) and will be truncated. "
                    f"Preview: '{text_preview}'"
                )
        
        # Tokenize batch with truncation
        encoded = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length
        )
        
        # Move to device
        encoded = {k: v.to(device) for k, v in encoded.items()}
        
        # Generate translations
        with torch.no_grad():
            generated_tokens = model.generate(**encoded)
        
        # Decode translations
        batch_translations = tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )
        
        all_translations.extend(batch_translations)
    
    return all_translations
