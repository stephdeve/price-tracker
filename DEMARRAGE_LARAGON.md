# 🚀 Démarrage avec Laragon

## ✅ Avantages de Laragon

Vous avez déjà installé dans Laragon :
- ✅ **MySQL** (base de données)
- ✅ **Redis** (cache pour Celery)
- ✅ **Node.js** (pour le frontend)
- ✅ **Python** (pour le backend)

Pas besoin de Docker ! Tout est déjà là.

---

## 📋 Étape 1 : Démarrer les Services Laragon

### 1.1 Ouvrir Laragon
- Lancez **Laragon** depuis le menu Démarrer

### 1.2 Démarrer MySQL et Redis
Dans Laragon :
1. Cliquez sur **"Démarrer Tout"** (ou individuellement)
2. Vérifiez que MySQL est démarré (icône verte)
3. Pour Redis : clic droit sur Laragon → **Services** → Cocher **Redis**

> [!TIP]
> Si Redis n'apparaît pas, il est déjà dans `C:\laragon\bin\redis`. Vous pouvez le démarrer manuellement.

---

## 📋 Étape 2 : Créer la Base de Données

### 2.1 Via HeidiSQL (inclus dans Laragon)
Laragon inclut HeidiSQL pour gérer MySQL :

1. Dans Laragon, cliquez sur **"Base de données"**
2. HeidiSQL s'ouvre automatiquement
3. Clic droit sur la connexion → **Créer une base de données**
4. Nom : `price_tracker_db`
5. Encodage : `utf8mb4_general_ci`
6. Cliquez sur **OK**

### 2.2 Alternative : Via Terminal

```powershell
# Aller dans le dossier MySQL de Laragon
cd C:\laragon\bin\mysql\mysql-8.0.30\bin

# Se connecter (mot de passe par défaut : vide)
.\mysql.exe -u root -p

# Dans MySQL :
CREATE DATABASE price_tracker_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
EXIT;
```

---

## 📋 Étape 3 : Configurer le Projet

### 3.1 Créer le fichier `.env`

```powershell
# Copier le template
cd d:\dev\price-tracker-IA
Copy-Item .env.example .env
```

### 3.2 Modifier le fichier `.env`

Ouvrez `d:\dev\price-tracker-IA\.env` et modifiez :

```env
# ===== BASE DE DONNÉES MYSQL (LARAGON) =====
DATABASE_URL=mysql+aiomysql://root:@localhost:3306/price_tracker_db
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=price_tracker_db

# ===== REDIS (LARAGON) =====
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# ===== JWT =====
SECRET_KEY=votre_cle_secrete_tres_longue_et_complexe_123456789
JWT_SECRET_KEY=votre_autre_cle_secrete_pour_jwt_987654321
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ===== OLLAMA AI (Local - Gratuit) =====
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# ===== NOTIFICATIONS (optionnel pour l'instant) =====
TELEGRAM_BOT_TOKEN=
TELEGRAM_ENABLED=false
WHATSAPP_ACCOUNT_SID=
WHATSAPP_AUTH_TOKEN=
WHATSAPP_FROM_NUMBER=
WHATSAPP_ENABLED=false

# ===== PAIEMENT KKIAPAY =====
KKIAPAY_PUBLIC_KEY=votre_public_key_test
KKIAPAY_PRIVATE_KEY=votre_private_key_test
KKIAPAY_SECRET=votre_secret_test
KKIAPAY_SANDBOX=true

# ===== LIMITES =====
FREE_TIER_MAX_PRODUCTS=5
PREMIUM_TIER_MAX_PRODUCTS=100
```

> [!IMPORTANT]
> Remplacez les `SECRET_KEY` par des valeurs aléatoires sécurisées !

---

## 📋 Étape 4 : Installer et Démarrer le Backend

### 4.1 Activer l'environnement virtuel Python

```powershell
cd d:\dev\price-tracker-IA\backend

# Activer l'environnement virtuel
..\venv\Scripts\Activate.ps1
```

### 4.2 Installer les dépendances Python

```powershell
pip install -r requirements.txt
```

### 4.3 Installer Playwright (pour le scraping)

```powershell
playwright install chromium
```

### 4.4 Créer les tables de la base de données

```powershell
# Générer la migration initiale
alembic revision --autogenerate -m "Initial migration"

# Appliquer les migrations
alembic upgrade head
```

