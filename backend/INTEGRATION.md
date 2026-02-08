# Multi-Source Price Tracker - Backend Integration

## 🎯 Nouvelles Fonctionnalités

### Scraper AliExpress
- Support complet pour AliExpress avec extraction JSON et HTML
- Compatible avec l'architecture Playwright existante
- Intégré dans les tâches Celery

### Normalisation Améliorée
- **30+ marques** avec variantes (Samsung, Apple, Xiaomi, Tecno, etc.)
- **Extraction d'attributs**: Capacité, RAM, Taille d'écran, Couleur
- **Taxonomie unifiée** pour les catégories

### Matching Multi-Étapes
1. **Exact** (SKU, EAN, UPC) → 100% confiance
2. **Fuzzy** (Similarité texte) → 85%+ confiance
3. **Sémantique** (ML embeddings) → 80%+ confiance

## 📦 Installation

```bash
cd /home/steven/dev/price-tracker/backend
pip install -r requirements.txt
```

## 🧪 Test Rapide

```bash
# Tester le scraper AliExpress
python test_aliexpress.py
```

## 📖 Documentation Complète

Voir [walkthrough.md](file:///home/steven/.gemini/antigravity/brain/c1596428-440e-4581-a2b9-94029475e888/walkthrough.md) pour tous les détails.

## ✅ Compatibilité

- ✅ Aucun changement de schéma MySQL
- ✅ Scrapers Jumia/Amazon inchangés
- ✅ Routes API compatibles
- ✅ Tâches Celery rétrocompatibles
