## Sistema de Localización (i18n)

Se ha implementado un sistema de localización para la CLI interactiva que permite traducir todos los textos a diferentes idiomas.

### Estructura de archivos

```
locale/
├── es.json    # Textos en español
└── en.json    # Textos en inglés
```

### Módulo `src/locale.py`

El módulo `locale.py` proporciona las siguientes funciones:

#### Funciones principales:

```python
from src.locale import t, set_locale, get_locale, get_supported_locales

# Obtener texto traducido
texto = t('header')  # Obtiene la traducción de la clave 'header'

# Establecer idioma
set_locale('en')  # Cambiar a inglés
set_locale('es')  # Cambiar a español

# Obtener idioma actual
idioma = get_locale()  # Retorna 'es' o 'en'

# Obtener idiomas soportados
idiomas = get_supported_locales()  # ['es', 'en']
```

#### Clase `LocaleManager`:

```python
from src.locale import LocaleManager, get_locale_manager

# Obtener instancia singleton
manager = get_locale_manager()

# Traducir
texto = manager.t('header')
texto = manager.translate('header')  # Alias

# Cambiar idioma
manager.set_locale('en')

# Obtener idioma actual
idioma = manager.get_current_locale()

# Idiomas soportados
idiomas = manager.get_supported_locales()
```

### Archivos de idioma

Los archivos de idioma son archivos JSON con estructura clave-valor:

#### `locale/es.json`:
```json
{
  "header": "JSON TRANSLATOR - CLI INTERACTIVO",
  "section_input_file": "1. Archivo a traducir",
  "input_dir_label": "Directorio de entrada",
  ...
}
```

#### `locale/en.json`:
```json
{
  "header": "JSON TRANSLATOR - INTERACTIVE CLI",
  "section_input_file": "1. File to translate",
  "input_dir_label": "Input directory",
  ...
}
```

### Detección automática de idioma y comportamiento por defecto

El sistema intenta detectar automáticamente el idioma del sistema y además la CLI pregunta primero qué idioma usar para la propia interfaz.

1. **Locale del sistema**: Usa `locale.getdefaultlocale()` para detectar el idioma del sistema
2. **Variables de entorno**: Comprueba `LANG`, `LANGUAGE`, `LC_ALL`
3. **Valor por defecto**: Si no se detecta nada, la aplicación ahora usa `en` (inglés) como `DEFAULT_LOCALE` por defecto
4. **Selección del usuario**: Al iniciar la CLI interactiva se preguntará explícitamente por el idioma de la interfaz y ese valor tiene prioridad inmediata

Ejemplo en Linux/Mac (forzar idioma de la sesión):
```bash
# Forzar español
export LANG=es_ES.UTF-8
python -m src.main --interactive

# Forzar inglés
export LANG=en_US.UTF-8
python -m src.main --interactive
```

Ejemplo en Windows PowerShell:
```powershell
# Forzar español
$env:LANG='es_ES.UTF-8'
python -m src.main --interactive

# Forzar inglés
$env:LANG='en_US.UTF-8'
python -m src.main --interactive
```

### Cómo agregar un nuevo idioma

1. **Crear archivo de idioma**:
   Crea `locale/codigo.json` (ej: `locale/fr.json` para francés)

2. **Copiar estructura**:
   Copia todas las claves de `locale/es.json`:
   ```json
   {
     "header": "JSON TRANSLATOR - CLI INTERACTIF",
     "section_input_file": "1. Fichier à traduire",
     ...
   }
   ```

3. **Agregar código de idioma**:
   Modifica `src/locale.py` para incluir el nuevo código:
   ```python
   SUPPORTED_LOCALES = ["es", "en", "fr"]
   ```

4. **Traducir todas las claves**:
   Asegúrate de que todas las claves estén presentes en el nuevo archivo.

### Estructura de claves de idioma

Las claves se organizan por categorías:

#### Encabezados y secciones:
- `header` - Título principal
- `header_summary` - Título del resumen
- `section_input_file` - Sección 1
- `section_source_lang` - Sección 2
- `section_target_langs` - Sección 3
- `section_output_dir` - Sección 4
- `section_source_options` - Sección 5
- `section_device` - Sección 6

