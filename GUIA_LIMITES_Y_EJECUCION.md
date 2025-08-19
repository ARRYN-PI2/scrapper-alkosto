# 🚀 Alkosto Scraper - Guía de Límites y Ejecución

## 📋 Descripción

El Alkosto Scraper es una herramienta para extraer información de productos del sitio web de Alkosto. Incluye múltiples opciones para configurar límites y controlar la velocidad de extracción.

## ⚙️ Tipos de Límites Disponibles

### 🔢 Límites de Cantidad
- **`max_productos`**: Número máximo de productos a extraer
- **Rango recomendado**: 5-500 productos
- **Por defecto**: 20 productos

### ⏱️ Límites Temporales
- **`delay_between_requests`**: Tiempo de espera entre requests
- **Rango recomendado**: 0.5-5.0 segundos
- **Por defecto**: 1.0 segundos

### 📂 Límites por Categoría
| Categoría | Máximo Recomendado | URL Base |
|-----------|-------------------|----------|
| televisores | 200 | https://www.alkosto.com/tv/smart-tv/c/BI_120_ALKOS |
| celulares | 300 | https://www.alkosto.com/celulares/smartphones/c/BI_101_ALKOS |
| audifonos | 200 | https://www.alkosto.com/audio/audifonos/c/BI_111_ALKOS |
| videojuegos | 500 | https://www.alkosto.com/videojuegos/c/BI_VIJU_ALKOS |
| domotica | 150 | https://www.alkosto.com/casa-inteligente-domotica/c/BI_CAIN_ALKOS |

## 🎯 Formas de Ejecutar el Scraper

### 1. 🏃‍♂️ Ejecución Rápida (Script Básico)

**Archivo**: `ejecutar_scraper.py`

```bash
# Editar configuración en el archivo
python ejecutar_scraper.py
```

**Configuración** (modificar variables en el archivo):
```python
CATEGORIA = "televisores"  # Cambiar categoría
LIMITE_PRODUCTOS = 10      # Cambiar límite
DELAY_SEGUNDOS = 1.0       # Cambiar delay
```

### 2. 🔧 Ejecución Avanzada (Script Completo)

**Archivo**: `ejecutar_scraper_completo.py`

```bash
# Ver categorías disponibles
python ejecutar_scraper_completo.py --listar-categorias

# Scraping básico
python ejecutar_scraper_completo.py --categoria televisores --limite 20

# Scraping con delay personalizado
python ejecutar_scraper_completo.py --categoria celulares --limite 50 --delay 2.0

# Ver todas las opciones
python ejecutar_scraper_completo.py --help
```

**Parámetros disponibles**:
- `--categoria, -c`: Categoría a scrapear (default: televisores)
- `--limite, -l`: Número máximo de productos (default: 20)
- `--delay, -d`: Tiempo entre requests en segundos (default: 1.0)
- `--no-generico`: Usar entidades específicas en lugar de ProductoGenerico
- `--listar-categorias`: Mostrar categorías disponibles

### 3. 📚 Ver Ejemplos de Configuración

**Archivo**: `ejemplos_limites.py`

```bash
# Ejecutar ejemplos completos
python ejemplos_limites.py
```

## 🎮 Ejemplos de Uso

### Ejemplo 1: Prueba Rápida
```bash
# Extraer 5 televisores con delay normal
python ejecutar_scraper_completo.py --categoria televisores --limite 5
```

### Ejemplo 2: Muestreo Medio
```bash
# Extraer 50 celulares con delay conservador
python ejecutar_scraper_completo.py --categoria celulares --limite 50 --delay 2.0
```

### Ejemplo 3: Extracción Completa
```bash
# Extraer todos los audifonos disponibles
python ejecutar_scraper_completo.py --categoria audifonos --limite 200 --delay 1.5
```

### Ejemplo 4: Categorías Específicas
```bash
# Videojuegos (categoría con más productos)
python ejecutar_scraper_completo.py --categoria videojuegos --limite 100

# Domótica (categoría especializada)
python ejecutar_scraper_completo.py --categoria domotica --limite 30
```

