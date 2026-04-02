"""
Translation engine interfaces and implementations.
Adheres to the Open-Closed Principle (SOLID) by defining an abstract base class.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
import torch
from src.config import (
    MAX_SEQUENCE_LENGTH,
    TRANSLATION_BATCH_SIZE,
    validate_language_pair,
    SUPPORTED_LANGUAGES,
    SUPPORTED_SOURCE_LANGUAGES,
    get_model_path,
    NLLB_MODEL_NAME
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


class NLLBTranslationProvider(TranslationProvider):
    """
    Multilingual high-performance provider using NLLB-200 + CTranslate2.
    """
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = str(get_model_path())
        self.model_path = model_path
        self.translator = None
        self.tokenizer = None
        self.device = None
        self.cache = {}
        # Mapping ISO 639-1 to NLLB codes
        self.lang_map = {
            "en": "eng_Latn",
            "es": "spa_Latn",
            "fr": "fra_Latn",
            "de": "deu_Latn",
            "ca": "cat_Latn"
        }
        self.current_source_language = None
        self.current_target_language = None

    def load_model(self, source_language: str, target_language: str, device: Optional[str] = None) -> str:
        """
        Loads the model only once. Language changes don't require reloading.
        """
        self.current_source_language = source_language
        self.current_target_language = target_language

        if self.translator is not None:
            return self.device

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        elif device not in ["cpu", "cuda"]:
            raise ValueError(f"Invalid device: {device}. Must be 'cpu' or 'cuda'")
        
        if device == "cuda" and not torch.cuda.is_available():
            print("Warning: CUDA requested but not available. Falling back to CPU.")
            device = "cpu"

        import ctranslate2
        import transformers
        from src.logger import log_progress, log_warning

        # Step 0: Ensure local model exists
        self._ensure_local_model()

        log_progress(f"Initializing NLLB-200 with CTranslate2 on {device}...")
        
        # Optimize inference
        self.translator = ctranslate2.Translator(
            self.model_path,
            device=device,
            compute_type="int8", 
            intra_threads=0      # Auto-detect cores
        )
        
        self.tokenizer = transformers.AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
        print() # Ensure the last download bar (e.g. tokenizer/config) ends with a newline
        self.device = device
        return device

    def translate_batch(
        self, 
        texts: List[str], 
        max_length: int = MAX_SEQUENCE_LENGTH,
        batch_size: int = 96, # Optimized batch size
        progress_callback: callable = None
    ) -> List[str]:
        if not texts: 
            return []

        source_lang = self.current_source_language
        target_lang = self.current_target_language
        
        src_prefix = self.lang_map.get(source_lang, source_lang)
        tgt_prefix = self.lang_map.get(target_lang, target_lang)

        results_map = {}
        to_translate = []
        
        for t in texts:
            cache_key = f"{target_lang}:{t}"
            if cache_key in self.cache:
                results_map[t] = self.cache[cache_key]
            else:
                to_translate.append(t)

        unique_to_translate = list(set(to_translate))
        
        # Calculate how many texts we already resolved from cache
        initial_resolved = len(texts) - len(to_translate)
        
        # To report progress relative to the original `texts` list length
        resolved_count = initial_resolved
        
        if unique_to_translate:
            for i in range(0, len(unique_to_translate), batch_size):
                batch = unique_to_translate[i : i + batch_size]
                
                self.tokenizer.src_lang = src_prefix
                # Batch tokenization
                encoded = self.tokenizer(batch, truncation=True, max_length=max_length)
                source_tokens = [self.tokenizer.convert_ids_to_tokens(ids) for ids in encoded["input_ids"]]
                
                step_results = self.translator.translate_batch(
                    source_tokens,
                    target_prefix=[[tgt_prefix]] * len(batch),
                    beam_size=1 # Greedy search for maximum speed
                )
                
                for original, res in zip(batch, step_results):
                    trans_text = self.tokenizer.decode(
                        self.tokenizer.convert_tokens_to_ids(res.hypotheses[0]),
                        skip_special_tokens=True
                    )
                    self.cache[f"{target_lang}:{original}"] = trans_text
                    results_map[original] = trans_text
                
                # Approximate progress for the original `texts` list
                resolved_count += len([t for t in to_translate if t in batch])
                if progress_callback:
                    # Provide an estimated progress based on the ratio of unique requested
                    progress_callback(min(len(texts), resolved_count))

        # Ensure final callback is called with total items
        if progress_callback:
            progress_callback(len(texts))

        return [results_map[t] for t in texts]

    def translate_multi_target_batch(
        self, 
        texts: List[str], 
        target_langs: List[str],
        max_length: int = MAX_SEQUENCE_LENGTH,
        batch_size: int = 96,
        progress_callback: callable = None
    ) -> Dict[str, List[str]]:
        """
        Translate a batch of texts to multiple target languages in one pass.
        Returns a dictionary mapping language code to list of translated strings.
        """
        if not texts: 
            return {lang: [] for lang in target_langs}

        source_lang = self.current_source_language
        src_prefix = self.lang_map.get(source_lang, source_lang)

        # Initialize results structure
        results_map = {lang: {} for lang in target_langs}
        unique_to_translate = list(set(texts))
        
        total_unique = len(unique_to_translate)
        total_work = total_unique * len(target_langs)
        work_done = 0

        # We can optimize by tokenizing once per batch
        for i in range(0, total_unique, batch_size):
            batch = unique_to_translate[i : i + batch_size]
            
            # Tokenize source once
            self.tokenizer.src_lang = src_prefix
            encoded = self.tokenizer(batch, truncation=True, max_length=max_length)
            source_tokens = [self.tokenizer.convert_ids_to_tokens(ids) for ids in encoded["input_ids"]]
            
            for lang in target_langs:
                tgt_prefix = self.lang_map.get(lang, lang)
                
                # Perform translation for this language
                step_results = self.translator.translate_batch(
                    source_tokens,
                    target_prefix=[[tgt_prefix]] * len(batch),
                    beam_size=1
                )
                
                for original, res in zip(batch, step_results):
                    trans_text = self.tokenizer.decode(
                        self.tokenizer.convert_tokens_to_ids(res.hypotheses[0]),
                        skip_special_tokens=True
                    )
                    results_map[lang][original] = trans_text
                
                work_done += len(batch)
                if progress_callback:
                    # Update progress proportionally
                    progress_callback(work_done, total_work)

        # Final response formatted as lists matching input order
        final_results = {}
        for lang in target_langs:
            final_results[lang] = [results_map[lang][t] for t in texts]
            
        return final_results

    def _ensure_local_model(self):
        """
        Verify if the optimized model exists. If not, download and convert it.
        """
        import os
        from src.logger import log_progress
        
        if os.path.exists(self.model_path):
            return

        log_progress(f"Optimization model not found at {self.model_path}")
        log_progress(">>> LoomPy: Initializing first-time setup (downloading and optimizing NLLB-200)...")
        log_progress("This may take several minutes depending on your internet speed.")
        
        import ctranslate2
        from pathlib import Path
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # We use the Distilled 600M version for best balance of speed/quality
        source_model = "facebook/nllb-200-distilled-600M"
        
        converter = ctranslate2.converters.TransformersConverter(source_model)
        converter.convert(
            self.model_path,
            quantization="int8", # Force int8 for CPU efficiency
            force=True
        )
        
        log_progress(f"V Model optimized and saved to {self.model_path}")
