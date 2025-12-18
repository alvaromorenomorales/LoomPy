"""
Translation engine interfaces and implementations.
Adheres to the Open-Closed Principle (SOLID) by defining an abstract base class.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import torch
from transformers import MarianMTModel, MarianTokenizer

from src.config import (
    MODEL_TEMPLATES,
    MAX_SEQUENCE_LENGTH,
    TRANSLATION_BATCH_SIZE,
    get_model_name,
    get_model_name_for_pair,
    validate_language,
    validate_language_pair,
    SUPPORTED_LANGUAGES,
    SUPPORTED_SOURCE_LANGUAGES
)
from src.logger import log_warning, log_progress

class TranslationProvider(ABC):
    """Abstract base class for translation providers."""
    
    @abstractmethod
    def load_model(self, source_language: str, target_language: str, device: Optional[str] = None):
        """Load the model for a specific language pair."""
        pass
    
    @abstractmethod
    def translate_batch(self, texts: List[str]) -> List[str]:
        """Translate a batch of texts."""
        pass

class OpusMTProvider(TranslationProvider):
    """
    Concrete implementation of TranslationProvider using HuggingFace Opus-MT models.
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = None
        self.current_source_language = None
        self.current_target_language = None

    def load_model(self, source_language: str, target_language: str, device: Optional[str] = None) -> str:
        """
        Load Opus-MT model and tokenizer for a language pair.
        
        Args:
            source_language: ISO 639-1 source language code (e.g., "es", "en", "fr")
            target_language: ISO 639-1 target language code (e.g., "en", "fr", "ca")
            device: Device to use ('cpu', 'cuda', or None for auto-detect)
        
        Returns:
            str: The device used ('cpu' or 'cuda')
        """
        if not validate_language_pair(source_language, target_language):
            from src.config import get_supported_target_languages
            supported_targets = get_supported_target_languages(source_language)
            raise ValueError(
                f"Unsupported language pair: {source_language} -> {target_language}. "
                f"Available target languages for {source_language}: {', '.join(supported_targets) if supported_targets else 'none'}"
            )
            
        # Optimize: Don't reload if it's the same language pair and device
        if (self.current_source_language == source_language and 
            self.current_target_language == target_language and 
            self.model is not None):
             return self.device

        model_name = get_model_name_for_pair(source_language, target_language)
        
        # Determine device
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        elif device not in ["cpu", "cuda"]:
            raise ValueError(f"Invalid device: {device}. Must be 'cpu' or 'cuda'")
        
        if device == "cuda" and not torch.cuda.is_available():
            print(f"Warning: CUDA requested but not available. Falling back to CPU.")
            device = "cpu"
        
        try:
            self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            self.model = MarianMTModel.from_pretrained(model_name)
            self.model = self.model.to(device)
            self.model.eval()
            
            self.device = device
            self.current_source_language = source_language
            self.current_target_language = target_language
            return device
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model {model_name}: {str(e)}") from e

    def translate_batch(
        self, 
        texts: List[str], 
        max_length: int = MAX_SEQUENCE_LENGTH,
        batch_size: int = TRANSLATION_BATCH_SIZE,
        progress_callback: callable = None
    ) -> List[str]:
        """
        Translate a batch of texts using the loaded model.
        
        Args:
            texts: List of texts to translate
            max_length: Maximum sequence length
            batch_size: Number of texts to process at once
            progress_callback: Optional callback to report progress (processed_count)
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model and tokenizer must be loaded before translation.")

        if not texts:
            return []
        
        all_translations = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Check for lengths
            for idx, text in enumerate(batch):
                test_encoded = self.tokenizer(
                    text, return_tensors="pt", truncation=False, add_special_tokens=True
                )
                actual_length = len(test_encoded["input_ids"][0])
                if actual_length > max_length:
                    text_preview = text[:50] + "..." if len(text) > 50 else text
                    log_warning(
                        f"Text at index {i + idx} exceeds max_length "
                        f"({actual_length} > {max_length}). Preview: '{text_preview}'"
                    )
            
            encoded = self.tokenizer(
                batch, return_tensors="pt", padding=True, truncation=True, max_length=max_length
            )
            encoded = {k: v.to(self.device) for k, v in encoded.items()}
            
            with torch.no_grad():
                generated_tokens = self.model.generate(**encoded)
            
            batch_translations = self.tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )
            all_translations.extend(batch_translations)
            
            # Report progress after each batch
            if progress_callback:
                progress_callback(len(all_translations))
            
        return all_translations
