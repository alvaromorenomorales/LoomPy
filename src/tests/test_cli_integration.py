"""Quick integration test of the interactive CLI imports."""

def test_cli_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    # Test locale imports
    from src.locale import t, set_locale, get_locale, get_supported_locales
    print("✓ Locale imports successful")
    
    # Test interactive_cli imports
    from src.interactive_cli import run_interactive_cli
    print("✓ Interactive CLI imports successful")
    
    # Test that locale functions work
    locales = get_supported_locales()
    assert 'spa_Latn' in locales, f"Spanish (spa_Latn) not in supported locales: {locales}"
    assert 'eng_Latn' in locales, f"English (eng_Latn) not in supported locales: {locales}"
    print(f"✓ Supported locales: {locales}")
    
    # Test translations
    set_locale('spa_Latn')
    header_es = t('header')
    assert 'INTERACTIVO' in header_es, "Spanish header missing 'INTERACTIVO'"
    print(f"✓ Spanish translation works: '{header_es}'")
    
    set_locale('eng_Latn')
    header_en = t('header')
    assert 'INTERACTIVE' in header_en, "English header missing 'INTERACTIVE'"
    print(f"✓ English translation works: '{header_en}'")
    
    # Test fallback
    set_locale('eng_Latn')
    current = get_locale()
    assert current == 'eng_Latn', f"Current locale should be 'eng_Latn' but is '{current}'"
    print(f"✓ Locale switching works: {current}")
    
    print("\n" + "="*60)
    print("All integration tests passed!")
    print("="*60)

if __name__ == '__main__':
    test_cli_imports()
