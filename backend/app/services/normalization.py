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
    "official", "store", "original", "neuf", "garantie", "livraison"
}

_WS_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")
_CAPACITY_RE = re.compile(r"(\d+)\s?(gb|go)", re.IGNORECASE)
_SIZE_INCH_RE = re.compile(r"(\d{1,2}(?:\.\d)?)\s?(''|\"|pouces|inch|in)", re.IGNORECASE)


def _ascii_lower(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    return s.lower()


def normalize_title(title: str) -> str:
    """Lowercase, strip accents, remove promo words/punctuations, collapse spaces."""
    t = _ascii_lower(title)
    # remove promo words
    tokens = [tok for tok in _NON_ALNUM_RE.split(t) if tok and tok not in _PROMO_WORDS]
    return _WS_RE.sub(" ", " ".join(tokens)).strip()


def extract_attributes(title: str) -> Dict[str, Optional[float]]:
    t = _ascii_lower(title)
    attrs: Dict[str, Optional[float]] = {
        "capacity_gb": None,
        "size_inch": None,
    }
    m = _CAPACITY_RE.search(t)
    if m:
        try:
            attrs["capacity_gb"] = float(m.group(1))
        except Exception:
            pass
    m2 = _SIZE_INCH_RE.search(t)
    if m2:
        try:
            attrs["size_inch"] = float(m2.group(1))
        except Exception:
            pass
    return attrs


def guess_brand(title: str) -> Optional[str]:
    t = _ascii_lower(title)
    for b in COMMON_BRANDS:
        if re.search(rf"\b{re.escape(b)}\b", t):
            return b
    return None
