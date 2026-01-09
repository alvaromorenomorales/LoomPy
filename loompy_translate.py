#!/usr/bin/env python3
"""
loompy_translate.py

Translate a JSON file to multiple target languages using Helsinki-NLP Opus-MT models.
Each language uses a separate model.
Only string values are translated; keys remain unchanged.
Placeholders like {name} or %s are preserved.
"""

import json
import os
import re
import argparse
from copy import deepcopy
from typing import Any, Dict, List, Tuple

import torch
from transformers import MarianMTModel, MarianTokenizer

# ---------- Placeholder utilities ----------
PLACEHOLDER_RE = re.compile(r'(\{[^}]+\}|%s|%\([^\)]+\)s)')

def extract_placeholders(text: str) -> Tuple[str, Dict[str, str]]:
    placeholders = {}
    def repl(m):
        idx = len(placeholders)
        token = f"__PH{idx}__"
        placeholders[token] = m.group(0)
        return token
    transformed = PLACEHOLDER_RE.sub(repl, text)
    return transformed, placeholders

def restore_placeholders(text: str, mapping: Dict[str, str]) -> str:
    for token, orig in mapping.items():
        text = text.replace(token, orig)
    return text

# ---------- JSON traversal ----------
def collect_string_paths(obj: Any, path: Tuple = ()) -> List[Tuple[Tuple, str]]:
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            results.extend(collect_string_paths(v, path + (k,)))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(collect_string_paths(item, path + (i,)))
    elif isinstance(obj, str):
        results.append((path, obj))
    return results

def set_by_path(root: Any, path: Tuple, value: Any) -> None:
    cur = root
    for key in path[:-1]:
        cur = cur[key]
    cur[path[-1]] = value

# ---------- Model loading & translation ----------
def load_opus_mt(model_name: str, device: str = None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    model.to(device)
    return model, tokenizer, device

def translate_batch(texts: List[str], model, tokenizer, device: str, max_length: int = 512) -> List[str]:
    translated = []
    batch_size = 16
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        encoded = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=max_length).to(device)
        generated = model.generate(**encoded, max_length=max_length)
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translated.extend(decoded)
    return translated

def translate_json_values(src_obj: Any, model, tokenizer, device: str) -> Any:
    result = deepcopy(src_obj)
    paths_and_texts = collect_string_paths(src_obj)
    if not paths_and_texts:
        return result

    paths, texts = zip(*paths_and_texts)
    transformed_texts = []
    placeholder_maps = []
    for t in texts:
        t_transformed, mapping = extract_placeholders(t)
        transformed_texts.append(t_transformed)
        placeholder_maps.append(mapping)

    translated_texts = translate_batch(list(transformed_texts), model, tokenizer, device)
    final_texts = [restore_placeholders(tr, mapping) for tr, mapping in zip(translated_texts, placeholder_maps)]

    for path, new_val in zip(paths, final_texts):
        set_by_path(result, path, new_val)

    return result

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Translate JSON file to multiple languages using Opus-MT.")
    parser.add_argument("input", nargs="?", default="es.json", help="Input Spanish JSON file (default: es.json)")
    parser.add_argument("--out-dir", default=".", help="Output directory for translated files")
    parser.add_argument("--langs", nargs="+", default=["en", "fr", "ca"], help="Target language codes (default: en fr ca)")
    parser.add_argument("--device", default=None, choices=["cpu", "cuda"], help="Device to run on (default auto detect)")
    args = parser.parse_args()

    # Map target language codes to Opus-MT model names
    model_map = {
        "en": "Helsinki-NLP/opus-mt-es-en",
        "fr": "Helsinki-NLP/opus-mt-es-fr",
        "ca": "Helsinki-NLP/opus-mt-es-ca"  # If not available, use a workaround
    }

    with open(args.input, "r", encoding="utf-8") as f:
        src = json.load(f)

    os.makedirs(args.out_dir, exist_ok=True)

    for lang in args.langs:
        model_name = model_map.get(lang)
        if not model_name:
            print(f"No Opus-MT model defined for language {lang}, skipping.")
            continue
        print(f"Loading model for {lang}: {model_name}")
        model, tokenizer, device = load_opus_mt(model_name, args.device)
        print(f"Translating to {lang} ...")
        translated = translate_json_values(src, model, tokenizer, device)
        out_file = os.path.join(args.out_dir, f"{lang}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(translated, f, ensure_ascii=False, indent=2)
        print(f"Written {out_file}")

if __name__ == "__main__":
    main()