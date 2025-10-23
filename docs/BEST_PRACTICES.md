# FastAPI Best Practices - SynchroBus API

Ce document regroupe les best practices pour le développement et la maintenance de cette API FastAPI.

## 🏗️ Structure du Projet

### Organisation des fichiers
```
src/
├── api/
│   ├── __init__.py
│   ├── dependencies.py      # Dépendances réutilisables
│   └── routers/             # Routers séparés par domaine
│       ├── __init__.py
│       ├── bus.py
│       ├── direction.py
│       └── bus_stop.py
├── core/
│   ├── __init__.py
│   ├── config.py            # Configuration centralisée
│   ├── logging.py           # Configuration logging
│   └── security.py          # Sécurité (CORS, rate limiting)
├── database/
│   ├── __init__.py
│   ├── Database.py
│   ├── Table.py
│   └── session.py           # Session management
├── models/
│   ├── __init__.py
│   └── schemas.py           # Modèles Pydantic
├── services/
│   ├── __init__.py
│   └── bus_service.py       # Logique métier
└── main.py                  # Point d'entrée
```

## 🔒 Sécurité

### 1. HTTPS/TLS
- **Production**: Toujours utiliser HTTPS
- Utiliser un reverse proxy (Nginx, Caddy, Traefik) pour gérer les certificats SSL
- Configuration Let's Encrypt pour les certificats gratuits

### 2. CORS (Cross-Origin Resource Sharing)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,  # Liste spécifique, jamais ["*"] en prod
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 3. Validation des entrées
- **Toujours** utiliser Pydantic pour la validation
- Valider les types, longueurs, formats (regex pour emails, etc.)
- Utiliser `constr`, `PositiveInt`, etc.

### 4. Protection contre les injections
- Utiliser SQLAlchemy avec des requêtes paramétrées
- **Jamais** de SQL brut avec interpolation de strings
- Sanitizer les entrées utilisateur

### 5. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/endpoint")
@limiter.limit("5/minute")
async def limited_endpoint():
    return {"message": "Rate limited endpoint"}
```

### 6. Security Headers
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# En production
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
```

## 📝 Logging

### Configuration structurée
```python
import logging
import sys
from logging.config import dictConfig

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "app": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}

dictConfig(log_config)
logger = logging.getLogger("app")
```

### Middleware de logging
```python
import time
import uuid
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        f"Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host,
        }
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Request completed",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s",
        }
    )
    
    response.headers["X-Request-ID"] = request_id
    return response
```

## 🗄️ Base de données

### 1. Session Management avec Context Manager
```python
from contextlib import contextmanager
from sqlalchemy.orm import Session

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utilisation dans les endpoints
@app.get("/items")
async def get_items():
    with get_db() as db:
        items = db.query(Item).all()
        return items
```

### 2. Dependency Injection FastAPI
```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items")
async def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

## 🧪 Tests

### 1. Structure des tests
```
tests/
├── __init__.py
├── conftest.py              # Fixtures pytest
├── test_api/
│   ├── test_bus.py
│   ├── test_direction.py
│   └── test_bus_stop.py
└── test_services/
    └── test_bus_service.py
```

### 2. Client de test async
```python
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_get_bus(client: AsyncClient):
    response = await client.get("/v1/bus")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 📦 Modèles Pydantic

### Séparation des modèles
```python
from pydantic import BaseModel, Field
from typing import Optional

# Modèle de base
class BusBase(BaseModel):
    id: str = Field(..., description="ID du bus")

# Modèle de création
class BusCreate(BusBase):
    pass

# Modèle de réponse
class BusResponse(BusBase):
    class Config:
        from_attributes = True  # Anciennement orm_mode
        
# Modèle pour les directions
class DirectionResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
```

## ⚡ Performance

### 1. Async vs Sync
- Utiliser `async def` pour les opérations I/O (DB, API externes)
- Utiliser `def` pour les opérations CPU-intensive (calculs)
- **NE JAMAIS** faire d'opérations bloquantes dans une route async

```python
# ❌ MAU VAIS
@app.get("/bad")
async def bad_route():
    time.sleep(10)  # Bloque tout l'event loop !
    return {"status": "bad"}

# ✅ BON (si sync I/O)
@app.get("/good")
def good_route():
    time.sleep(10)  # Bloqué mais dans un thread séparé
    return {"status": "good"}

# ✅ MEILLEUR (async I/O)
@app.get("/best")
async def best_route():
    await asyncio.sleep(10)  # Non-bloquant
    return {"status": "best"}
```

### 2. Connection Pooling
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DB_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Vérifie les connexions
)
```

## 🚀 Déploiement

### 1. Variables d'environnement
- **Jamais** de secrets en dur dans le code
- Utiliser `.env` en dev, secrets manager en prod
- Valider les variables au démarrage

### 2. Gunicorn + Uvicorn Workers
```bash
gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8080 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
```

### 3. Health checks
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    try:
        # Vérifier la connexion DB
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unavailable")
```

## 📋 Checklist avant Production

### Sécurité
- [ ] HTTPS activé
- [ ] CORS configuré avec origines spécifiques
- [ ] Rate limiting actif
- [ ] Security headers configurés
- [ ] Validation des entrées partout
- [ ] Pas de secrets en dur
- [ ] Dépendances à jour (`pip-audit`, `safety`)

### Code & Tests
- [ ] Tous les tests passent
- [ ] Couverture de tests > 80%
- [ ] Linter configuré (ruff, black)
- [ ] Pas d'endpoints de debug en prod
- [ ] Documentation API à jour

### Performance
- [ ] Connection pooling configuré
- [ ] Async/sync bien utilisé
- [ ] Caching si nécessaire (Redis)

### Monitoring
- [ ] Logging configuré
- [ ] Métriques (Prometheus)
- [ ] Alertes configurées
- [ ] Health checks implémentés

### Déploiement
- [ ] Docker image optimisée
- [ ] CI/CD pipeline testé
- [ ] Backups DB configurés
- [ ] Plan de rollback défini

## 🛠️ Outils recommandés

### Développement
- **Linter**: `ruff` (remplace black, isort, flake8)
- **Tests**: `pytest`, `httpx`, `pytest-asyncio`
- **DB**: SQLAlchemy ORM, Alembic pour migrations
- **Validation**: Pydantic

### Production
- **Serveur**: Gunicorn + Uvicorn workers
- **Reverse proxy**: Nginx, Caddy, Traefik
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK stack ou Better Stack
- **Errors**: Sentry

### Sécurité
- **Scan vulnérabilités**: `pip-audit`, `safety`, `bandit`
- **Rate limiting**: `slowapi`
- **Password hashing**: `passlib` avec `bcrypt`

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Best Practices GitHub](https://github.com/zhanymkanov/fastapi-best-practices)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
