## CLI Interactivo

Se ha agregado una interfaz de línea de comandos interactiva para facilitar el uso del traductor sin necesidad de recordar todas las opciones.

### Uso Básico

Para iniciar el modo interactivo, ejecuta:

```bash
python -m src.main --interactive
```

O de forma más corta:

```bash
python -m src.main -i
```

### Flujo de la CLI Interactiva

La CLI te hará preguntas paso a paso. Atención: la primera pregunta ahora solicita el idioma de la interfaz (por defecto en inglés).

#### 1. **Idioma de la interfaz (CLI)**
```
▶ 1. Selecciona el idioma de la interfaz
  1. en - English
  2. es - Español
Selecciona una opción (1-2): 
```
- Por defecto la interfaz aparece en inglés (`en`). Puedes cambiarla aquí antes de continuar con las demás preguntas.

#### 2. **Archivo a traducir**
```
▶ 2. Archivo a traducir
Directorio de entrada: input
Introduce el nombre o ruta del archivo JSON [es.json]: 
```
- Puedes escribir solo el nombre (`es.json`) si está en la carpeta `input/`
- O una ruta completa/relativa
- Si el archivo no existe, te mostrará los archivos disponibles

#### 3. **Idioma de origen**
```
▶ 3. ¿De qué idioma quieres traducir?
  1. es
  2. en
  3. fr
  4. ca
  5. de
Selecciona una opción (1-5): 
```
- Los idiomas soportados como origen son: es, en, fr, ca, de
- Los idiomas disponibles como destino dependen del idioma de origen

#### 3. **Idiomas destino**
```
▶ 3. Idiomas destino
  1. en
  2. fr
  3. ca
Introduce los números separados por espacios o comas [1,2,3]: 
```
- Puedes seleccionar uno o más idiomas
- Sepáralos con espacios: `1 2 3`
- O con comas: `1,2,3`
- Por defecto se seleccionan: English, French, Catalan (si están disponibles)

#### 4. **Directorio de salida**
```
▶ 4. Directorio de salida
Directorio predeterminado: output
¿Quieres usar un directorio personalizado? [s/N]: 
```
- Por defecto se usa `output/`
- Si escribes `s` (sí), puedes especificar otro directorio

#### 5. **Opciones del archivo de origen**
```
▶ 5. Opciones del archivo de origen
¿Quieres actualizar el archivo original con claves ordenadas y duplicados eliminados? [s/N]: 
```
- Si respondes `s`, el archivo original se sobrescribirá con la versión limpia y ordenada
- Si respondes `n`, se te preguntará si quieres guardar una copia:
  ```
  ¿Quieres guardar una copia limpia y ordenada en el directorio de salida? [s/N]: 
  ```

#### 6. **Dispositivo de procesamiento**
```
▶ 6. Dispositivo de procesamiento
  1. Automático (detectar GPU/CPU) - Recomendado
  2. CPU
  3. CUDA (GPU)
Selecciona un dispositivo (1-3): 
```
- **Automático**: Detecta y usa GPU si está disponible, sino usa CPU
- **CPU**: Fuerza el uso de procesador (más lento pero compatible)
- **CUDA**: Usa GPU (requiere NVIDIA y CUDA instalado)

#### 7. **Resumen y confirmación**
```
============================================================
              RESUMEN DE CONFIGURACIÓN
============================================================
Archivo:            input/es.json
Idioma origen:      ES
Idiomas destino:    EN, FR, CA
Directorio salida:  output
Actualizar origen:  No
Guardar copia:      No
Dispositivo:        AUTO

¿Continuar con la traducción? [S/n]: 
```
- Revisa la configuración
- Responde `s` para continuar o `n` para cancelar

### Ejemplos

#### Iniciar en modo interactivo (por defecto en inglés)
```bash
python -m src.main -i
# En la primera pregunta selecciona idioma de la interfaz (Enter = English por defecto)
```

#### Traducir de inglés a varios idiomas
```bash
python -m src.main -i
# 1. Archivo: input.json
# 2. Idioma origen: 2 (English)
# 3. Idiomas destino: 1 2 (Spanish, French)
# 4. Directorio: output (por defecto)
# 5. Opciones: n (no actualizar original)
# 6. Dispositivo: 1 (automático)
# 7. Confirmar: s (sí, continuar)
```

#### Traducciones personalizadas
```bash
python -m src.main -i
# Sigue el flujo interactivo
# La CLI se adaptará según tu selección
```

### Comparación: CLI tradicional vs CLI interactivo

**CLI tradicional (sin --interactive):**
```bash
python -m src.main input/es.json --source-lang es --langs en fr ca --update-source --device cpu
```

**CLI interactivo:**
```bash
python -m src.main --interactive
# Te guía paso a paso de forma más amigable
```

### Respuestas rápidas

La CLI acepta varios formatos de respuesta:

#### Para confirmaciones (Sí/No):
- **Sí**: `s`, `si`, `sí`, `y`, `yes`
- **No**: `n`, `no`
- **Por defecto**: Si presionas Enter sin escribir nada

#### Para seleccionar opciones:
```bash
# Todas estas formas funcionan igual:
1 2 3     # separado por espacios
1, 2, 3   # separado por comas
1,2,3     # sin espacios
```

#### Para archivos:
```bash
# Todas estas formas funcionan:
es.json              # solo el nombre (busca en "input/")
input/es.json        # ruta relativa
/ruta/completa.json  # ruta absoluta
```

### Colores y símbolos

La CLI usa colores para mejorar la legibilidad:

- 🔵 **Azul** (`▶`): Secciones principales
- 🟢 **Verde** (`✓`): Confirmaciones y éxito
- 🟡 **Amarillo**: Números de opciones y advertencias
- 🔴 **Rojo** (`✗`): Errores
- 🔵 **Cyan** (`═`): Encabezados y énfasis

Ejemplo:
```
✓ Archivo encontrado: input/es.json
✓ Idioma seleccionado: es
✓ Idiomas seleccionados: en, fr, ca
✗ El archivo no existe: archivo.json
```

### Flujo de cancelación

En cualquier momento puedes:

1. **Antes de confirmar**: Responde `n` a la pregunta final
   ```
   ¿Continuar con la traducción? [S/n]: n
   Operación cancelada
   ```

2. **Presionar Ctrl+C**: Cancela la ejecución
   ```
   ^C
   ```

### Notas importantes

- **Validación automática**: Si introduces datos inválidos, la CLI te lo indicará y volverá a preguntar
- **Valores por defecto**: Todos tienen valores por defecto sensatos (presiona Enter)
- **Idiomas disponibles**: Dependen del idioma de origen seleccionado
- **Archivos**: Debe existir el archivo antes de continuar

### Próximos pasos

Después de completar la traducción:

1. Los archivos traducidos se guardan en el directorio especificado
2. Se muestra un resumen de las traducciones completadas
3. Si hubo errores, se indican al final
