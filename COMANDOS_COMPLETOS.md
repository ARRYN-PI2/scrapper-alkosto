# 🛒 Guía Completa de Comandos - Scrapper Alkosto
### 📱 Celulares (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria celulares --paginas 1 --output celulares_completo --hybrid
python -m alkosto_scraper.main scrape --categoria celulares --paginas 1 --output celulares_completo.csv --hybrid
```

### 📺 Televisores (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria televisores --paginas 1 --output televisores_completo --hybrid
python -m alkosto_scraper.main scrape --categoria televisores --paginas 1 --output televisores_completo.csv --hybrid
```

### 🎮 Videojuegos (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria videojuegos --paginas 1 --output videojuegos_completo --hybrid
python -m alkosto_scraper.main scrape --categoria videojuegos --paginas 1 --output videojuegos_completo.csv --hybrid
```

### 🍳 Cocina (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria cocina --paginas 1 --output cocina_completo --hybrid
python -m alkosto_scraper.main scrape --categoria cocina --paginas 1 --output cocina_completo.csv --hybrid
```

### ❄️ Refrigeración (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria refrigeracion --paginas 1 --output refrigeracion_completo --hybrid
python -m alkosto_scraper.main scrape --categoria refrigeracion --paginas 1 --output refrigeracion_completo.csv --hybrid
```

### 🧺 Lavado (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria lavado --paginas 1 --output lavado_completo --hybrid
python -m alkosto_scraper.main scrape --categoria lavado --paginas 1 --output lavado_completo.csv --hybrid
```

### 🎧 Audífonos (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria audifonos --paginas 1 --output audifonos_completo --hybrid
python -m alkosto_scraper.main scrape --categoria audifonos --paginas 1 --output audifonos_completo.csv --hybrid
```

### 🏃 Deportes (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria deportes --paginas 1 --output deportes_completo --hybrid
python -m alkosto_scraper.main scrape --categoria deportes --paginas 1 --output deportes_completo.csv --hybrid
```

### 🏠 Domótica (Completo)
```bash
python -m alkosto_scraper.main scrape --categoria domotica --paginas 1 --output domotica_completo --hybrid
python -m alkosto_scraper.main scrape --categoria domotica --paginas 1 --output domotica_completo.csv --hybrid
```

---

## 📊 Formatos de Archivos Generados

Cuando ejecutas cualquier comando, se generan automáticamente:

### Para comandos sin extensión (ej: `--output productos`)
- `productos.jsonl` - Archivo principal en formato JSON Lines
- `productos_formatted.json` - Archivo JSON formateado automáticamente ✅

### Para comandos con extensión CSV (ej: `--output productos.csv`)
- `productos.csv` - Archivo CSV para Excel/hojas de cálculo

---

## 🔧 Opciones Avanzadas

### Múltiples páginas
```bash
# Extraer 3 páginas de televisores
python -m alkosto_scraper.main scrape --categoria televisores --paginas 3 --output televisores_3_paginas --hybrid

# Extraer 5 páginas de celulares
python -m alkosto_scraper.main scrape --categoria celulares --paginas 5 --output celulares_5_paginas --hybrid
```

### Adaptador HTML Legacy (No recomendado)
```bash
python -m alkosto_scraper.main scrape --categoria televisores --paginas 1 --output televisores_legacy --legacy
```

---

## 💡 Recomendaciones

1. **Para análisis completo**: Usa siempre `--hybrid` para obtener especificaciones técnicas detalladas
2. **Para Excel**: Usa `.csv` si planeas abrir en Excel o Google Sheets
3. **Para programación**: Usa `.jsonl` para procesamiento posterior en Python/JavaScript
4. **JSON formateado**: Se genera automáticamente como `_formatted.json` para visualización

---

## 🎯 Ejemplos de Uso Común

### Análisis de mercado de televisores
```bash
python -m alkosto_scraper.main scrape --categoria televisores --paginas 3 --output analisis_tv_mercado --hybrid
```

### Comparación de precios de celulares
```bash
python -m alkosto_scraper.main scrape --categoria celulares --paginas 2 --output comparacion_celulares.csv --hybrid
```

### Inventario completo de electrodomésticos
```bash
python -m alkosto_scraper.main scrape --categoria refrigeracion --paginas 2 --output refrigeracion_inventario --hybrid
python -m alkosto_scraper.main scrape --categoria lavado --paginas 2 --output lavado_inventario --hybrid
python -m alkosto_scraper.main scrape --categoria cocina --paginas 2 --output cocina_inventario --hybrid
```

---

## ⚡ Tiempo de Ejecución Estimado

- **Comando rápido (sin `--hybrid`)**: ~10-30 segundos por página
- **Comando completo (con `--hybrid`)**: ~2-5 minutos por página (más lento pero más completo)
- **Por página**: ~50 productos promedio

---

## 🚨 Importante

- Los comandos con `--hybrid` incluyen delays para no sobrecargar el servidor
- Se recomienda empezar con 1 página para probar antes de extraer múltiples páginas
- Los archivos `_formatted.json` se crean automáticamente para facilitar la visualización
