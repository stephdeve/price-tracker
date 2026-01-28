# Contributing to Price Tracker Bénin

Merci de votre intérêt pour contribuer au projet ! 🇧🇯

## 🌟 Code de Conduite

- Soyez respectueux et inclusif
- Concentrez-vous sur les solutions, pas les personnes
- Acceptez les critiques constructives
- Aidez les nouveaux contributeurs

## 🚀 Comment contribuer

### 1. Signaler un Bug

Créez une issue avec :
- Description claire du problème
- Étapes pour reproduire
- Comportement attendu vs actuel
- Captures d'écran si applicable
- Version (backend, frontend, Docker)

### 2. Proposer une Fonctionnalité

Créez une issue "Feature Request" avec :
- Contexte et cas d'utilisation
- Description détaillée
- Exemples ou maquettes
- Impact sur l'existant

### 3. Contribuer du Code

#### Setup

```powershell
# Fork le repo sur GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/price-tracker-IA.git
cd price-tracker-IA

# Ajouter l'upstream remote
git remote add upstream https://github.com/ORIGINAL/price-tracker-IA.git

# Setup l'environnement
.\dev.ps1 setup
.\dev.ps1 up
```

#### Workflow

1. **Créer une branche**
   ```powershell
   git checkout -b feature/amazing-feature
   # ou
   git checkout -b fix/bug-description
   ```

2. **Faire vos changements**
   - Suivre les conventions de code (voir ci-dessous)
   - Ajouter des tests si applicable
   - Mettre à jour la documentation

3. **Tester**
   ```powershell
   .\dev.ps1 test
   .\dev.ps1 test-scraper
   ```

4. **Commit**
   ```powershell
   git add .
   git commit -m "Add: Description de la feature"
   ```

5. **Push et Pull Request**
   ```powershell
   git push origin feature/amazing-feature
   ```
   
   Créez une PR sur GitHub avec :
   - Titre clair
   - Description des changements
   - Screenshots si UI
   - Référence aux issues liées

## 📝 Conventions de Code

### Backend (Python)

#### Style
- PEP 8 (utilisez `black` pour formatter)
- Type hints pour les fonctions
- Docstrings pour les fonctions publiques

```python
async def scrape_product(url: str) -> Optional[Dict[str, Any]]:
    """
    Scrape a single product from URL
    
    Args:
        url: Product URL to scrape
        
    Returns:
        Product data dict or None if failed
    """
    ...
```

#### Imports
```python
# Standard library
import asyncio
from typing import Optional

# Third-party
from fastapi import APIRouter

# Local
from app.models.product import Product
```

#### Nommage
- Variables/fonctions : `snake_case`
- Classes : `PascalCase`
- Constantes : `UPPER_SNAKE_CASE`
- Privé : `_prefixed`

### Frontend (React/JavaScript)

#### Style
- ESLint + Prettier
- PascalCase pour components
- camelCase pour fonctions/variables
- UPPER_SNAKE_CASE pour constantes

```jsx
// Good
const ProductCard = ({ product }) => {
  const [isLoading, setIsLoading] = useState(false);
  const API_BASE_URL = "http://localhost:8000";
  
  return <div>{product.name}</div>;
};

export default ProductCard;
```

#### Fichiers
- Un component par fichier
- Nommer le fichier comme le component
- Index.js pour exports de dossier

### Git Commits

Format : `Type: Description courte`

Types:
- `Add:` Nouvelle fonctionnalité
- `Fix:` Correction de bug  
- `Update:` Modification existante
- `Remove:` Suppression
- `Refactor:` Restructuration
- `Docs:` Documentation
- `Test:` Tests
- `Style:` Formatting, pas de changement de logique

Exemples:
```
Add: Jumia category scraping
Fix: Price parsing for products without decimals
Update: Increase scraping retry limit to 5
Docs: Add API documentation for alerts endpoint
```

## 🧪 Tests

### Backend

```powershell
# Run all tests
.\dev.ps1 test

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py -v

# With coverage
docker-compose exec backend pytest --cov=app --cov-report=html
```

### Frontend (à venir)

```bash
cd frontend
npm test
npm run test:coverage
```

## 📚 Documentation

### Code Comments

Commentez le "pourquoi", pas le "quoi" :

```python
# ❌ Bad
# Increment counter
counter += 1

# ✅ Good
# Retry count must stay under limit to prevent infinite loops
if retry_count >= MAX_RETRIES:
    return None
```

### API Documentation

Utilisez les docstrings FastAPI :

```python
@router.post("/products/track", response_model=TrackedProductResponse)
async def track_product(
    product_data: TrackedProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Track a product for price monitoring
    
    - **product_id**: UUID of product to track
    - **target_price**: Optional price threshold for alerts
    
    Returns tracked product with creation timestamp
    """
    ...
```

## 🎯 Zones qui ont besoin d'aide

### Critiques (Haute priorité)

- [ ] API endpoints (auth, products, alerts)
- [ ] Celery tasks pour scraping automatique
- [ ] ML predictions avec Prophet
- [ ] Frontend React complet

### Importantes

- [ ] Tests automatisés (backend + frontend)
- [ ] CI/CD pipeline GitHub Actions
- [ ] Intégration KKiapay réelle
- [ ] Amazon Product Advertising API

### Nice-to-have

- [ ] Support d'autres marketplaces (AliExpress, etc.)
- [ ] Extension Chrome pour tracking rapide
- [ ] Application mobile (React Native)
- [ ] Dashboard admin
- [ ] Notifications push web

## 🐛 Signaler des Problèmes de Sécurité

**Ne pas** créer une issue publique.

Envoyez un email privé à : security@example.com (à configurer)

Include:
- Description de la vulnérabilité
- Étapes pour reproduire
- Impact potentiel
- Suggestions de correction si possible

## 💬 Questions ?

- GitHub Discussions
- Issues avec label "question"
- Discord (à créer si communauté grandit)

## 📄 Licence

En contribuant, vous acceptez que vos contributions soient sous licence MIT.

---

Merci de contribuer au Price Tracker Bénin! 🙏🇧🇯