#### Prompts y etiquetas:
- `input_file_prompt` - Pregunta para archivo
- `choose_source_lang` - Pregunta para idioma origen
- `choose_target_langs` - Pregunta para idiomas destino
- `input_dir_label` - Etiqueta de directorio entrada
- `output_dir_label` - Etiqueta de directorio salida
- `custom_output_dir` - Pregunta sobre directorio personalizado

#### Mensajes de dispositivo:
- `device_auto` - Automático
- `device_auto_desc` - Descripción (Recomendado)
- `device_cpu` - CPU
- `device_cuda` - CUDA (GPU)
- `device_prompt` - Pregunta de dispositivo
- `device_selected_auto` - Confirmación automático
- `device_selected_cpu` - Confirmación CPU
- `device_selected_cuda` - Confirmación CUDA

#### Mensajes de confirmación:
- `update_source_prompt` - Actualizar archivo original
- `save_clean_copy` - Guardar copia limpia
- `confirm_proceed` - Continuar con traducción

#### Mensajes de estado:
- `file_found` - Archivo encontrado
- `file_not_found` - Archivo no encontrado
- `lang_selected` - Idioma seleccionado
- `langs_selected` - Idiomas seleccionados
- `using_directory` - Usando directorio
- `operation_cancelled` - Operación cancelada
- `saving_to_original` - Se guardará en el original

#### Resumen:
- `summary_file` - Archivo
- `summary_source_lang` - Idioma origen
- `summary_target_langs` - Idiomas destino
- `summary_output_dir` - Directorio salida
- `summary_update_source` - Actualizar origen
- `summary_save_copy` - Guardar copia
- `summary_device` - Dispositivo
- `summary_yes` - Sí
- `summary_no` - No

#### Mensajes de error:
- `invalid_device` - Opción no válida
- `invalid_input` - Entrada no válida
- `invalid_numbers` - Números fuera de rango
- `empty_path` - Ruta vacía
- `langs_required` - Se requiere al menos un idioma
- `enter_number` - Introduce un número

#### Instrucciones:
- `target_langs_instruction` - Cómo seleccionar idiomas
- `available_files` - Archivos disponibles en
- `no_files` - Sin archivos JSON
- `select_option` - Selecciona una opción
- `select_languages` - Selecciona idiomas

### Ejemplo: Agregar soporte para francés

1. **Crear `locale/fr.json`**:
```json
{
  "header": "JSON TRANSLATOR - CLI INTERACTIF",
  "section_input_file": "1. Fichier à traduire",
  "input_dir_label": "Répertoire d'entrée",
  "input_file_prompt": "Entrez le nom ou le chemin du fichier JSON",
  ...
}
```

2. **Actualizar `src/locale.py`**:
```python
SUPPORTED_LOCALES = ["es", "en", "fr"]
```

3. **Usar francés**:
```bash
export LANG=fr_FR.UTF-8
python -m src.main --interactive
```

### Fallback de idiomas

Si una clave no se encuentra en el idioma actual:
1. Intenta obtenerla del idioma actual
2. Si no está, intenta del inglés (fallback)
3. Si no está en ninguno, retorna la clave como texto

```python
# Ejemplo
t('key_not_found', 'texto por defecto')  # Retorna 'texto por defecto'
t('key_not_found')  # Retorna 'key_not_found'
```

### Pruebas del sistema de localización

Prueba que el sistema funciona correctamente:

```bash
# Español (defecto)
python -m src.main --interactive

# Inglés
export LANG=en_US.UTF-8
python -m src.main --interactive

# O fuerza idioma en código
python -c "from src.locale import set_locale; set_locale('en')"
```

### Notas importantes

1. **Singleton**: Solo hay una instancia de `LocaleManager` en toda la aplicación
2. **Thread-safe**: El sistema carga los archivos al inicializar
3. **UTF-8**: Todos los archivos JSON deben estar en UTF-8
4. **Claves completas**: Todas las claves deben estar en todos los idiomas
5. **Fallback automático**: Si falta una traducción, usa inglés como fallback
