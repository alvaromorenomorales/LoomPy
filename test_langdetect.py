import json
import time
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

def detectar_idioma_json(ruta_archivo: str):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        def get_all_values(obj):
            values = []
            if isinstance(obj, dict):
                for v in obj.values():
                    values.extend(get_all_values(v))
            elif isinstance(obj, list):
                for item in obj:
                    values.extend(get_all_values(item))
            elif isinstance(obj, str):
                values.append(obj)
            return values

        textos = get_all_values(datos)
        muestra_texto = " ".join([str(t) for t in textos[:20]])
        
        if not muestra_texto.strip():
            return None

        return detect(muestra_texto)
    except Exception as e:
        print(f"Error: {e}")
        return None

# Create a test json
test_json = "test_es.json"
with open(test_json, "w", encoding="utf-8") as f:
    json.dump({"test": "Hola, ¿cómo estás? Esto es una prueba en español."}, f)

start = time.time()
lang = detectar_idioma_json(test_json)
end = time.time()
print(f"Detected: {lang} in {end-start:.4f}s")
