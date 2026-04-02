"""Tests for the translation engine module using NLLB-200."""

import pytest
from unittest.mock import patch, MagicMock
from src.translation_engine import NLLBTranslationProvider
from src.config import SUPPORTED_LANGUAGES, SUPPORTED_SOURCE_LANGUAGES


class TestNLLBTranslationProvider:
    """Test the NLLBTranslationProvider class."""
    
    def test_provider_initialization(self):
        """Test that provider initializes correctly."""
        provider = NLLBTranslationProvider(model_path="dummy/path")
        assert provider.model_path == "dummy/path"
        assert provider.translator is None
        assert provider.tokenizer is None
        assert provider.device is None
        assert provider.current_source_language is None
        assert provider.current_target_language is None

    @patch('torch.cuda.is_available')
    @patch('ctranslate2.Translator')
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('os.path.exists')
    def test_load_model_cpu(self, mock_exists, mock_tokenizer, mock_translator, mock_cuda):
        """Test loading model on CPU."""
        mock_exists.return_value = True
        mock_cuda.return_value = False
        
        provider = NLLBTranslationProvider(model_path="dummy/path")
        device = provider.load_model("spa_Latn", "eng_Latn", device="cpu")
        
        assert device == "cpu"
        assert provider.translator is not None
        assert provider.tokenizer is not None
        assert provider.device == "cpu"
        assert provider.current_source_language == "spa_Latn"
        assert provider.current_target_language == "eng_Latn"

    @patch('torch.cuda.is_available')
    @patch('ctranslate2.Translator')
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('os.path.exists')
    def test_load_model_cuda(self, mock_exists, mock_tokenizer, mock_translator, mock_cuda):
        """Test loading model on CUDA."""
        mock_exists.return_value = True
        mock_cuda.return_value = True
        
        provider = NLLBTranslationProvider(model_path="dummy/path")
        device = provider.load_model("spa_Latn", "eng_Latn", device="cuda")
        
        assert device == "cuda"
        assert provider.device == "cuda"

    @patch('ctranslate2.Translator')
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('os.path.exists')
    def test_translate_batch(self, mock_exists, mock_tokenizer, mock_translator):
        """Test basic translation batch."""
        mock_exists.return_value = True
        
        # Setup mocks
        mock_translator_instance = mock_translator.return_value
        mock_tokenizer_instance = mock_tokenizer.return_value
        
        # Mock tokenization
        mock_tokenizer_instance.return_value = {"input_ids": [[1, 2, 3]]}
        mock_tokenizer_instance.convert_ids_to_tokens.return_value = ["tokens"]
        
        # Mock translation result
        mock_hyp = MagicMock()
        mock_hyp.hypotheses = [["translated_tokens"]]
        mock_translator_instance.translate_batch.return_value = [mock_hyp]
        
        # Mock decoding
        mock_tokenizer_instance.convert_tokens_to_ids.return_value = [4, 5, 6]
        mock_tokenizer_instance.decode.return_value = "Hello World"
        
        provider = NLLBTranslationProvider(model_path="dummy/path")
        provider.load_model("spa_Latn", "eng_Latn", device="cpu")
        
        results = provider.translate_batch(["Hola Mundo"])
        
        assert results == ["Hello World"]
        assert "eng_Latn:Hola Mundo" in provider.cache

    @patch('ctranslate2.Translator')
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('os.path.exists')
    def test_translate_multi_target_batch(self, mock_exists, mock_tokenizer, mock_translator):
        """Test translation to multiple targets at once."""
        mock_exists.return_value = True
        
        mock_translator_instance = mock_translator.return_value
        mock_tokenizer_instance = mock_tokenizer.return_value
        
        # Setup mocks for 2 target languages
        mock_tokenizer_instance.return_value = {"input_ids": [[1, 2, 3]]}
        mock_tokenizer_instance.convert_ids_to_tokens.return_value = ["tokens"]
        
        mock_hyp = MagicMock()
        mock_hyp.hypotheses = [["res"]]
        mock_translator_instance.translate_batch.return_value = [mock_hyp]
        
        mock_tokenizer_instance.decode.side_effect = ["English", "French"]
        
        provider = NLLBTranslationProvider(model_path="dummy/path")
        provider.load_model("spa_Latn", "eng_Latn", device="cpu")
        
        targets = ["eng_Latn", "fra_Latn"]
        results = provider.translate_multi_target_batch(["Hola"], targets)
        
        assert "eng_Latn" in results
        assert "fra_Latn" in results
        assert results["eng_Latn"] == ["English"]
        assert results["fra_Latn"] == ["French"]

    @patch('ctranslate2.converters.TransformersConverter')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_ensure_local_model_downloads_if_missing(self, mock_exists, mock_makedirs, mock_converter):
        """Test that model is downloaded if it doesn't exist."""
        mock_exists.return_value = False # Model doesn't exist
        
        provider = NLLBTranslationProvider(model_path="some/new/path")
        provider._ensure_local_model()
        
        assert mock_converter.called
        assert mock_makedirs.called

    def test_translate_batch_empty_list(self):
        """Test translating empty list returns empty list."""
        provider = NLLBTranslationProvider(model_path="dummy/path")
        result = provider.translate_batch([])
        assert result == []
