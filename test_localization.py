"""Quick test to verify the localization system works correctly."""

from src.locale import t, set_locale, get_locale, get_supported_locales, LocaleManager

def test_localization():
    """Test the localization system."""
    
    print("=" * 60)
    print("Testing Localization System")
    print("=" * 60)
    
    # Test 1: Get supported locales
    print("\n1. Supported locales:")
    locales = get_supported_locales()
    print(f"   {locales}")
    
    # Test 2: Test Spanish (default)
    print("\n2. Testing Spanish (es):")
    set_locale('es')
    print(f"   Current locale: {get_locale()}")
    print(f"   header: {t('header')}")
    print(f"   section_input_file: {t('section_input_file')}")
    print(f"   confirm_proceed: {t('confirm_proceed')}")
    
    # Test 3: Test English
    print("\n3. Testing English (en):")
    set_locale('en')
    print(f"   Current locale: {get_locale()}")
    print(f"   header: {t('header')}")
    print(f"   section_input_file: {t('section_input_file')}")
    print(f"   confirm_proceed: {t('confirm_proceed')}")
    
    # Test 4: Test invalid key with default
    print("\n4. Testing invalid key:")
    print(f"   t('invalid_key_xyz'): {t('invalid_key_xyz')}")
    print(f"   t('invalid_key_xyz', 'default text'): {t('invalid_key_xyz', 'default text')}")
    
    # Test 5: Test all keys (make sure none are missing)
    print("\n5. Checking for missing keys:")
    set_locale('es')
    es_keys = set(LocaleManager._translations.get('es', {}).keys())
    en_keys = set(LocaleManager._translations.get('en', {}).keys())
    
    missing_in_es = en_keys - es_keys
    missing_in_en = es_keys - en_keys
    
    if missing_in_es:
        print(f"   ⚠️  Missing in Spanish: {missing_in_es}")
    else:
        print(f"   ✓ All keys present in Spanish")
    
    if missing_in_en:
        print(f"   ⚠️  Missing in English: {missing_in_en}")
    else:
        print(f"   ✓ All keys present in English")
    
    print(f"\n   Total keys in Spanish: {len(es_keys)}")
    print(f"   Total keys in English: {len(en_keys)}")
    
    # Test 6: Show all translations
    print("\n6. All translations (Spanish):")
    set_locale('es')
    for key in sorted(es_keys):
        value = t(key)
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == '__main__':
    test_localization()
