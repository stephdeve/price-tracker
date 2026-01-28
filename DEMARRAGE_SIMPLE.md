# 🎯 Démarrage Simplifié - Frontend Uniquement

## Situation Actuelle

✅ **Installé:**
- Python 3.11+
- Node.js v22.14.0

❌ **Manquant:**
- MySQL
- Redis

## Solution : Mode Démo Frontend

Vous pouvez démarrer le frontend en mode démo pour voir l'interface utilisateur !

### Étape 1: Installer les dépendances frontend

```powershell
cd d:\dev\price-tracker-IA\frontend
npm install
```

### Étape 2: Démarrer le frontend

```powershell
npm run dev
```

### Étape 3: Ouvrir dans le navigateur

http://localhost:5173

## Ce qui fonctionnera :

✅ Homepage (design complet)
✅ Page de tarifs
✅ Formulaires d'inscription/connexion (UI seulement)
❌ API calls (pas de backend)

---

## Pour avoir le backend complet:

### Option A: Installer MySQL + Redis (30 min)

**1. MySQL:**
- Télécharger: https://dev.mysql.com/downloads/installer/
- Installer MySQL Server 8.0
- Configurer utilisateur/mot de passe

**2. Redis via WSL:**
```powershell
# Installer WSL
wsl --install

# Redémarrer l'ordinateur

# Installer Redis
wsl
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**3. Configuration Backend:**
```powershell
# Fixer ExecutionPolicy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Créer venv
cd d:\dev\price-tracker-IA\backend
python -m venv venv

# Activer
.\venv\Scripts\Activate.ps1

# Installer
pip install -r requirements.txt

# Migrations
alembic revision --autogenerate -m "Initial"
alembic upgrade head

# Lancer API
uvicorn app.main:app --reload
```

### Option B: Installer Docker Desktop (10 min) ⭐ RECOMMANDÉ

1. Télécharger https://www.docker.com/products/docker-desktop
2. Installer, redémarrer
3. Lancer:
```powershell
cd d:\dev\price-tracker-IA
docker compose up -d
```

Tout fonctionne automatiquement ! 🎉

---

## Commandes Actuelles

Pour l'instant, démarrons le frontend:

```powershell
cd d:\dev\price-tracker-IA\frontend

# Si npm install pas fini
npm install

# Démarrer
npm run dev
```

Vous verrez une belle interface même sans backend !