## 🛠️ Uso Programático

### Importar y usar directamente:

```python
from AlkostoScraperHibrido import AlkostoScraperHibrido

# Crear scraper
scraper = AlkostoScraperHibrido(
    categoria="televisores",
    modo_generico=True,
    delay_between_requests=1.0
)

# Obtener URLs de productos
urls = scraper.get_product_urls_with_load_more(max_productos=20)

# Extraer productos
productos = []
for url in urls:
    try:
        producto = scraper.scrape_product(url)
        productos.append(producto)
    except Exception as e:
        print(f"Error: {e}")

print(f"Extraídos: {len(productos)} productos")
```

## 📊 Configuración de Límites Recomendada

### Por Tipo de Uso:

| Uso | Límite Productos | Delay | Tiempo Estimado |
|-----|-----------------|-------|-----------------|
| **Prueba rápida** | 5-10 | 1.0s | 30-60 segundos |
| **Desarrollo** | 20-50 | 1.0s | 2-5 minutos |
| **Muestreo** | 50-100 | 1.5s | 5-10 minutos |
| **Producción** | 100-500 | 2.0s | 10-60 minutos |

### Por Categoría:

| Categoría | Prueba | Desarrollo | Producción |
|-----------|--------|------------|------------|
| **televisores** | 5 | 20 | 100-200 |
| **celulares** | 5 | 30 | 100-300 |
| **audifonos** | 5 | 25 | 100-200 |
| **videojuegos** | 10 | 50 | 200-500 |

## 🛡️ Límites de Seguridad

El scraper incluye varios mecanismos de seguridad:

- **User-Agent rotativo**: Evita detección como bot
- **Delays automáticos**: Previene sobrecarga del servidor
- **Timeout de requests**: 30 segundos máximo por request
- **Límite de páginas**: Máximo 10 páginas por búsqueda
- **Manejo de errores**: Continúa ejecutándose aunque fallen algunos productos

## 📁 Archivos de Salida

Los datos se guardan en:
- **Directorio**: `data/output/`
- **Formato**: JSON
- **Nombre**: `alkosto_{categoria}_{timestamp}.json`

### Estructura del JSON:
```json
{
  "categoria": "televisores",
  "timestamp_extraccion": "20240812_143022",
  "total_productos": 20,
  "productos": [
    {
      "nombre": "Smart TV Samsung 55\" 4K UHD",
      "precio": 1599000,
      "marca": "Samsung",
      "categoria": "televisores",
      "url_producto": "https://www.alkosto.com/...",
      "timestamp_extraccion": "2024-08-12T14:30:22",
      "atributos_extra": {...}
    }
  ]
}
```

## 🚨 Recomendaciones Importantes

### ✅ Buenas Prácticas:
1. **Empezar con límites pequeños** (5-10 productos) para probar
2. **Usar delays apropiados** (mínimo 1.0 segundos)
3. **Verificar la categoría** antes de ejecutar
4. **Monitorear errores** durante la ejecución

### ⚠️ Precauciones:
1. **No usar delays muy pequeños** (< 0.5s) - riesgo de bloqueo
2. **No extraer más de 500 productos** de una vez
3. **Revisar logs** si hay muchos errores 404
4. **Respetar el sitio web** - no sobrecargar el servidor

## 🐛 Solución de Problemas

### Error: URLs no encontradas
```bash
# Verificar categoría
python ejecutar_scraper_completo.py --listar-categorias

# Probar con límite más pequeño
python ejecutar_scraper_completo.py --categoria televisores --limite 5
```

### Error: Productos sin datos
- Aumentar el delay entre requests
- Verificar conectividad a internet
- Revisar si la URL de la categoría es correcta

### Error: Precios incorrectos
- El parsing de precios puede fallar en algunos productos
- Los datos se guardan aunque el precio sea incorrecto
- Revisar manualmente los productos con precios extraños

## 📞 Ayuda

Para ver todas las opciones disponibles:
```bash
python ejecutar_scraper_completo.py --help
```

Para ver ejemplos de configuración:
```bash
python ejemplos_limites.py
```
