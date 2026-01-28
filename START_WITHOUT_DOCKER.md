# 🚨 Guide de Démarrage Rapide Sans Docker

Docker n'est pas installé sur votre système. Voici comment démarrer sans Docker.

## Option 1: Installer Docker Desktop (Recommandé)

1. **Télécharger Docker Desktop**
   - Aller sur https://www.docker.com/products/docker-desktop
   - Télécharger pour Windows
   - Installer et redémarrer l'ordinateur

2. **Après installation**
   ```powershell
   docker --version
   docker compose version
   ```

3. **Puis lancer le projet**
   ```powershell
   cd d:\dev\price-tracker-IA
   docker compose up -d --build
   ```

---

## Option 2: Démarrage Manuel (Sans Docker)

### Prérequis à installer

1. **Python 3.11+**  
   https://www.python.org/downloads/

2. **MySQL 8.0**  
   https://dev.mysql.com/downloads/mysql/

3. **Redis** (via WSL ou Windows version)  
   WSL: `wsl --install` puis `sudo apt install redis-server`

4. **Node.js 18+**  
   https://nodejs.org/

---

### A. Configurer MySQL

```powershell
# Ouvrir MySQL Command Line ou Workbench
mysql -u root -p

# Créer la base
CREATE DATABASE price_tracker;
CREATE USER 'price_user'@'localhost' IDENTIFIED BY 'price_password';
GRANT ALL PRIVILEGES ON price_tracker.* TO 'price_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### B. Démarrer Redis

```powershell
# Via WSL
wsl
sudo service redis-server start
# Vérifier: redis-cli ping (doit retourner PONG)
```

### C. Configuration Backend

```powershell
cd d:\dev\price-tracker-IA\backend

# Créer environnement virtuel
python -m venv venv

# Activer
.\venv\Scripts\Activate.ps1

# Installer dépendances
pip install -r requirements.txt

# Installer Playwright browsers
playwright install chromium
playwright install-deps chromium
```

### D. Modifier .env

```powershell
notepad d:\dev\price-tracker-IA\.env
```

Changer ces lignes pour connexion locale:
```env
DATABASE_URL=mysql+aiomysql://price_user:price_password@localhost:3306/price_tracker
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### E. Créer les tables

```powershell
cd d:\dev\price-tracker-IA\backend

# S'assurer que venv est activé
.\venv\Scripts\Activate.ps1

# Migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### F. Démarrer Backend (3 terminaux)

**Terminal 1: API FastAPI**
```powershell
cd d:\dev\price-tracker-IA\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Celery Worker**
```powershell
cd d:\dev\price-tracker-IA\backend
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

**Terminal 3: Celery Beat** (optionnel - pour scraping auto)
```powershell
cd d:\dev\price-tracker-IA\backend
.\venv\Scripts\Activate.ps1
celery -A app.tasks.celery_app beat --loglevel=info
```

### G. Démarrer Frontend

**Terminal 4: Vite Dev Server**
```powershell
cd d:\dev\price-tracker-IA\frontend

# Installer dépendances (si pas déjà fait)
npm install

# Démarrer
npm run dev
```

---

## ✅ Vérification

Une fois tout démarré:

- **Frontend**: http://localhost:5173 (Homepage)
- **Backend API**: http://localhost:8000/docs (Swagger UI)
- **Backend Health**: http://localhost:8000/health

---

## 🎯 Test Rapide

1. Aller sur http://localhost:5173
2. Cliquer "Inscription"
3. Créer un compte:
   - Email: test@example.com
   - Téléphone: +22997123456
   - Nom: Test User
   - Mot de passe: password123
4. Se connecter
5. Aller sur http://localhost:8000/docs
6. Tester les endpoints API

---

## 🐛 Problèmes Courants

### Python venv ne s'active pas
```powershell
# Changer la politique d'exécution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### MySQL connection refused
```powershell
# Vérifier que MySQL tourne
Get-Service MySQL*
# ou
netstat -ano | findstr :3306
```

### Redis not found
```powershell
# Dans WSL
wsl
sudo service redis-server status
sudo service redis-server start
```

### Port 8000 déjà utilisé
```powershell
# Trouver le processus
netstat -ano | findstr :8000
# Tuer avec le PID
taskkill /F /PID <PID>
```

---

## 💡 Recommandation

**Docker Desktop est vraiment plus simple !** Tout est automatique:
- Pas besoin d'installer MySQL/Redis manuellement
- Un seul commande: `docker compose up -d`
- Isolation complète
- Facile à nettoyer

Installez Docker Desktop pour une meilleure expérience 😊
