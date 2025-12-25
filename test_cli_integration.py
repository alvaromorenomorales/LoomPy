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
    assert 'es' in locales, "Spanish not in supported locales"
    assert 'en' in locales, "English not in supported locales"
    print(f"✓ Supported locales: {locales}")
    
    # Test translations
    set_locale('es')
    header_es = t('header')
    assert 'INTERACTIVO' in header_es, "Spanish header missing 'INTERACTIVO'"
    print(f"✓ Spanish translation works: '{header_es}'")
    
    set_locale('en')
    header_en = t('header')
    assert 'INTERACTIVE' in header_en, "English header missing 'INTERACTIVE'"
    print(f"✓ English translation works: '{header_en}'")
    
    # Test fallback
    set_locale('en')
    current = get_locale()
    assert current == 'en', f"Current locale should be 'en' but is '{current}'"
    print(f"✓ Locale switching works: {current}")
    
    print("\n" + "="*60)
    print("All integration tests passed!")
    print("="*60)

if __name__ == '__main__':
    test_cli_imports()
