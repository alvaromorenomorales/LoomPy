## 🚀 Quick Start - Sistema de Localización

### Instalación

No se requieren dependencias adicionales. Todo usa la librería estándar de Python.

```bash
# Clonar o descargar el proyecto
cd langsTranslator

# Verificar que funciona
python verify_system.py
```

### Uso Básico

La CLI interactiva ahora pregunta primero por el idioma de la interfaz; el valor por defecto es inglés (`en`).

```bash
python -m src.main --interactive
```

Al iniciar verás primero una pregunta como:

```
▶ 1. Selecciona el idioma de la interfaz
  1. en - English
  2. es - Español
Selecciona una opción (1-2):
```

Si presionas Enter en la primera pregunta la interfaz permanecerá en inglés.

### Flujo Interactivo

```
1. Selecciona idioma de la interfaz → en (Enter = English por defecto)
2. Selecciona archivo               → es.json
3. Idioma origen                    → Español
4. Idiomas destino                  → Inglés, Francés
5. Directorio de salida             → output (defecto)
6. Opciones del archivo             → No actualizar
7. Dispositivo                      → Automático
8. Confirmación                     → Sí

↓ Inicia traducción
```

### Ejemplo Completo

```bash
$ python -m src.main --interactive

╔════════════════════════════════════════════════════════╗
║    JSON TRANSLATOR - CLI INTERACTIVO                   ║
╚════════════════════════════════════════════════════════╝

▶ 1. Archivo a traducir
  Directorio de entrada: input
  Introduce el nombre o ruta del archivo JSON [es.json]: 
✓ Archivo encontrado: input/es.json

▶ 2. Idioma de origen
¿De qué idioma quieres traducir?
  1. es
  2. en
  3. fr
  4. ca
  5. de
Selecciona una opción (1-5): 1
✓ Idioma seleccionado: es

▶ 3. Idiomas destino
¿A qué idiomas quieres traducir?
  1. en
  2. fr
  3. ca
Introduce los números separados por espacios o comas [1,2,3]: 
✓ Idiomas seleccionados: en, fr, ca

▶ 4. Directorio de salida
  Directorio predeterminado: output
  ¿Quieres usar un directorio personalizado? [s/N]: n
✓ Usando directorio: output

▶ 5. Opciones del archivo de origen
  ¿Quieres actualizar el archivo original con claves ordenadas y duplicados eliminados? [s/N]: n
  ¿Quieres guardar una copia limpia y ordenada en el directorio de salida? [s/N]: n

▶ 6. Dispositivo de procesamiento
  1. Automático (detectar GPU/CPU) - Recomendado
  2. CPU
  3. CUDA (GPU)
  Selecciona un dispositivo (1-3): 1
✓ Dispositivo: automático

╔════════════════════════════════════════════════════════╗
║         RESUMEN DE CONFIGURACIÓN                       ║
╚════════════════════════════════════════════════════════╝
Archivo:            input/es.json
Idioma origen:      ES
Idiomas destino:    EN, FR, CA
Directorio salida:  output
Actualizar origen:  No
Guardar copia:      No
Dispositivo:        AUTO

¿Continuar con la traducción? [S/n]: s

✓ Iniciando traducción...
```

### Agregar Nuevo Idioma

#### Ejemplo: Francés

**Paso 1:** Crear `locale/fr.json`
```bash
cat > locale/fr.json << 'EOF'
{
  "header": "JSON TRANSLATOR - CLI INTERACTIF",
  "section_input_file": "1. Fichier à traduire",
  "input_dir_label": "Répertoire d'entrée",
  ...
}
EOF
```

**Paso 2:** Actualizar `src/locale.py`
```python
SUPPORTED_LOCALES = ["es", "en", "fr"]  # Agregar "fr"
```

**Paso 3:** Usar
```bash
export LANG=fr_FR.UTF-8
python -m src.main --interactive
```

### Testing

#### Test de Localización
```bash
python test_localization.py

# Resultado:
# ✓ All keys present in Spanish
# ✓ All keys present in English
# Total keys in Spanish: 54
# Total keys in English: 54
```

#### Test de Integración
```bash
python test_cli_integration.py

# Resultado:
# ✓ Locale imports successful
# ✓ Interactive CLI imports successful
# ✓ Supported locales: ['es', 'en']
# ✓ Spanish translation works
# ✓ English translation works
```

#### Verificar Sistema
```bash
python verify_system.py

# Resultado:
# ✓ Todos los imports funcionan correctamente
# ✓ Español: JSON TRANSLATOR - CLI INTERACTIVO
# ✓ Inglés: JSON TRANSLATOR - INTERACTIVE CLI
# ✓ Sistema de localización e CLI interactivo están listos
```

### CLI Tradicional (Aún Funciona)

```bash
# Modo no-interactivo (original)
python -m src.main input/es.json --source-lang es --langs en fr ca

# Con opciones personalizadas
python -m src.main --update-source --output-source --device cpu

# Modo interactivo (nuevo)
python -m src.main --interactive
```

### Comandos Útiles

```bash
# Ver ayuda
python -m src.main --help

# Español interactivo
python -m src.main -i

# Inglés interactivo
export LANG=en_US.UTF-8 && python -m src.main -i

# Tests
python test_localization.py
python test_cli_integration.py
python verify_system.py
```

### Documentación

- 📖 [LOCALIZATION.md](LOCALIZATION.md) - Guía técnica
- 📖 [INTERACTIVE_CLI_GUIDE.md](INTERACTIVE_CLI_GUIDE.md) - Guía de usuario
- 📖 [LOCALIZATION_SUMMARY.md](LOCALIZATION_SUMMARY.md) - Resumen
- 📖 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Estructura

### Troubleshooting

#### Problema: CLI en inglés en lugar de español
**Solución:** El sistema detectó un idioma diferente. Fuerza español:
```bash
export LANG=es_ES.UTF-8
python -m src.main --interactive
```

#### Problema: ImportError de src.locale
**Solución:** Asegúrate que estás en el directorio correcto:
```bash
cd langsTranslator
python -m src.main --interactive
```

#### Problema: Archivo no encontrado
**Solución:** Pon el archivo en `input/` o usa ruta completa:
```bash
# Defecto busca en input/
python -m src.main --interactive

# O proporciona ruta completa
python -m src.main /ruta/completa/archivo.json --interactive
```

### Próximos Pasos

1. Agregar más idiomas siguiendo el ejemplo de francés
2. Personalizar los textos según tus necesidades
3. Crear scripts para automatizar traducciones frecuentes
4. Integrar con sistema de versionado

---

**¡Listo para usar!** 🎉

```bash
python -m src.main --interactive
```
