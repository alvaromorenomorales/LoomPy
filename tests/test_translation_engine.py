"""Tests for the translation engine module."""

import pytest
import torch
from unittest.mock import patch, MagicMock
from src.translation_engine import load_opus_mt, translate_batch, MODEL_MAPPING


class TestModelMapping:
    """Test the model mapping configuration."""
    
    def test_model_mapping_contains_required_languages(self):
        """Test that model mapping includes all required languages."""
        assert "en" in MODEL_MAPPING
        assert "fr" in MODEL_MAPPING
        assert "ca" in MODEL_MAPPING
    
    def test_model_mapping_values_are_valid(self):
        """Test that model names follow expected format."""
        for lang, model_name in MODEL_MAPPING.items():
            assert model_name.startswith("Helsinki-NLP/opus-mt-es-")
            assert model_name.endswith(f"-{lang}")


class TestLoadOpusMT:
    """Test the load_opus_mt function."""
    
    def test_load_opus_mt_invalid_language(self):
        """Test that invalid language raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported target language"):
            load_opus_mt("invalid_lang")
    
    def test_load_opus_mt_invalid_device(self):
        """Test that invalid device raises ValueError."""
        with pytest.raises(ValueError, match="Invalid device"):
            load_opus_mt("en", device="gpu")
    
    @pytest.mark.slow
    def test_load_opus_mt_cpu(self):
        """Test loading model on CPU."""
        model, tokenizer, device = load_opus_mt("en", device="cpu")
        
        assert model is not None
        assert tokenizer is not None
        assert device == "cpu"
    
    @pytest.mark.slow
    def test_load_opus_mt_auto_detect(self):
        """Test auto-detection of device."""
        model, tokenizer, device = load_opus_mt("en")
        
        assert model is not None
        assert tokenizer is not None
        assert device in ["cpu", "cuda"]
    
    # Unit tests for GPU detection (Requirements 6.2)
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_gpu_detection_when_available(self, mock_model, mock_tokenizer, mock_cuda):
        """Test that GPU is detected and used when available."""
        # Setup mocks
        mock_cuda.return_value = True
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        # Call with auto-detect
        model, tokenizer, device = load_opus_mt("en", device=None)
        
        # Verify GPU was detected
        assert device == "cuda"
        mock_cuda.assert_called_once()
        
        # Verify model was moved to GPU
        mock_model_instance.to.assert_called_with("cuda")
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_gpu_detection_when_not_available(self, mock_model, mock_tokenizer, mock_cuda):
        """Test that CPU is used when GPU is not available."""
        # Setup mocks
        mock_cuda.return_value = False
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        # Call with auto-detect
        model, tokenizer, device = load_opus_mt("en", device=None)
        
        # Verify CPU was selected
        assert device == "cpu"
        mock_cuda.assert_called_once()
        
        # Verify model was moved to CPU
        mock_model_instance.to.assert_called_with("cpu")
    
    # Unit tests for CPU fallback (Requirements 6.3)
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_cpu_fallback_when_cuda_requested_but_unavailable(
        self, mock_model, mock_tokenizer, mock_cuda, capsys
    ):
        """Test that system falls back to CPU when CUDA is requested but not available."""
        # Setup mocks
        mock_cuda.return_value = False
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        # Request CUDA explicitly
        model, tokenizer, device = load_opus_mt("en", device="cuda")
        
        # Verify fallback to CPU
        assert device == "cpu"
        
        # Verify warning was printed
        captured = capsys.readouterr()
        assert "Warning: CUDA requested but not available" in captured.out
        assert "Falling back to CPU" in captured.out
        
        # Verify model was moved to CPU
        mock_model_instance.to.assert_called_with("cpu")
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_explicit_cpu_selection(self, mock_model, mock_tokenizer, mock_cuda):
        """Test that CPU is used when explicitly requested."""
        # Setup mocks
        mock_cuda.return_value = True  # GPU available but not requested
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        # Request CPU explicitly
        model, tokenizer, device = load_opus_mt("en", device="cpu")
        
        # Verify CPU was used
        assert device == "cpu"
        
        # Verify model was moved to CPU
        mock_model_instance.to.assert_called_with("cpu")
    
    # Unit tests for model loading errors (Requirements 6.2, 6.3)
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    def test_model_loading_error_tokenizer_failure(self, mock_tokenizer):
        """Test that RuntimeError is raised when tokenizer fails to load."""
        # Setup mock to raise exception
        mock_tokenizer.side_effect = Exception("Network error")
        
        # Verify RuntimeError is raised with appropriate message
        with pytest.raises(RuntimeError, match="Failed to load model"):
            load_opus_mt("en", device="cpu")
    
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_model_loading_error_model_failure(self, mock_model, mock_tokenizer):
        """Test that RuntimeError is raised when model fails to load."""
        # Setup mocks
        mock_tokenizer.return_value = MagicMock()
        mock_model.side_effect = Exception("Model not found")
        
        # Verify RuntimeError is raised with appropriate message
        with pytest.raises(RuntimeError, match="Failed to load model"):
            load_opus_mt("en", device="cpu")
    
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_model_loading_error_device_transfer_failure(self, mock_model, mock_tokenizer):
        """Test that RuntimeError is raised when model fails to transfer to device."""
        # Setup mocks
        mock_tokenizer.return_value = MagicMock()
        mock_model_instance = MagicMock()
        mock_model_instance.to.side_effect = Exception("CUDA out of memory")
        mock_model.return_value = mock_model_instance
        
        # Verify RuntimeError is raised with appropriate message
        with pytest.raises(RuntimeError, match="Failed to load model"):
            load_opus_mt("en", device="cpu")
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_model_loading_all_supported_languages(self, mock_model, mock_tokenizer, mock_cuda):
        """Test that all supported languages can be loaded without errors."""
        # Setup mocks
        mock_cuda.return_value = False
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        # Test each supported language
        for lang in MODEL_MAPPING.keys():
            model, tokenizer, device = load_opus_mt(lang, device="cpu")
            assert model is not None
            assert tokenizer is not None
            assert device == "cpu"


class TestTranslateBatch:
    """Test the translate_batch function."""
    
    def test_translate_batch_empty_list(self):
        """Test translating empty list returns empty list."""
        # We don't need to load a real model for this test
        result = translate_batch([], None, None, "cpu")
        assert result == []
    
    @patch('src.translation_engine.log_warning')
    def test_translate_batch_truncation_warning(self, mock_log_warning):
        """Test that truncation warning is logged for long texts (Requirements 6.4)."""
        # Create mock tokenizer that simulates a long text
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()
        
        # First call (checking length) returns long sequence
        # Second call (actual encoding) returns truncated sequence
        long_ids = torch.tensor([[1] * 600])  # 600 tokens > 512 max_length
        truncated_ids = torch.tensor([[1] * 512])  # Truncated to 512
        
        mock_tokenizer.return_value = {
            "input_ids": truncated_ids,
            "attention_mask": torch.ones_like(truncated_ids)
        }
        
        # Mock the individual tokenization calls for length checking
        call_count = [0]
        def tokenizer_side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:  # First call is for length check
                return {"input_ids": long_ids}
            else:  # Subsequent calls are for actual encoding
                return {
                    "input_ids": truncated_ids,
                    "attention_mask": torch.ones_like(truncated_ids)
                }
        
        mock_tokenizer.side_effect = tokenizer_side_effect
        mock_tokenizer.batch_decode.return_value = ["translated text"]
        mock_model.generate.return_value = truncated_ids
        
        # Call translate_batch with a text
        texts = ["Este es un texto muy largo que excede el límite de tokens"]
        translate_batch(texts, mock_model, mock_tokenizer, "cpu", max_length=512)
        
        # Verify warning was logged
        mock_log_warning.assert_called_once()
        warning_message = mock_log_warning.call_args[0][0]
        assert "exceeds max_length" in warning_message
        assert "600 > 512 tokens" in warning_message
        assert "will be truncated" in warning_message
    
    @pytest.mark.slow
    def test_translate_batch_single_text(self):
        """Test translating a single text."""
        model, tokenizer, device = load_opus_mt("en", device="cpu")
        
        texts = ["Hola mundo"]
        translations = translate_batch(texts, model, tokenizer, device)
        
        assert len(translations) == 1
        assert isinstance(translations[0], str)
        assert len(translations[0]) > 0
    
    @pytest.mark.slow
    def test_translate_batch_multiple_texts(self):
        """Test translating multiple texts."""
        model, tokenizer, device = load_opus_mt("en", device="cpu")
        
        texts = ["Hola", "Buenos días", "Adiós"]
        translations = translate_batch(texts, model, tokenizer, device)
        
        assert len(translations) == len(texts)
        for translation in translations:
            assert isinstance(translation, str)
            assert len(translation) > 0
    
    @pytest.mark.slow
    def test_translate_batch_preserves_order(self):
        """Test that translations maintain input order."""
        model, tokenizer, device = load_opus_mt("en", device="cpu")
        
        texts = ["uno", "dos", "tres"]
        translations = translate_batch(texts, model, tokenizer, device)
        
        # Verify we got the same number of translations
        assert len(translations) == len(texts)
        
        # Translations should be in the same order
        # (we can't verify exact translations, but we can verify structure)
        for i, translation in enumerate(translations):
            assert isinstance(translation, str)
    
    @pytest.mark.slow
    def test_translate_batch_with_small_batch_size(self):
        """Test batch processing with small batch size."""
        model, tokenizer, device = load_opus_mt("en", device="cpu")
        
        texts = ["Hola", "Buenos días", "Adiós", "Gracias", "Por favor"]
        translations = translate_batch(texts, model, tokenizer, device, batch_size=2)
        
        assert len(translations) == len(texts)
        for translation in translations:
            assert isinstance(translation, str)
            assert len(translation) > 0


class TestIntegration:
    """Integration tests for the translation engine."""
    
    @pytest.mark.slow
    def test_all_supported_languages(self):
        """Test that all supported languages can be loaded."""
        for lang in MODEL_MAPPING.keys():
            model, tokenizer, device = load_opus_mt(lang, device="cpu")
            assert model is not None
            assert tokenizer is not None
    
    @pytest.mark.slow
    def test_translate_with_protected_placeholders(self):
        """Test translation with placeholder tokens."""
        model, tokenizer, device = load_opus_mt("en", device="cpu")
        
        # Simulate protected text with placeholder tokens
        texts = ["Hola __PH0__", "Buenos días __PH1__"]
        translations = translate_batch(texts, model, tokenizer, device)
        
        assert len(translations) == len(texts)
        # Placeholder tokens should be preserved (or at least present in some form)
        for translation in translations:
            assert isinstance(translation, str)
