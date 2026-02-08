"""
Normalization utilities for product titles and attributes.
Additive module: safe to import without changing existing behavior.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, Optional

# Common brands (extendable)
COMMON_BRANDS = [
    "apple", "samsung", "xiaomi", "huawei", "tecno", "infinix", "nokia",
    "oppo", "vivo", "realme", "sony", "lg", "oneplus", "motorola", "lenovo",
    "hp", "dell", "asus", "acer", "msi", "toshiba", "canon", "nikon",
]

_PROMO_WORDS = {
    "promo", "offre", "réduction", "reduction", "soldes", "deal", "mega", "flash",

# Extended brand mapping for normalization
BRAND_MAPPINGS = {
    # Electronics
    "samsung": ["samsung", "sam sung", "samsumg"],
    "apple": ["apple", "iphone", "ipad", "macbook", "airpods"],
    "xiaomi": ["xiaomi", "redmi", "poco", "mi"],
    "huawei": ["huawei", "honor"],
    "oppo": ["oppo", "realme"],
    "vivo": ["vivo", "iqoo"],
    "oneplus": ["oneplus", "one plus"],
    "nokia": ["nokia"],
    "tecno": ["tecno", "camon", "spark"],
    "infinix": ["infinix", "hot", "note"],
    "itel": ["itel"],
    
    # Laptops
    "hp": ["hp", "hewlett packard"],
    "dell": ["dell"],
    "lenovo": ["lenovo", "thinkpad"],
    "asus": ["asus", "rog"],
    "acer": ["acer"],
    "msi": ["msi"],
    
    # Other
    "lg": ["lg"],
    "sony": ["sony"],
    "jbl": ["jbl"],
    "anker": ["anker"],
}

# Category mapping
CATEGORY_MAPPINGS = {
    "smartphones": ["phone", "smartphone", "mobile", "téléphone", "cellphone"],
    "laptops": ["laptop", "notebook", "ordinateur portable", "pc portable"],
    "tablets": ["tablet", "ipad", "tablette"],
    "headphones": ["headphone", "earphone", "écouteur", "casque", "airpod"],
    "smartwatches": ["smartwatch", "watch", "montre"],
    "accessories": ["case", "cover", "charger", "cable", "accessoire"],
}


def normalize_title(title: str) -> str:
    """Normalize product title for matching"""
    if not title:
        return ""
    
    # Convert to lowercase
    normalized = title.lower().strip()
    
    # Remove special characters but keep spaces and alphanumeric
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove common filler words
    filler_words = ['original', 'authentic', 'new', 'brand', 'official', 'genuine']
    for word in filler_words:
        normalized = re.sub(rf'\b{word}\b', '', normalized)
    
    return normalized.strip()


def guess_brand(title: str) -> Optional[str]:
    """Extract and normalize brand from title"""
    if not title:
        return None
    
    title_lower = title.lower()
    
    # Check against brand mappings
    for canonical_brand, variants in BRAND_MAPPINGS.items():
        for variant in variants:
            if variant in title_lower:
                return canonical_brand
    
    return None


def extract_attributes(title: str) -> Dict[str, any]:
    """
    Extract product attributes from title
    Returns dict with: capacity_gb, ram_gb, screen_inches, color
    """
    attributes = {}
    
    if not title:
        return attributes
    
    title_lower = title.lower()
    
    # Extract storage capacity (GB, TB)
    storage_patterns = [
        r'(\d+)\s*tb',  # 1TB, 2 TB
        r'(\d+)\s*gb(?!\s*ram)',  # 128GB, 256 GB (but not "8GB RAM")
    ]
    
    for pattern in storage_patterns:
        match = re.search(pattern, title_lower)
        if match:
            capacity = int(match.group(1))
            if 'tb' in match.group(0):
                capacity *= 1024  # Convert TB to GB
            attributes['capacity_gb'] = capacity
            break
    
    # Extract RAM
    ram_match = re.search(r'(\d+)\s*gb\s*ram', title_lower)
    if ram_match:
        attributes['ram_gb'] = int(ram_match.group(1))
    
    # Extract screen size
    screen_match = re.search(r'(\d+\.?\d*)\s*(?:inch|pouces|")', title_lower)
    if screen_match:
        attributes['screen_inches'] = float(screen_match.group(1))
    
    # Extract color (common colors)
    colors = ['black', 'white', 'blue', 'red', 'green', 'gold', 'silver', 'gray', 'grey', 
              'pink', 'purple', 'yellow', 'orange', 'noir', 'blanc', 'bleu', 'rouge']
    for color in colors:
        if re.search(rf'\b{color}\b', title_lower):
            attributes['color'] = color
            break
    
    return attributes


def normalize_category(category: Optional[str]) -> Optional[str]:
    """Normalize category to unified taxonomy"""
    if not category:
        return None
    
    category_lower = category.lower()
    
    for canonical_category, variants in CATEGORY_MAPPINGS.items():
        for variant in variants:
            if variant in category_lower:
                return canonical_category
    
    return category
