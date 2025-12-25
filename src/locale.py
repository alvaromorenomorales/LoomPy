"""Localization system for interactive CLI."""
import json
from pathlib import Path
from typing import Dict, Optional
import locale as sys_locale
import os


class LocaleManager:
    """Manages localization files and translations."""
    
    LOCALE_DIR = Path(__file__).parent.parent / "locale"
    SUPPORTED_LOCALES = ["es", "en"]
    DEFAULT_LOCALE = "en"
    
    _instance = None
    _translations = {}
    _current_locale = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            cls._instance = super(LocaleManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the locale manager."""
        if not self._translations:
            self._load_all_locales()
            # Default to the configured DEFAULT_LOCALE (English by default).
            # The interactive CLI will allow the user to change this at startup.
            self.set_locale(self.DEFAULT_LOCALE)
    
    @classmethod
    def _load_all_locales(cls) -> None:
        """Load all available locale files."""
        for locale_code in cls.SUPPORTED_LOCALES:
            locale_file = cls.LOCALE_DIR / f"{locale_code}.json"
            if locale_file.exists():
                try:
                    with open(locale_file, "r", encoding="utf-8") as f:
                        cls._translations[locale_code] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading locale file {locale_file}: {e}")
                    cls._translations[locale_code] = {}
            else:
                print(f"Locale file not found: {locale_file}")
                cls._translations[locale_code] = {}
    
    @classmethod
    def _detect_system_locale(cls) -> str:
        """Detect the system locale and return a supported locale code."""
        # Try to get locale from environment or system
        try:
            # Get system locale (e.g., "es_ES.UTF-8" or "en_US.UTF-8")
            system_locale = sys_locale.getdefaultlocale()[0] or ""
            
            # Extract language code (e.g., "es" from "es_ES")
            if system_locale:
                lang_code = system_locale.split("_")[0].lower()
                if lang_code in cls.SUPPORTED_LOCALES:
                    return lang_code
        except Exception:
            pass
        
        # Try to get from environment variable
        for env_var in ["LANG", "LANGUAGE", "LC_ALL"]:
            locale_str = os.environ.get(env_var, "").split(":")[0]
            if locale_str:
                lang_code = locale_str.split("_")[0].lower()
                if lang_code in cls.SUPPORTED_LOCALES:
                    return lang_code
        
        # Return default locale
        return cls.DEFAULT_LOCALE
    
    def set_locale(self, locale_code: str) -> bool:
        """
        Set the current locale.
        
        Args:
            locale_code: Language code (e.g., "es", "en")
            
        Returns:
            bool: True if locale was set successfully, False otherwise
        """
        if locale_code not in self.SUPPORTED_LOCALES:
            return False
        
        self._current_locale = locale_code
        return True
    
    def get_current_locale(self) -> str:
        """Get the current locale code."""
        return self._current_locale or self.DEFAULT_LOCALE
    
    def get_supported_locales(self) -> list:
        """Get list of supported locale codes."""
        return self.SUPPORTED_LOCALES.copy()
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        """
        Translate a key to the current locale.
        
        Args:
            key: Translation key (e.g., "header", "section_input_file")
            default: Default text if key is not found
            
        Returns:
            str: Translated text or default or the key itself
        """
        locale = self.get_current_locale()
        
        # Get from current locale
        if locale in self._translations:
            if key in self._translations[locale]:
                return self._translations[locale][key]
        
        # Fallback to English
        if "en" in self._translations:
            if key in self._translations["en"]:
                return self._translations["en"][key]
        
        # Return default or key
        return default or key
    
    def translate(self, key: str, default: Optional[str] = None) -> str:
        """Alias for t() method."""
        return self.t(key, default)


# Global instance
_locale_manager = None


def get_locale_manager() -> LocaleManager:
    """Get or create the locale manager singleton."""
    global _locale_manager
    if _locale_manager is None:
        _locale_manager = LocaleManager()
    return _locale_manager


def t(key: str, default: Optional[str] = None) -> str:
    """
    Convenience function to translate a key.
    
    Args:
        key: Translation key
        default: Default text if key is not found
        
    Returns:
        str: Translated text
    """
    return get_locale_manager().t(key, default)


def set_locale(locale_code: str) -> bool:
    """
    Convenience function to set the current locale.
    
    Args:
        locale_code: Language code (e.g., "es", "en")
        
    Returns:
        bool: True if successful
    """
    return get_locale_manager().set_locale(locale_code)


def get_locale() -> str:
    """Get the current locale code."""
    return get_locale_manager().get_current_locale()


def get_supported_locales() -> list:
    """Get list of supported locales."""
    return get_locale_manager().get_supported_locales()
