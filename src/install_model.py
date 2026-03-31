"""
LoomPy - Pre-installation Script
Downloads and converts the NLLB-200-600M model to CTranslate2 format.
"""

import os
import sys

def install_package(package):
    print(f"  [+] Installing {package} via pip...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except Exception as e:
        print(f"  [!] Failed to install {package}: {e}")
        sys.exit(1)

# Ensure dependencies are available
try:
    import ctranslate2
    import transformers
except ImportError:
    print("\n[!] Pre-requisites not found. Attempting automatic installation...")
    install_package("ctranslate2")
    install_package("transformers")
    print("[V] Dependencies installed. Continuing with model setup...")
    # Refresh imports
    import ctranslate2
    import transformers

from .translation_engine import NLLBTranslationProvider
from .config import get_model_path
from .logger import log_progress

def main():
    model_path = get_model_path()
    
    print("\n" + "="*70)
    print("  LoomPy - NLLB-200-600M MODEL PRE-INSTALLATION")
    print("="*70)
    
    if os.path.exists(model_path):
        print(f"\n[V] Model already installed at: {model_path}")
        print("    If you want to reinstall, please delete the folder.")
        return

    print("\nStarting download and optimization (int8)...")
    print("This may take several minutes depending on your internet speed.")
    
    try:
        # Initialize provider which triggers the internal _ensure_local_model()
        provider = NLLBTranslationProvider()
        
        # We trigger model loading with a dummy language pair to force the conversion
        # NLLB is multilingual, so it doesn't matter which one we use for loading.
        provider.load_model(source_language="es", target_language="en")
        
        print(f"\n[V] SUCCESS: Model optimized and saved to: {model_path}")
        print("\nNow you can run translations at full speed with NLLB-200!")
        print("Example: python -m src.main --langs en fr\n")
        
    except Exception as e:
        print(f"\n[!] ERROR during installation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
