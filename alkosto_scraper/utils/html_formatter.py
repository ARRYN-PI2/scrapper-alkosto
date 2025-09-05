"""
Utilidades para formateo y limpieza de datos
"""
import re
import html
from typing import Optional

def clean_html_details(html_text: str) -> str:
    """
    Limpia y formatea el HTML de detalles adicionales para mejor legibilidad
    
    Args:
        html_text: Texto HTML crudo
        
    Returns:
        Texto limpio y formateado
    """
    if not html_text or html_text.strip() == "":
        return ""
    
    # Decodificar entidades HTML
    text = html.unescape(html_text)
    
    # Reemplazar etiquetas de párrafo con saltos de línea
    text = re.sub(r'<p[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n', text, flags=re.IGNORECASE)
    
    # Reemplazar etiquetas de span manteniendo el contenido
    text = re.sub(r'<span[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</span>', '', text, flags=re.IGNORECASE)
    
    # Reemplazar etiquetas de div con saltos de línea
    text = re.sub(r'<div[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    
    # Reemplazar br con saltos de línea
    text = re.sub(r'<br[^>]*/?>', '\n', text, flags=re.IGNORECASE)
    
    # Formatear listas
    text = re.sub(r'<ul[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</ul>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<ol[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</ol>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', '\n• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '', text, flags=re.IGNORECASE)
    
    # Formatear encabezados
    text = re.sub(r'<h[1-6][^>]*>', '\n=== ', text, flags=re.IGNORECASE)
    text = re.sub(r'</h[1-6]>', ' ===\n', text, flags=re.IGNORECASE)
    
    # Formatear texto en negrita
    text = re.sub(r'<strong[^>]*>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'</strong>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'<b[^>]*>', '**', text, flags=re.IGNORECASE)
    text = re.sub(r'</b>', '**', text, flags=re.IGNORECASE)
    
    # Formatear texto en cursiva
    text = re.sub(r'<em[^>]*>', '*', text, flags=re.IGNORECASE)
    text = re.sub(r'</em>', '*', text, flags=re.IGNORECASE)
    text = re.sub(r'<i[^>]*>', '*', text, flags=re.IGNORECASE)
    text = re.sub(r'</i>', '*', text, flags=re.IGNORECASE)
    
    # Remover todas las demás etiquetas HTML
    text = re.sub(r'<[^>]+>', '', text)
    
    # Limpiar espacios en blanco excesivos
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
    
    text = text.strip()
    
    return text

def format_details_as_markdown(html_text: str) -> str:
    """
    Convierte HTML a formato markdown para mejor legibilidad
    
    Args:
        html_text: Texto HTML crudo
        
    Returns:
        Texto en formato markdown
    """
    if not html_text or html_text.strip() == "":
        return ""
    
    text = clean_html_details(html_text)
    
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('===') and line.endswith('==='):
            title = line.replace('===', '').strip()
            formatted_lines.append(f"## {title}")
        elif line.startswith('•'):
            formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def format_product_details(producto_dict: dict) -> dict:
    """
    Formatea los detalles adicionales de un producto
    
    Args:
        producto_dict: Diccionario del producto
        
    Returns:
        Diccionario del producto con detalles formateados
    """
    if 'detalles_adicionales' in producto_dict:
        raw_details = producto_dict['detalles_adicionales']
        
        producto_dict['detalles_adicionales_raw'] = raw_details
        producto_dict['detalles_adicionales'] = clean_html_details(raw_details)
        producto_dict['detalles_adicionales_markdown'] = format_details_as_markdown(raw_details)
    
    return producto_dict