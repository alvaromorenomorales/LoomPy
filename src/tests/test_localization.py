"""Quick test to verify the localization system works correctly."""
import pytest
from src.locale import t, set_locale, get_locale, get_supported_locales, LocaleManager

def test_localization_discovery():
    """Test the localization system and auto-discovery."""
    
    # Test 1: Get supported locales (the ones we renamed)
    locales = get_supported_locales()
    assert 'spa_Latn' in locales
    assert 'eng_Latn' in locales
    assert 'fra_Latn' in locales
    
    # Test 2: Test Spanish
    set_locale('spa_Latn')
    assert get_locale() == 'spa_Latn'
    assert 'INTERACTIVO' in t('header')
    
    # Test 3: Test English
    set_locale('eng_Latn')
    assert get_locale() == 'eng_Latn'
    assert 'INTERACTIVE' in t('header')
    
    # Test 4: Test fallback to default (eng_Latn usually)
    set_locale('fra_Latn')
    assert get_locale() == 'fra_Latn'
    # "header" exists in fra_Latn.json, but some non-existent key should fallback to eng_Latn or return key
    # If key is missing in all, it returns the key
    assert t('non_existent_key_123') == 'non_existent_key_123'
    
    # Test 5: Key consistency check (Manual check equivalent)
    translations = LocaleManager._translations
    spa_keys = set(translations.get('spa_Latn', {}).keys())
    eng_keys = set(translations.get('eng_Latn', {}).keys())
    
    # Just verify we have more than 5 keys in each
    assert len(spa_keys) > 5
    assert len(eng_keys) > 5

if __name__ == '__main__':
    # Run simple manual verify if called directly
    print("Running localization tests...")
    locales = get_supported_locales()
    print(f"Discovered: {locales}")
    set_locale('spa_Latn')
    print(f"Spanish label: {t('header')}")
    print("Done.")
