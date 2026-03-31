"""Tests for the translation engine module."""

import pytest
import torch
from unittest.mock import patch, MagicMock
from src.translation_engine import OpusMTProvider
from src.config import SUPPORTED_LANGUAGES, get_model_name_for_pair


class TestOpusMTProvider:
    """Test the OpusMTProvider class."""
    
    def test_provider_initialization(self):
        """Test that provider initializes correctly."""
        provider = OpusMTProvider()
        assert provider.model is None
        assert provider.tokenizer is None
        assert provider.device is None
        assert provider.current_source_language is None
        assert provider.current_target_language is None


class TestLoadModel:
    """Test the load_model method."""
    
    def test_load_model_invalid_language_pair(self):
        """Test that invalid language pair raises ValueError."""
        provider = OpusMTProvider()
        with pytest.raises(ValueError, match="Unsupported language pair"):
            provider.load_model("invalid_lang", "en")
    
    def test_load_model_invalid_device(self):
        """Test that invalid device raises ValueError."""
        provider = OpusMTProvider()
        with pytest.raises(ValueError, match="Invalid device"):
            provider.load_model("es", "en", device="gpu")
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_load_model_cpu(self, mock_model, mock_tokenizer, mock_cuda):
        """Test loading model on CPU."""
        mock_cuda.return_value = False
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        provider = OpusMTProvider()
        device = provider.load_model("es", "en", device="cpu")
        
        assert device == "cpu"
        assert provider.model is not None
        assert provider.tokenizer is not None
        assert provider.device == "cpu"
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_load_model_auto_detect_gpu_available(self, mock_model, mock_tokenizer, mock_cuda):
        """Test auto-detection when GPU is available."""
        mock_cuda.return_value = True
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        provider = OpusMTProvider()
        device = provider.load_model("es", "en", device=None)
        
        assert device == "cuda"
        mock_model_instance.to.assert_called_with("cuda")
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_load_model_auto_detect_gpu_unavailable(self, mock_model, mock_tokenizer, mock_cuda):
        """Test auto-detection when GPU is not available."""
        mock_cuda.return_value = False
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        provider = OpusMTProvider()
        device = provider.load_model("es", "en", device=None)
        
        assert device == "cpu"
        mock_model_instance.to.assert_called_with("cpu")
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_load_model_cuda_fallback_to_cpu(self, mock_model, mock_tokenizer, mock_cuda):
        """Test fallback to CPU when CUDA requested but unavailable."""
        mock_cuda.return_value = False
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        provider = OpusMTProvider()
        device = provider.load_model("es", "en", device="cuda")
        
        assert device == "cpu"
        mock_model_instance.to.assert_called_with("cpu")
    
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    def test_load_model_tokenizer_error(self, mock_tokenizer):
        """Test that RuntimeError is raised when tokenizer fails."""
        mock_tokenizer.side_effect = Exception("Network error")
        
        provider = OpusMTProvider()
        with pytest.raises(RuntimeError, match="Failed to load model"):
            provider.load_model("es", "en", device="cpu")
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_load_model_caching(self, mock_model, mock_tokenizer, mock_cuda):
        """Test that model is cached and not reloaded for same language pair."""
        mock_cuda.return_value = False
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        provider = OpusMTProvider()
        
        # Load model first time
        device1 = provider.load_model("es", "en", device="cpu")
        assert device1 == "cpu"
        
        # Load same model again
        device2 = provider.load_model("es", "en", device="cpu")
        assert device2 == "cpu"
        
        # Verify from_pretrained was called only once
        assert mock_tokenizer.call_count == 1
        assert mock_model.call_count == 1



class TestTranslateBatch:
    """Test the translate_batch method."""
    
    def test_translate_batch_empty_list(self):
        """Test translating empty list returns empty list."""
        provider = OpusMTProvider()
        # Empty list should return immediately without requiring loaded model
        result = provider.translate_batch([])
        assert result == []
    
    def test_translate_batch_not_loaded(self):
        """Test that error is raised if model not loaded."""
        provider = OpusMTProvider()
        with pytest.raises(RuntimeError, match="Model and tokenizer must be loaded"):
            provider.translate_batch(["Test"])
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_translate_batch_single_text(self, mock_model, mock_tokenizer, mock_cuda):
        """Test translating a single text."""
        mock_cuda.return_value = False
        
        # Setup mocks
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        # Mock the encoding and generation
        mock_tokenizer_instance.return_value = {
            "input_ids": torch.tensor([[1, 2, 3]]),
            "attention_mask": torch.tensor([[1, 1, 1]])
        }
        mock_model_instance.generate.return_value = torch.tensor([[4, 5, 6]])
        mock_tokenizer_instance.batch_decode.return_value = ["Hello world"]
        
        provider = OpusMTProvider()
        provider.load_model("es", "en", device="cpu")
        translations = provider.translate_batch(["Hola mundo"])
        
        assert len(translations) == 1
        assert translations[0] == "Hello world"
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_translate_batch_multiple_texts(self, mock_model, mock_tokenizer, mock_cuda):
        """Test translating multiple texts."""
        mock_cuda.return_value = False
        
        # Setup mocks
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        # Mock the encoding and generation
        mock_tokenizer_instance.return_value = {
            "input_ids": torch.tensor([[1, 2, 3], [4, 5, 6]]),
            "attention_mask": torch.tensor([[1, 1, 1], [1, 1, 1]])
        }
        mock_model_instance.generate.return_value = torch.tensor([[7, 8, 9], [10, 11, 12]])
        mock_tokenizer_instance.batch_decode.return_value = ["Hello", "Good morning"]
        
        provider = OpusMTProvider()
        provider.load_model("es", "en", device="cpu")
        translations = provider.translate_batch(["Hola", "Buenos días"])
        
        assert len(translations) == 2
        assert translations == ["Hello", "Good morning"]
    
    @patch('torch.cuda.is_available')
    @patch('src.translation_engine.MarianTokenizer.from_pretrained')
    @patch('src.translation_engine.MarianMTModel.from_pretrained')
    def test_translate_batch_with_progress_callback(self, mock_model, mock_tokenizer, mock_cuda):
        """Test that progress callback is called."""
        mock_cuda.return_value = False
        
        # Setup mocks
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        mock_tokenizer.return_value = mock_tokenizer_instance
        mock_model.return_value = mock_model_instance
        
        # Mock the encoding and generation
        mock_tokenizer_instance.return_value = {
            "input_ids": torch.tensor([[1, 2, 3]]),
            "attention_mask": torch.tensor([[1, 1, 1]])
        }
        mock_model_instance.generate.return_value = torch.tensor([[4, 5, 6]])
        mock_tokenizer_instance.batch_decode.return_value = ["Hello"]
        
        # Track progress callback calls
        progress_values = []
        def progress_callback(count):
            progress_values.append(count)
        
        provider = OpusMTProvider()
        provider.load_model("es", "en", device="cpu")
        provider.translate_batch(["Hola"], progress_callback=progress_callback)
        
        assert len(progress_values) > 0
        assert progress_values[-1] == 1



class TestIntegration:
    """Integration tests for the translation engine."""
    
    @pytest.mark.slow
    def test_supported_languages_can_be_loaded(self):
        """Test that all supported target languages can be loaded."""
        provider = OpusMTProvider()
        
        # Test loading models for Spanish to English, French, Catalan
        for target_lang in ["en", "fr", "ca"]:
            device = provider.load_model("es", target_lang, device="cpu")
            assert device is not None
            assert provider.model is not None
            assert provider.tokenizer is not None

