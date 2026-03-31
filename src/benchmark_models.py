"""
Benchmark: Opus-MT vs NLLB-200 (distilled-600M)
Traduce input/es.json de español a inglés con ambos modelos y compara tiempos y calidad.
"""

import json
import time
import sys
import os
import torch
from pathlib import Path

# Aumentar timeout de descarga de HuggingFace
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "120"


def extract_strings(obj, path=""):
    """Extrae todas las cadenas traducibles de un JSON anidado."""
    results = []
    if isinstance(obj, str):
        results.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            results.extend(extract_strings(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            results.extend(extract_strings(v, f"{path}[{i}]"))
    return results


def translate_with_opus_mt(texts, device):
    """Traduce con Helsinki-NLP/opus-mt-es-en (MarianMT)."""
    from transformers import MarianMTModel, MarianTokenizer

    model_name = "Helsinki-NLP/opus-mt-es-en"
    print(f"\n{'='*60}")
    print(f"  OPUS-MT ({model_name})")
    print(f"{'='*60}")

    print("  Cargando modelo...")
    t0 = time.time()
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name).to(device)
    model.eval()
    load_time = time.time() - t0
    print(f"  Modelo cargado en {load_time:.2f}s (device: {device})")

    print(f"  Traduciendo {len(texts)} cadenas...")
    batch_size = 32
    translations = []
    t0 = time.time()
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        encoded = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        encoded = {k: v.to(device) for k, v in encoded.items()}
        with torch.no_grad():
            generated = model.generate(**encoded)
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translations.extend(decoded)
        done = min(i + batch_size, len(texts))
        print(f"    [{done}/{len(texts)}]", end="\r")
    translate_time = time.time() - t0
    print(f"  Traduccion completada en {translate_time:.2f}s")

    # Liberar memoria
    del model, tokenizer
    if device == "cuda":
        torch.cuda.empty_cache()

    return translations, load_time, translate_time


def translate_with_nllb(texts, device):
    """Traduce con facebook/nllb-200-distilled-600M."""
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    model_name = "facebook/nllb-200-distilled-600M"
    print(f"\n{'='*60}")
    print(f"  NLLB-200 ({model_name})")
    print(f"{'='*60}")

    print("  Cargando modelo...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    model.eval()
    load_time = time.time() - t0
    print(f"  Modelo cargado en {load_time:.2f}s (device: {device})")

    print(f"  Traduciendo {len(texts)} cadenas...")
    batch_size = 32
    translations = []
    t0 = time.time()

    # NLLB usa códigos FLORES-200
    tokenizer.src_lang = "spa_Latn"

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        encoded = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=512)
        encoded = {k: v.to(device) for k, v in encoded.items()}
        with torch.no_grad():
            generated = model.generate(
                **encoded,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids("eng_Latn")
            )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translations.extend(decoded)
        done = min(i + batch_size, len(texts))
        print(f"    [{done}/{len(texts)}]", end="\r")
    translate_time = time.time() - t0
    print(f"  Traduccion completada en {translate_time:.2f}s")

    # Liberar memoria
    del model, tokenizer
    if device == "cuda":
        torch.cuda.empty_cache()

    return translations, load_time, translate_time


def main():
    input_file = Path("input/es.json")
    if not input_file.exists():
        print(f"Error: {input_file} no encontrado")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    pairs = extract_strings(data)
    texts = [text for _, text in pairs]
    keys = [key for key, _ in pairs]

    print(f"Fichero: {input_file}")
    print(f"Cadenas a traducir: {len(texts)}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # --- NLLB-200 primero (necesita descarga) ---
    nllb_translations, nllb_load, nllb_translate = translate_with_nllb(texts, device)

    # --- Opus-MT ---
    opus_translations, opus_load, opus_translate = translate_with_opus_mt(texts, device)

    # --- Resultados ---
    print(f"\n{'='*60}")
    print(f"  RESULTADOS")
    print(f"{'='*60}")
    print(f"  {'Metrica':<30} {'Opus-MT':>12} {'NLLB-200':>12}")
    print(f"  {'-'*54}")
    print(f"  {'Tiempo carga modelo (s)':<30} {opus_load:>12.2f} {nllb_load:>12.2f}")
    print(f"  {'Tiempo traduccion (s)':<30} {opus_translate:>12.2f} {nllb_translate:>12.2f}")
    print(f"  {'Tiempo total (s)':<30} {opus_load+opus_translate:>12.2f} {nllb_load+nllb_translate:>12.2f}")
    print(f"  {'Cadenas/segundo':<30} {len(texts)/opus_translate:>12.1f} {len(texts)/nllb_translate:>12.1f}")
    print(f"  {'Cadenas traducidas':<30} {len(opus_translations):>12} {len(nllb_translations):>12}")

    # Muestras comparativas
    print(f"\n{'='*60}")
    print(f"  MUESTRAS COMPARATIVAS (10 aleatorias)")
    print(f"{'='*60}")
    import random
    random.seed(42)
    sample_indices = random.sample(range(len(texts)), min(10, len(texts)))
    for idx in sample_indices:
        print(f"\n  Key: {keys[idx]}")
        print(f"  ES:      {texts[idx][:80]}")
        print(f"  Opus-MT: {opus_translations[idx][:80]}")
        print(f"  NLLB:    {nllb_translations[idx][:80]}")

    # Guardar resultados completos
    output = {
        "benchmark": {
            "device": device,
            "total_strings": len(texts),
            "opus_mt": {
                "model": "Helsinki-NLP/opus-mt-es-en",
                "load_time_s": round(opus_load, 2),
                "translate_time_s": round(opus_translate, 2),
                "total_time_s": round(opus_load + opus_translate, 2),
                "strings_per_second": round(len(texts) / opus_translate, 1)
            },
            "nllb_200": {
                "model": "facebook/nllb-200-distilled-600M",
                "load_time_s": round(nllb_load, 2),
                "translate_time_s": round(nllb_translate, 2),
                "total_time_s": round(nllb_load + nllb_translate, 2),
                "strings_per_second": round(len(texts) / nllb_translate, 1)
            }
        },
        "samples": [
            {
                "key": keys[idx],
                "source_es": texts[idx],
                "opus_mt_en": opus_translations[idx],
                "nllb_200_en": nllb_translations[idx]
            }
            for idx in sample_indices
        ]
    }

    output_file = Path("output/benchmark_results.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  Resultados guardados en {output_file}")


if __name__ == "__main__":
    main()
