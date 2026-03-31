
import time
import sys
import os
import copy
from pathlib import Path

from .file_io import load_json_file
from .translation_pipeline import translate_json_values
from .config import DEFAULT_DEVICE
from .translation_engine import NLLBTranslationProvider

def run_multi_lang_benchmark():
    input_file = "input/public.json"
    source_lang = "es"
    target_langs = ["en", "fr", "ca"]
    
    print(f"Loading source file: {input_file}")
    source_data = load_json_file(input_file)
    
    provider = NLLBTranslationProvider()
    
    # --- PRUEBA 1: EN SERIE (COMO ESTÁ AHORA) ---
    print("\n" + "="*50)
    print("PRUEBA 1: TRADUCCIÓN EN SERIE (UNO A UNO)")
    print("="*50)
    
    start_total_serie = time.time()
    
    for lang in target_langs:
        print(f"\nTraduciedo a {lang.upper()}...")
        start_lang = time.time()
        
        provider.load_model(source_lang, lang, DEFAULT_DEVICE)
        
        def translate_func(texts):
            return provider.translate_batch(texts)
            
        translated_data = translate_json_values(source_data, translate_func)
        
        duration_lang = time.time() - start_lang
        print(f"V {lang.upper()} completado en {duration_lang:.2f}s")
        
    total_duration_serie = time.time() - start_total_serie
    print(f"\nTOTAL SERIE: {total_duration_serie:.2f}s")
    
    # --- PRUEBA 2: EN PARALELO (BATCH MULTI-IDIOMA) ---
    print("\n" + "="*50)
    print("PRUEBA 2: TRADUCCIÓN EN PARALELO (NUEVA LÓGICA)")
    print("="*50)
    
    start_total_parallel = time.time()
    
    # 1. Recolectar todos los textos a traducir del JSON
    from .json_traversal import collect_string_paths
    from .placeholder_protection import extract_placeholders
    
    string_paths = collect_string_paths(source_data)
    protected_texts = []
    for _, original_text in string_paths:
        p_text, _ = extract_placeholders(original_text)
        protected_texts.append(p_text)
    
    # Eliminar duplicados para máxima velocidad
    unique_texts = list(set(protected_texts))
    
    print(f"Textos únicos a traducir: {len(unique_texts)}")
    print(f"Idiomas destino: {len(target_langs)}")
    
    # Simulación de lo que haría el nuevo motor
    # En lugar de iterar por idioma y luego por batch, 
    # podemos iterar por batch y dentro traducir a N idiomas
    
    results = {lang: {} for lang in target_langs}
    
    # Cargar modelo (solo una vez necesario para NLLB)
    provider.load_model(source_lang, target_langs[0], DEFAULT_DEVICE)
    
    batch_size = 96
    for i in range(0, len(unique_texts), batch_size):
        batch = unique_texts[i:i + batch_size]
        
        # Tokenización común
        provider.tokenizer.src_lang = provider.lang_map.get(source_lang, "spa_Latn")
        encoded = provider.tokenizer(batch, truncation=True, max_length=512)
        source_tokens = [provider.tokenizer.convert_ids_to_tokens(ids) for ids in encoded["input_ids"]]
        
        for lang in target_langs:
            tgt_prefix = provider.lang_map.get(lang, "eng_Latn")
            
            # Traducción masiva al idioma actual
            step_results = provider.translator.translate_batch(
                source_tokens,
                target_prefix=[[tgt_prefix]] * len(batch),
                beam_size=1
            )
            
            for original, res in zip(batch, step_results):
                trans_text = provider.tokenizer.decode(
                    provider.tokenizer.convert_tokens_to_ids(res.hypotheses[0]),
                    skip_special_tokens=True
                )
                results[lang][original] = trans_text
                
    total_duration_parallel = time.time() - start_total_parallel
    print(f"\nTOTAL PARALELO (SIMULADO): {total_duration_parallel:.2f}s")
    
    # --- RESULTADOS ---
    print("\n" + "="*50)
    print("COMPARATIVA MULTI-IDIOMA")
    print("="*50)
    print(f"Tiempo en Serie:     {total_duration_serie:.2f}s")
    print(f"Tiempo en Paralelo:  {total_duration_parallel:.2f}s")
    improvement = total_duration_serie / total_duration_parallel
    print(f"Mejora:              {improvement:.2f}x más rápido")

if __name__ == "__main__":
    run_multi_lang_benchmark()
