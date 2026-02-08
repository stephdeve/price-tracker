# 🚀 Price Tracker - Guide de Démarrage

## 📦 Services Disponibles

Le projet inclut maintenant **15 services Docker** :

### Core Services
- **MySQL** - Base de données (port 3306)
- **Redis** - Cache & Celery broker (port 6379)
- **Backend** - API FastAPI (port 8000)
- **Celery Worker** - Traitement async
- **Celery Beat** - Planification
- **Frontend** - React app (port 5173)

### Monitoring Stack 📊
- **Prometheus** - Collecte métriques (port 9090)
- **Grafana** - Visualisation (port 3001)
- **Loki** - Agrégation logs (port 3100)
- **Promtail** - Collecteur logs
- **AlertManager** - Gestion alertes (port 9093)
- **Uptime Kuma** - Monitoring uptime (port 3002)

### Exporters
- **Node Exporter** - Métriques système (port 9100)
- **MySQL Exporter** - Métriques MySQL (port 9104)
- **Redis Exporter** - Métriques Redis (port 9121)
- **cAdvisor** - Métriques conteneurs (port 8080)

### Optional
- **Ollama** - IA locale (port 11434)

---

## 🚀 Démarrage Rapide

### 1. Configuration

```bash
cd /home/steven/dev/price-tracker
cp .env.example .env
```

**Éditer `.env` et configurer:**
```bash
# Base de données
MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=price_tracker
MYSQL_USER=price_user
MYSQL_PASSWORD=price_password

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin123

# Alertes (optionnel)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
ALERT_EMAIL=your_email@example.com
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
```

### 2. Démarrer TOUS les services

```bash
docker-compose up -d
```

### 3. Démarrer SEULEMENT les services essentiels

```bash
# Sans monitoring
docker-compose up -d mysql redis backend celery_worker celery_beat frontend
```

### 4. Initialiser la base de données

```bash
docker-compose exec backend alembic upgrade head
```

---

## 🌐 Accès aux Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | - |
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Grafana** | http://localhost:3001 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | - |
| **AlertManager** | http://localhost:9093 | - |
| **Uptime Kuma** | http://localhost:3002 | Setup on first visit |
| **cAdvisor** | http://localhost:8080 | - |

---

## 📊 Configuration Monitoring

### Grafana Dashboards

1. **Accéder à Grafana**: http://localhost:3001
2. **Login**: admin / admin123
3. **Datasources déjà configurées**:
   - Prometheus (métriques)
   - Loki (logs)
   - MySQL (données)
   - Redis

### Alertes Telegram

1. **Créer un bot Telegram**:
   - Parler à @BotFather
   - `/newbot` et suivre les instructions
   - Copier le token

2. **Obtenir votre Chat ID**:
   - Parler à @userinfobot
   - Copier votre ID

3. **Configurer dans `.env`**:
   ```bash
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_CHAT_ID=123456789
   ```

4. **Rebuild AlertManager**:
   ```bash
   docker-compose up -d alertmanager
   ```

### Types d'Alertes

- 🚨 **Critical**: Backend down, MySQL down, Redis down
- ⚠️ **Warning**: Erreurs >5%, Latence >2s, Disque <15%, RAM >90%
- 📊 **Info**: Métriques Celery, tâches en échec

---

## 🧪 Tests

### Test Scrapers

```bash
# AliExpress
docker-compose exec backend python test_aliexpress.py

# Jumia
docker-compose exec backend python test_scraper.py
```

### Test API

```bash
# Health check
curl http://localhost:8000/health

# Métriques Prometheus
curl http://localhost:8000/metrics
```

---

## 📈 Métriques Disponibles

### Backend
- `http_requests_total` - Total requêtes HTTP
- `http_request_duration_seconds` - Latence requêtes
- `scraping_requests_total` - Requêtes scraping
- `products_scraped_total` - Produits scrapés
- `price_alerts_sent_total` - Alertes envoyées

### Système
- `node_cpu_seconds_total` - CPU usage
- `node_memory_MemAvailable_bytes` - RAM disponible
- `node_filesystem_avail_bytes` - Disque disponible

### MySQL
- `mysql_up` - Status MySQL
- `mysql_global_status_connections` - Connexions
- `mysql_global_status_queries` - Requêtes

### Redis
- `redis_up` - Status Redis
- `redis_connected_clients` - Clients connectés
- `redis_memory_used_bytes` - Mémoire utilisée

---

## 🛠️ Commandes Utiles

### Logs
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f prometheus
```

### Restart
```bash
# Tout redémarrer
docker-compose restart

# Service spécifique
docker-compose restart backend
```

### Stop
```bash
# Arrêter tout
docker-compose down

# Arrêter et supprimer volumes
docker-compose down -v
```

### Rebuild
```bash
# Rebuild après changement de code
docker-compose up -d --build backend celery_worker celery_beat
```

---

## 🎯 Fonctionnalités

✅ **Multi-source scraping** - Jumia, Amazon, AliExpress  
✅ **Product matching** - 3 stages (exact, fuzzy, semantic)  
✅ **Price tracking** - Historique complet  
✅ **Alertes** - Telegram, Email, WhatsApp  
✅ **Monitoring complet** - Prometheus + Grafana  
✅ **Logs centralisés** - Loki + Promtail  
✅ **Alerting** - AlertManager avec notifications  
✅ **Uptime monitoring** - Uptime Kuma  
✅ **IA locale** - Ollama (optionnel)  

---

## 📝 Documentation

- [INTEGRATION.md](backend/INTEGRATION.md) - Guide d'intégration
- [Walkthrough](/.gemini/antigravity/brain/c1596428-440e-4581-a2b9-94029475e888/walkthrough.md) - Documentation complète

---

## 🐛 Dépannage

### Prometheus ne collecte pas de métriques

```bash
# Vérifier que le backend expose /metrics
curl http://localhost:8000/metrics

# Vérifier la config Prometheus
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# Restart Prometheus
docker-compose restart prometheus
```

### Grafana ne se connecte pas aux datasources

```bash
# Vérifier les datasources
docker-compose exec grafana cat /etc/grafana/provisioning/datasources/datasources.yml

# Restart Grafana
docker-compose restart grafana
```

### Alertes ne sont pas envoyées

```bash
# Vérifier AlertManager config
docker-compose exec alertmanager cat /etc/alertmanager/alertmanager.yml

# Vérifier les logs
docker-compose logs alertmanager

# Tester manuellement
curl -X POST http://localhost:9093/api/v1/alerts
```

---

## 🎉 Prêt !

Le système est maintenant **production-ready** avec monitoring complet ! 🚀