### 4.5 Démarrer le Backend FastAPI

```powershell
# Démarrer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le backend sera accessible à : **http://localhost:8000**  
La documentation API : **http://localhost:8000/docs**

> [!TIP]
> Gardez ce terminal ouvert ! Le serveur tourne ici.

---

## 📋 Étape 5 : Démarrer les Workers Celery (Tâches en arrière-plan)

### 5.1 Démarrer Redis dans Laragon
Assurez-vous que Redis est bien démarré dans Laragon.

### 5.2 Ouvrir un nouveau terminal PowerShell

```powershell
cd d:\dev\price-tracker-IA\backend
..\venv\Scripts\Activate.ps1
```

### 5.3 Démarrer Celery Worker

```powershell
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

> [!NOTE]
> L'option `--pool=solo` est nécessaire sur Windows.

### 5.4 Ouvrir un 3ème terminal pour Celery Beat (planificateur)

```powershell
cd d:\dev\price-tracker-IA\backend
..\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## 📋 Étape 6 : Démarrer le Frontend React

### 6.1 Ouvrir un nouveau terminal

```powershell
cd d:\dev\price-tracker-IA\frontend
```

### 6.2 Installer les dépendances (si pas déjà fait)

```powershell
npm install
```

### 6.3 Démarrer le serveur de développement

```powershell
npm run dev
```

Le frontend sera accessible à : **http://localhost:5173**

---

## ✅ Vérification Complète

Vous devriez avoir **4 terminaux ouverts** :

| Terminal | Commande | URL |
|----------|----------|-----|
| 1️⃣ Backend FastAPI | `uvicorn app.main:app --reload` | http://localhost:8000 |
| 2️⃣ Celery Worker | `celery -A app.tasks.celery_app worker --pool=solo` | - |
| 3️⃣ Celery Beat | `celery -A app.tasks.celery_app beat` | - |
| 4️⃣ Frontend React | `npm run dev` | http://localhost:5173 |

### Test Rapide

1. **Backend** : Allez sur http://localhost:8000/docs → Vous devriez voir Swagger UI
2. **Frontend** : Allez sur http://localhost:5173 → Vous devriez voir la page d'accueil
3. **MySQL** : Dans HeidiSQL, vérifiez que les tables sont créées dans `price_tracker_db`
4. **Redis** : Le fait que Celery démarre confirme que Redis fonctionne

---

## 🧪 Tester le Scraping

### Test Jumia
```powershell
cd d:\dev\price-tracker-IA\backend
..\venv\Scripts\Activate.ps1
python test_scraper.py
```

---

## 🚨 Dépannage

### Problème : MySQL ne démarre pas dans Laragon
- Vérifiez qu'aucun autre MySQL n'est en cours (XAMPP, WAMP, etc.)
- Redémarrez Laragon

### Problème : Redis introuvable
Démarrez Redis manuellement :
```powershell
cd C:\laragon\bin\redis
.\redis-server.exe
```

### Problème : Port 8000 déjà utilisé
Changez le port du backend :
```powershell
uvicorn app.main:app --reload --port 8001
```

### Problème : Erreur de connexion à la base de données
- Vérifiez que MySQL est démarré dans Laragon
- Vérifiez le `.env` : le mot de passe est vide par défaut dans Laragon

---

## 📚 Prochaines Étapes

Une fois que tout fonctionne :

1. **Installer Ollama** (pour l'IA) : https://ollama.ai/download
   ```powershell
   ollama pull llama2
   ```

2. **Créer un compte de test KKiapay** : https://kkiapay.me

3. **Compléter le Frontend** :
   - Dashboard
   - Graphiques de prix
   - Gestion des alertes

4. **Tester les fonctionnalités** :
   - Inscription/Connexion
   - Ajouter un produit à suivre
   - Configurer une alerte

---

## 🎯 Commandes Utiles

### Arrêter tout
- **Backend** : `Ctrl+C` dans le terminal
- **Celery** : `Ctrl+C` dans les terminaux Celery
- **Frontend** : `Ctrl+C` dans le terminal frontend
- **Laragon** : Cliquez sur "Arrêter tout"

### Réinitialiser la base de données
```powershell
cd d:\dev\price-tracker-IA\backend
alembic downgrade base
alembic upgrade head
```

### Voir les logs Redis
```powershell
cd C:\laragon\bin\redis
.\redis-cli.exe
MONITOR
```
