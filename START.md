# 🚀 Guide de Démarrage Complet

## Ce qui est prêt maintenant

✅ **Backend complet** avec API REST fonctionnelle  
✅ **Frontend React** avec authentification  
✅ **Celery** pour scraping automatique  
✅ **Docker** pour déploiement facile  

---

## Démarrage Rapide (5 minutes)

### 1. Démarrer les services Docker

```powershell
cd d:\dev\price-tracker-IA

# Utiliser le helper script
.\dev.ps1 setup      # Créer .env (si pas déjà fait)
.\dev.ps1 up         # Démarrer MySQL, Redis, Backend, Celery
.\dev.ps1 status     # Vérifier que tout tourne
```

### 2. Créer la base de données

```powershell
# Créer et appliquer les migrations
.\dev.ps1 migration  # Message: "Initial migration"
.\dev.ps1 migrate    # Appliquer à la DB
```

### 3. Démarrer le frontend

```powershell
# Dans un nouveau terminal
cd frontend
npm install          # Installer les dépendances (première fois)
npm run dev          # Démarrer Vite
```

### 4. Ouvrir l'application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs (Swagger UI)

---

## Test du Flux Complet

### A. Créer un compte

1. Aller sur http://localhost:5173
2. Cliquer "Inscription"
3. Remplir le formulaire:
   - Nom: Test User
   - Email: test@example.com
   - Téléphone: +22997123456
   - Mot de passe: password123
4. S'inscrire

### B. Se connecter

1. Email: test@example.com
2. Mot de passe: password123
3. Cliquer "Se connecter"

### C. Tester l'API directement

Aller sur http://localhost:8000/docs

#### 1. Créer un compte (via Swagger)

```json
POST /api/v1/auth/register
{
  "email": "api@test.com",
  "phone": "+22997111222",
  "full_name": "API Test",
  "password": "secure123"
}
```

#### 2. Se connecter

```
POST /api/v1/auth/login
Form Data:
  username: api@test.com
  password: secure123
```

Copier l'`access_token` retourné.

#### 3. Autoriser dans Swagger

1. Cliquer sur "Authorize" (🔓 en haut)
2. Coller le token: `Bearer <votre_token>`
3. Cliquer "Authorize"

#### 4. Scraper un produit Jumia

```json
POST /api/v1/products/scrape
{
  "url": "https://www.jumia.com.bj/...",  # URL réelle d'un produit
  "marketplace": "jumia"
}
```

#### 5. Tracker le produit

```json
POST /api/v1/products/track
{
  "product_id": "<id_du_produit>",
  "target_price": 50000
}
```

#### 6. Voir mes produits trackés

```
GET /api/v1/products/tracked
```

#### 7. Créer une alerte

```json
POST /api/v1/alerts
{
  "product_id": "<id_du_produit>",
  "alert_type": "target_price",
  "threshold_value": 45000,
  "notification_channel": "email"
}
```

---

## Tester le Scraping Automatique (Celery)

### Lancer manuellement une tâche

```powershell
# Accéder au container backend
docker-compose exec backend python

# Dans Python:
from app.tasks.scraping_tasks import scrape_product_task
scrape_product_task.delay("<product_id>")
```

### Vérifier les logs Celery

```powershell
# Worker logs
.\dev.ps1 logs celery_worker

# Beat logs (scheduled tasks)
.\dev.ps1 logs celery_beat
```

---

## Fonctionnalités Disponibles

### ✅ Implémenté

| Feature | Status | Notes |
|---------|--------|-------|
| Inscription utilisateur | ✅ | Validation numéro béninois |
| Connexion JWT | ✅ | Token refresh automatique |
| Scraping Jumia | ✅ | Avec anti-bot |
| Scraping Amazon | ✅ | USD → XOF conversion |
| API Produits | ✅ | Search, track, untrack |
| API Alertes | ✅ | 4 types d'alertes |
| Celery Scraping | ✅ | Toutes les 12h |
| Celery Alerts | ✅ | Toutes les heures |
| Frontend Auth | ✅ | Login, register, private routes |
| Frontend Home | ✅ | Landing page |
| Frontend Pricing | ✅ | Free vs Premium |

###  🚧 À Implémenter (optionnel)

| Feature | Priority | Difficulté |
|---------|----------|-----------|
| Prophet ML | Moyenne | Difficile |
| Ollama AI Advice | Moyenne | Moyenne |
| Telegram Bot | Haute | Facile |
| WhatsApp (Twilio) | Moyenne | Facile |
| KKiapay Payment | Haute | Moyenne |
| Dashboard UI complet | Haute | Moyenne |
| Charts Recharts | Moyenne | Facile |
| BCEAO API | Basse | Moyenne |

---

## Structure des Fichiers Créés

### Backend (Complet)

```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── auth.py          ✅ Register, login, refresh
│   │   ├── products.py      ✅ CRUD, search, track
│   │   └── alerts.py        ✅ CRUD, test notification
│   ├── models/              ✅ Tous les modèles DB
│   ├── schemas/             ✅ Pydantic validation
│   ├── services/scraper/    ✅ Jumia + Amazon
│   ├── tasks/               ✅ Celery scraping + ML
│   ├── core/                ✅ Config, security, JWT
│   └── main.py              ✅ FastAPI app
├── alembic/                 ✅ Migrations
├── Dockerfile               ✅
├── requirements.txt         ✅
└── test_scraper.py          ✅
```

