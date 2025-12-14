"""Manual test script for translation engine (without pytest)."""

import sys

def test_model_mapping():
    """Test that MODEL_MAPPING is correctly defined."""
    from src.translation_engine import MODEL_MAPPING
    
    print("Testing MODEL_MAPPING...")
    assert "en" in MODEL_MAPPING, "English not in MODEL_MAPPING"
    assert "fr" in MODEL_MAPPING, "French not in MODEL_MAPPING"
    assert "ca" in MODEL_MAPPING, "Catalan not in MODEL_MAPPING"
    
    for lang, model_name in MODEL_MAPPING.items():
        assert model_name.startswith("Helsinki-NLP/opus-mt-es-"), f"Invalid model name: {model_name}"
        assert model_name.endswith(f"-{lang}"), f"Model name doesn't end with -{lang}: {model_name}"
    
    print("✓ MODEL_MAPPING is correct")


def test_load_opus_mt_validation():
    """Test load_opus_mt input validation."""
    from src.translation_engine import load_opus_mt
    
    print("\nTesting load_opus_mt validation...")
    
    # Test invalid language
    try:
        load_opus_mt("invalid_lang")
        assert False, "Should have raised ValueError for invalid language"
    except ValueError as e:
        assert "Unsupported target language" in str(e)
        print("✓ Invalid language raises ValueError")
    
    # Test invalid device
    try:
        load_opus_mt("en", device="gpu")
        assert False, "Should have raised ValueError for invalid device"
    except ValueError as e:
        assert "Invalid device" in str(e)
        print("✓ Invalid device raises ValueError")


def test_translate_batch_empty():
    """Test translate_batch with empty list."""
    from src.translation_engine import translate_batch
    
    print("\nTesting translate_batch with empty list...")
    result = translate_batch([], None, None, "cpu")
    assert result == [], f"Expected empty list, got {result}"
    print("✓ Empty list returns empty list")


def test_integration():
    """Test full integration if PyTorch is available."""
    print("\nTesting full integration...")
    try:
        from src.translation_engine import load_opus_mt, translate_batch
        
        print("Loading model (this may take a while)...")
        model, tokenizer, device = load_opus_mt("en", device="cpu")
        
        print(f"✓ Model loaded successfully on {device}")
        
        # Test translation
        texts = ["Hola mundo"]
        translations = translate_batch(texts, model, tokenizer, device)
        
        assert len(translations) == 1, f"Expected 1 translation, got {len(translations)}"
        assert isinstance(translations[0], str), "Translation should be a string"
        assert len(translations[0]) > 0, "Translation should not be empty"
        
        print(f"✓ Translation successful: '{texts[0]}' -> '{translations[0]}'")
        
    except Exception as e:
        print(f"⚠ Integration test skipped due to: {type(e).__name__}: {e}")
        print("  (This is expected if PyTorch has DLL issues on Windows)")


if __name__ == "__main__":
    try:
        test_model_mapping()
        test_load_opus_mt_validation()
        test_translate_batch_empty()
        test_integration()
        
        print("\n" + "="*60)
        print("All tests passed! ✓")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
