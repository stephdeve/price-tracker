# 🚀 Quick Start Guide - Price Tracker Bénin

## Option 1: Démarrage rapide avec Docker (Recommandé)

### 1. Vérifier les prérequis
```powershell
# Vérifier Docker
docker --version
docker-compose --version

# Si Docker n'est pas installé, téléchargez Docker Desktop pour Windows
# https://www.docker.com/products/docker-desktop
```

### 2. Configurer l'environnement
```powershell
cd d:\dev\price-tracker-IA

# Le fichier .env a déjà été créé, vous pouvez le modifier:
notepad .env

# Valeurs minimales requises pour commencer:
# - Les valeurs MySQL sont déjà configurées
# - JWT_SECRET_KEY: changez-le pour plus de sécurité
# - Le reste peut attendre pour les tests initiaux
```

### 3. Démarrer les services
```powershell
# Construire et démarrer tous les containers
docker-compose up -d --build

# Attendre 30 secondes que MySQL démarre complètement
Start-Sleep -Seconds 30

# Vérifier que les services tournent
docker-compose ps
```

Vous devriez voir :
- ✅ `price_tracker_mysql` - Running
- ✅ `price_tracker_redis` - Running  
- ✅ `price_tracker_backend` - Running
- ✅ `price_tracker_celery_worker` - Running
- ✅ `price_tracker_celery_beat` - Running

### 4. Créer la base de données
```powershell
# Entrer dans le container backend
docker-compose exec backend bash

# À l'intérieur du container:
# Générer la migration initiale
alembic revision --autogenerate -m "Initial migration"

# Appliquer les migrations
alembic upgrade head

# Sortir du container
exit
```

### 5. Tester l'API
```powershell
# Ouvrir votre navigateur à:
# http://localhost:8000
# http://localhost:8000/docs (Swagger UI)
```

---

## Option 2: Développement local (sans Docker)

### 1. Installer MySQL
```powershell
# Télécharger MySQL 8.0 pour Windows
# https://dev.mysql.com/downloads/mysql/

# Créer la base de données
mysql -u root -p
CREATE DATABASE price_tracker;
CREATE USER 'price_user'@'localhost' IDENTIFIED BY 'price_password';
GRANT ALL PRIVILEGES ON price_tracker.* TO 'price_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2. Installer Redis
```powershell
# Option 1: Via WSL2 (recommandé)
wsl --install
wsl
sudo apt update
sudo apt install redis-server
sudo service redis-server start

# Option 2: Redis for Windows (moins stable)
# https://github.com/microsoftarchive/redis/releases
```

### 3. Configuration Python
```powershell
cd d:\dev\price-tracker-IA\backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Installer Playwright browsers
playwright install chromium
```

### 4. Configurer .env (local)
```powershell
# Modifier .env pour connexion locale
notepad .env
```

Changez ces lignes:
```env
DATABASE_URL=mysql+aiomysql://price_user:price_password@localhost:3306/price_tracker
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
```

### 5. Lancer l'application
```powershell
# Terminal 1: Backend FastAPI
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery Worker
cd backend
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo

# Terminal 3: Celery Beat
cd backend
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## 🧪 Tester le Scraping (Jumia Bénin)

### Méthode 1: Via Python directement
```powershell
# Entrer dans le container (si Docker)
docker-compose exec backend python

# Ou activer venv (si local)
# .\backend\venv\Scripts\Activate.ps1
# cd backend
# python
```

```python
import asyncio
from app.services.scraper.jumia_scraper import JumiaScraper

async def test_scraping():
    # Remplacez par une vraie URL de produit Jumia Bénin
    url = "https://www.jumia.com.bj/..."  # Ex: Un téléphone populaire
    
    async with JumiaScraper() as scraper:
        print("🔍 Scraping en cours...")
        data = await scraper.scrape_product(url)
        
        if data:
            print(f"✅ Produit: {data['name']}")
            print(f"💰 Prix: {data['price']} {data['currency']}")
            print(f"📸 Image: {data['image_url'][:50]}...")
        else:
            print("❌ Échec du scraping")

# Lancer le test
asyncio.run(test_scraping())
```

### Méthode 2: Via un script de test
Créez `backend/test_scraper.py`:
```python
import asyncio
from app.services.scraper.jumia_scraper import JumiaScraper

async def main():
    # Liste de produits Jumia Bénin à tester
    test_urls = [
        "https://www.jumia.com.bj/...",  # Ajoutez des URLs réelles
    ]
    
    async with JumiaScraper() as scraper:
        for url in test_urls:
            print(f"\n{'='*60}")
            print(f"Testing: {url}")
            print('='*60)
            
            data = await scraper.scrape_product(url)
            
            if data:
                for key, value in data.items():
                    print(f"{key}: {value}")
            else:
                print("FAILED")

if __name__ == "__main__":
    asyncio.run(main())
```

Puis lancez:
```powershell
docker-compose exec backend python test_scraper.py
# Ou si local: python backend/test_scraper.py
```

---

## 📱 Installer Ollama (IA Gratuite)

### Windows
```powershell
# 1. Télécharger Ollama depuis https://ollama.ai
# 2. Installer l'application
# 3. Ouvrir PowerShell et lancer:

ollama pull llama3.2

# Vérifier que ça fonctionne
ollama run llama3.2 "Bonjour, parle-moi du Bénin"

# Ollama sera accessible sur http://localhost:11434
```

### Linux / WSL
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2
```

---

## 🔧 Commandes Utiles

### Docker
```powershell
# Voir les logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Redémarrer un service
docker-compose restart backend

# Arrêter tout
docker-compose down

# Nettoyer et reconstruire
docker-compose down -v
docker-compose up -d --build
```

### Base de données
```powershell
# Accéder à MySQL
docker-compose exec mysql mysql -u price_user -pprice_password price_tracker

# Voir les tables
SHOW TABLES;

# Voir les utilisateurs
SELECT * FROM users;
```

### Alembic (Migrations)
```powershell
# Créer une nouvelle migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Appliquer les migrations
docker-compose exec backend alembic upgrade head

# Revenir en arrière
docker-compose exec backend alembic downgrade -1

# Voir l'historique
docker-compose exec backend alembic history
```

---

## ✅ Vérification de l'installation

### Checklist
- [ ] Docker Desktop installé et en cours d'exécution
- [ ] `docker-compose ps` montre tous les services "Up"
- [ ] http://localhost:8000 affiche le message de bienvenue
- [ ] http://localhost:8000/docs affiche Swagger UI
- [ ] Alembic migrations appliquées (tables créées dans MySQL)
- [ ] Ollama installé et modèle llama3.2 téléchargé
- [ ] Test de scraping Jumia réussi

### Problèmes courants

**Port 3306 déjà utilisé (MySQL)**
```powershell
# Trouver le processus
netstat -ano | findstr :3306
# Arrêter le service MySQL existant ou changer le port dans docker-compose.yml
```

**Port 6379 déjà utilisé (Redis)**
```powershell
# Même procédure
netstat -ano | findstr :6379
```

**Playwright ne fonctionne pas**
```powershell
# Réinstaller les browsers
docker-compose exec backend playwright install chromium
docker-compose exec backend playwright install-deps chromium
```

---

## 🎯 Prochaines étapes

1. ✅ Infrastructure ready
2. ✅ Database models créés
3. ✅ Scraping Jumia fonctionnel
4. **SUIVANT**: Créer les endpoints API (auth, products)
5. **PUIS**: Frontend React
6. **ENFIN**: Intégration KKiapay  

---

Need help? Les logs sont votre ami! 📋
```powershell
docker-compose logs -f
```