### Frontend (Core Complet)

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Navbar.jsx   ✅ Avec user menu
│   │   │   ├── Footer.jsx   ✅
│   │   │   └── Loader.jsx   ✅
│   │   └── auth/
│   │       └── PrivateRoute.jsx ✅
│   ├── pages/
│   │   ├── HomePage.jsx      ✅ Landing
│   │   ├── LoginPage.jsx     ✅ Avec validation
│   │   ├── RegisterPage.jsx  ✅ Validation Benin phone
│   │   ├── PricingPage.jsx   ✅ Free vs Premium
│   │   ├── DashboardPage.jsx 🚧 Placeholder
│   │   ├── ProductDetailPage.jsx 🚧
│   │   ├── AlertsPage.jsx    🚧
│   │   └── ProfilePage.jsx   🚧
│   ├── services/
│   │   └── api.js            ✅ Axios + token refresh
│   ├── store/
│   │   └── authStore.js      ✅ Zustand auth
│   ├── App.jsx               ✅ Routing
│   └── main.jsx              ✅ React Query + Toast
├── package.json              ✅
├── vite.config.js            ✅ API proxy
└── tailwind.config.js        ✅ Benin colors
```

---

## Prochaines Étapes (Optionnelles)

### Pour un MVP complet:

1. **Compléter le Dashboard**
   - Hook `useProducts` avec React Query
   - Afficher liste des produits trackés
   - Bouton "Ajouter produit" avec URL input

2. **Ajouter les Charts**
   - Installer composant Recharts
   - Endpoint `/api/v1/prices/{product_id}/history`
   - Afficher graphique ligne sur ProductDetailPage

3. **Intégrer Telegram**
   - Créer bot via @BotFather
   - Implémenter `telegram_bot.py`
   - Tester envoi alerte

4. **Ajouter KKiapay**
   - S'inscrire sur kkiapay.me
   - Implémenter webhook
   - Tester paiement test

### Pour un produit production:

5. **Tests automatisés**
   - Pytest pour backend (auth, products, alerts)
   - Jest pour frontend

6. **CI/CD**
   - GitHub Actions workflow
   - Auto-deploy sur Render (backend) + Vercel (frontend)

7. **Monitoring**
   - Sentry pour error tracking
   - Logs centralisés

---

## Commandes Utiles

### Backend

```powershell
# Logs en temps réel
.\dev.ps1 logs backend

# Shell Python
.\dev.ps1 shell
>>> from app.models.user import User
>>> # Tester des queries

# Nouvelle migration
.\dev.ps1 migration
# Message: "Add new field"

# Rollback migration
docker-compose exec backend alembic downgrade -1

# Tests
.\dev.ps1 test
```

### Frontend

```powershell
cd frontend

# Dev server
npm run dev

# Build production
npm run build

# Preview build
npm run preview
```

### Database

```powershell
# MySQL shell
.\dev.ps1 db-shell

# Requêtes SQL
SELECT * FROM users;
SELECT * FROM products;
SELECT COUNT(*) FROM price_history;
```

---

## Résolution de Problèmes

### Backend ne démarre pas

```powershell
# Vérifier les logs
.\dev.ps1 logs backend

# Reconstruire
.\dev.ps1 rebuild
```

### Frontend erreur de compilation

```powershell
cd frontend
rm -rf node_modules
rm package-lock.json
npm install
npm run dev
```

### Migrations échouent

```powershell
# Supprimer toutes les migrations
rm backend/alembic/versions/*.py

# Recréer from scratch
.\dev.ps1 migration
# Message: "Fresh start"

.\dev.ps1 migrate
```

### Port déjà utilisé

```powershell
# Trouver le processus
netstat -ano | findstr :8000  # Backend
netstat -ano | findstr :5173  # Frontend
netstat -ano | findstr :3306  # MySQL

# Tuer le processus (remplacer PID)
taskkill /F /PID <PID>
```

---

## Variables d'Environnement Importantes

Modifier `.env` pour activer les features:

```env
# Ollama (IA gratuite)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Telegram
TELEGRAM_BOT_TOKEN=<votre_token>

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=<sid>
TWILIO_AUTH_TOKEN=<token>

# KKiapay
KKIAPAY_PUBLIC_KEY=<public>
KKIAPAY_PRIVATE_KEY=<private>
KKIAPAY_SECRET=<secret>
```

---

## Déploiement Production

### Backend (Railway/Render)

1. Push code sur GitHub
2. Connecter repo sur Railway
3. Ajouter MySQL addon
4. Ajouter Redis addon
5. Variables d'environnement:
   ```
   DATABASE_URL=<from_addon>
   REDIS_URL=<from_addon>
   JWT_SECRET_KEY=<generate_random>
   ```

### Frontend (Vercel)

```powershell
cd frontend
npm install -g vercel
vercel
```

Suivre les prompts.

---

## 🎉 Félicitations!

Vous avez maintenant:
- ✅ Un backend FastAPI complet
- ✅ Un frontend React fonctionnel
- ✅ Un système de scraping automatique
- ✅ Une authentification sécurisée
- ✅ Des alertes configurables

**Prêt pour le marché béninois! 🇧🇯💰**

Questions? Consultez:
- README.md
- QUICKSTART.md
- walkthrough.md
- http://localhost:8000/docs (API interactive)
