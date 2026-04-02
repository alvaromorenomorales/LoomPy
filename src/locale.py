"""Localization system for interactive CLI."""
import json
from pathlib import Path
from typing import Dict, Optional, List
import locale as sys_locale
import os


class LocaleManager:
    """Manages localization files and translations."""
    
    LOCALE_DIR = Path(__file__).parent.parent / "locale"
    DEFAULT_LOCALE = "eng_Latn"
    
    _instance = None
    _translations = {}
    _current_locale = None
    _supported_locales = []
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            cls._instance = super(LocaleManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the locale manager."""
        if not self._translations:
            self._discover_and_load_locales()
            # Use system detection, falling back to English if it fails to find a supported locale.
            self.set_locale(self._detect_system_locale())
    
    def _discover_and_load_locales(self) -> None:
        """Scan locale directory and load all .json files."""
        if not self.LOCALE_DIR.exists():
            return

        self._supported_locales = []
        for locale_file in self.LOCALE_DIR.glob("*.json"):
            locale_code = locale_file.stem
            try:
                with open(locale_file, "r", encoding="utf-8") as f:
                    self._translations[locale_code] = json.load(f)
                self._supported_locales.append(locale_code)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading locale file {locale_file}: {e}")
        
        if self.DEFAULT_LOCALE not in self._supported_locales and self._supported_locales:
            # If default not found, use first available
            self.DEFAULT_LOCALE = self._supported_locales[0]

    def _detect_system_locale(self) -> str:
        """Detect the system locale and return a supported locale code."""
        # Mapping from ISO 639-1 to NLLB codes for system detection
        iso_to_nllb = {
            "en": "eng_Latn",
            "es": "spa_Latn",
            "fr": "fra_Latn"
        }
        
        try:
            # Get system locale (e.g., "es_ES.UTF-8" or "en_US.UTF-8")
            system_locale = sys_locale.getdefaultlocale()[0] or ""
            
            if system_locale:
                lang_code = system_locale.split("_")[0].lower()
                nllb_code = iso_to_nllb.get(lang_code, lang_code)
                if nllb_code in self._supported_locales:
                    return nllb_code
        except Exception:
            pass
        
        return self.DEFAULT_LOCALE
    
    def set_locale(self, locale_code: str) -> bool:
        """Set the current locale."""
        if locale_code not in self._supported_locales:
            return False
        
        self._current_locale = locale_code
        return True
    
    def get_current_locale(self) -> str:
        """Get the current locale code."""
        return self._current_locale or self.DEFAULT_LOCALE
    
    def get_supported_locales(self) -> list:
        """Get list of supported locale codes."""
        return sorted(self._supported_locales.copy())
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        """Translate a key to the current locale."""
        locale = self.get_current_locale()
        
        # Get from current locale
        if locale in self._translations:
            if key in self._translations[locale]:
                return self._translations[locale][key]
        
        # Fallback to default (eng_Latn usually)
        if self.DEFAULT_LOCALE in self._translations:
            if key in self._translations[self.DEFAULT_LOCALE]:
                return self._translations[self.DEFAULT_LOCALE][key]
        
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
    """Convenience function to translate a key."""
    return get_locale_manager().t(key, default)


def set_locale(locale_code: str) -> bool:
    """Convenience function to set locale."""
    return get_locale_manager().set_locale(locale_code)


def get_locale() -> str:
    """Get current locale code."""
    return get_locale_manager().get_current_locale()


def get_supported_locales() -> list:
    """Get list of supported locales."""
    return get_locale_manager().get_supported_locales()
