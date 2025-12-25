## Carpeta `locale/`

Contiene los archivos de traducción para la CLI interactiva.

### Archivos

- **`es.json`** - Textos en español (idioma por defecto)
- **`en.json`** - Textos en inglés

### Cómo funciona

Cada archivo JSON contiene pares clave-valor con las traducciones de todos los textos de la CLI interactiva:

```json
{
  "header": "JSON TRANSLATOR - CLI INTERACTIVO",
  "section_input_file": "1. Archivo a traducir",
  ...
}
```

### Agregar un nuevo idioma

Para agregar soporte para un nuevo idioma:

1. Copia uno de los archivos existentes (ej: `es.json`)
2. Crea un nuevo archivo con el código de idioma (ej: `fr.json` para francés)
3. Traduce todos los valores manteniendo las claves iguales
4. Actualiza `src/locale.py` agregando el código a `SUPPORTED_LOCALES`

### Detección automática

El sistema detecta automáticamente el idioma del sistema:
- En Linux/Mac: Usa la variable `LANG`
- En Windows: Intenta detectar desde configuración regional
- Fallback: Usa español si no puede detectar

Para forzar un idioma:
```bash
export LANG=en_US.UTF-8  # Linux/Mac
$env:LANG='en_US.UTF-8'  # Windows PowerShell
```

### Validación

Se proporcionan 54 claves de traducción que cubre todos los textos de la CLI:
- Títulos y secciones
- Preguntas y prompts
- Etiquetas y descripciones
- Mensajes de confirmación
- Mensajes de error y estado

### Estructura de archivos

```
locale/
├── es.json  # 54 claves en español
└── en.json  # 54 claves en inglés
```

Para más detalles, ver [LOCALIZATION.md](../LOCALIZATION.md)
