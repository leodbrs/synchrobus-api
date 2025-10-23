# Architecture - SynchroBus API

## Vue d'ensemble

SynchroBus API est une API REST construite avec FastAPI qui fournit des informations sur les lignes de bus de Chambéry. L'API suit les principes de clean architecture et les best practices FastAPI 2024.

## Stack Technique

### Backend
- **Framework**: FastAPI 0.119+
- **Runtime**: Python 3.11
- **Server**: Uvicorn (ASGI)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2

### Database
- **Type**: SQLite (development)
- **Location**: `database/db.sqlite`
- **Migrations**: Alembic dans `database/alembic/`

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **OS**: Alpine Linux (image de base)
- **Reverse Proxy**: Non configuré (à ajouter en production)

### Testing
- **Integration Tests**: Bruno CLI
- **Test Location**: `bruno/`
- **Coverage**: 11 endpoints, 29 tests

## Structure du Projet

```
synchrobus-api/
├── src/                        # Code source
│   ├── api/                    # Couche API
│   │   ├── dependencies.py     # Dépendances FastAPI (DI)
│   │   └── routers/            # Routers par domaine
│   │       ├── bus.py          # Routes /v1/bus/*
│   │       ├── direction.py    # Routes /v1/direction/*
│   │       ├── bus_stop.py     # Routes /v1/bus_stop/*
│   │       └── apple_shortcuts.py  # Routes /v1/appleshortcuts/*
│   │
│   ├── core/                   # Configuration centrale
│   │   ├── config.py           # Variables d'environnement
│   │   ├── logging_config.py   # Configuration logging
│   │   └── middleware.py       # Middlewares (logging, CORS)
│   │
│   ├── database/               # Couche données
│   │   ├── Database.py         # Session factory
│   │   ├── Table.py            # Modèles SQLAlchemy
│   │   └── alembic/            # Migrations
│   │
│   ├── models/                 # Schémas de validation
│   │   └── schemas.py          # Modèles Pydantic
│   │
│   ├── services/               # Logique métier (à développer)
│   │
│   ├── InitDb.py               # Script d'initialisation DB
│   ├── main.py                 # Point d'entrée FastAPI
│   └── config.py               # Backward compatibility
│
├── bruno/                      # Tests d'intégration
│   ├── bruno.json              # Configuration collection
│   ├── environments/           # Environnements de test
│   └── *.bru                   # Fichiers de test
│
├── .cursor/                    # Configuration Cursor AI
│   └── rules/                  # Règles par contexte
│
├── .env.example                # Template variables d'env
├── .gitignore                  # Fichiers ignorés
├── compose.yml                 # Configuration Docker Compose
├── Dockerfile                  # Image Docker
├── requirements.txt            # Dépendances Python
├── AGENTS.md                   # Instructions pour IA
├── BEST_PRACTICES.md           # Guide des best practices
├── ARCHITECTURE.md             # Ce fichier
└── README.md                   # Documentation utilisateur

```

## Architecture en Couches

### 1. API Layer (`src/api/`)
**Responsabilité**: Gestion des requêtes HTTP et routing

- **Routers**: Séparation par domaine métier
  - `bus.py`: Gestion des lignes de bus
  - `direction.py`: Gestion des directions
  - `bus_stop.py`: Gestion des arrêts (+ scraping live)
  - `apple_shortcuts.py`: Format spécifique pour iOS

- **Dependencies**: Injection de dépendances
  - `get_db()`: Fournit une session DB via FastAPI DI
  - Fermeture automatique des sessions (try/finally)

- **Validation**: Automatique via Pydantic
  - Query params validés
  - Response models garantis
  - Erreurs 422 auto-générées

### 2. Core Layer (`src/core/`)
**Responsabilité**: Configuration et cross-cutting concerns

- **config.py**: Configuration centralisée
  - Variables d'environnement (.env)
  - Valeurs par défaut
  - Validation au démarrage

- **logging_config.py**: Logging structuré
  - Format uniforme
  - Niveaux configurables
  - Intégration Uvicorn

- **middleware.py**: Middlewares transversaux
  - `LoggingMiddleware`: Log toutes les requêtes
  - `setup_cors()`: Configuration CORS
  - Headers personnalisés (X-Request-ID, X-Process-Time)

### 3. Database Layer (`src/database/`)
**Responsabilité**: Accès aux données

- **Table.py**: Modèles SQLAlchemy ORM
  ```python
  Bus, Direction, BusStop
  BusDirection, BusStopDirection, BusStopBus
  ```

- **Database.py**: Session factory
  - Configuration SQLite
  - Création de sessions

- **Alembic**: Migrations de schéma
  - Versionnage du schéma
  - Migrations auto-générées
  - Rollback possible

### 4. Models Layer (`src/models/`)
**Responsabilité**: Validation et sérialisation

- **schemas.py**: Modèles Pydantic v2
  - Request validation
  - Response serialization
  - Documentation OpenAPI
  - Type safety

### 5. Services Layer (`src/services/`)
**Responsabilité**: Logique métier (à développer)

- Actuellement vide
- Futur: extraction de la logique complexe
- Pattern: Service classes
- Testabilité améliorée

## Flux de Données

### Requête Entrante

```
1. Client HTTP
   ↓
2. Uvicorn (ASGI Server)
   ↓
3. FastAPI Application
   ↓
4. CORS Middleware
   ↓
5. Logging Middleware (début)
   ↓
6. Router (bus/direction/bus_stop/apple_shortcuts)
   ↓
7. Pydantic Validation (query params)
   ↓
8. Dependency Injection (get_db)
   ↓
9. Handler Function
   ↓
10. SQLAlchemy Query
    ↓
11. SQLite Database
    ↓
12. Résultat → Pydantic Model
    ↓
13. JSON Serialization
    ↓
14. Logging Middleware (fin)
    ↓
15. Response HTTP
```

### Requête Live Bus Stop

```
1. GET /v1/bus_stop/live/{bus_stop_id}
   ↓
2. Handler: get_bus_stop_live_info()
   ↓
3. HTTP Request → https://live.synchro-bus.fr/{id}
   ↓
4. BeautifulSoup Parsing
   ↓
5. Data Extraction (line, direction, time, remaining)
   ↓
6. Pydantic Validation (BusLiveInfoResponse)
   ↓
7. JSON Response
```

## Schéma de Base de Données

### Tables Principales

**bus**
- `id` (PK): Identifiant ligne (A, B, C, D)

**direction**
- `id` (PK): ID direction
- `name`: Nom de la direction

**bus_stop**
- `id` (PK): Identifiant arrêt (ex: GAMBE1)
- `name`: Nom de l'arrêt

### Tables de Relation (Many-to-Many)

**bus_direction**
- `bus_id` (FK → bus.id)
- `direction_id` (FK → direction.id)

**bus_stop_direction**
- `bus_stop_id` (FK → bus_stop.id)
- `direction_id` (FK → direction.id)

**bus_stop_bus**
- `bus_stop_id` (FK → bus_stop.id)
- `bus_id` (FK → bus.id)

### Relations

```
Bus ←→ Direction (Many-to-Many via bus_direction)
BusStop ←→ Direction (Many-to-Many via bus_stop_direction)
BusStop ←→ Bus (Many-to-Many via bus_stop_bus)
```

## Patterns de Design

### 1. Dependency Injection
```python
# api/dependencies.py
def get_db() -> Generator[Session, None, None]:
    db = APIDatabase(config.DB_URL)
    try:
        yield db
    finally:
        db.close()

# Utilisation dans les routers
@router.get("/")
async def endpoint(db: Session = Depends(get_db)):
    # db est automatiquement injecté et fermé
    return db.query(Model).all()
```

### 2. Repository Pattern (Implicite via SQLAlchemy)
```python
# Queries encapsulées dans les routers
query = select(Bus.id).where(
    Bus.id.in_(
        select(BusDirection.bus_id).where(
            BusDirection.direction_id == direction_id
        )
    )
)
```

### 3. Response Model Pattern
```python
@router.get("/", response_model=list[BusStopResponse])
async def get_all_bus_stops(db: Session = Depends(get_db)):
    # FastAPI valide automatiquement la réponse
    return [{"id": "GAMBE1", "name": "Gambetta"}]
```

### 4. Middleware Pattern
```python
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Pre-processing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Post-processing
        process_time = time.time() - start_time
        logger.info(f"Request took {process_time:.4f}s")
        
        return response
```

## Configuration

### Variables d'Environnement

```bash
# Database
DB_URL=sqlite:///./database/db.sqlite

# API
HOST=0.0.0.0
PORT=8080
RELOAD=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8051

# Logging
LOG_LEVEL=INFO
```

### Configuration Docker

- **Multi-stage build**: Optimisation de la taille de l'image
- **Virtual environment**: Isolation des dépendances
- **Volume watch**: Hot reload en développement
- **Alpine Linux**: Image légère

## Sécurité

### Implémenté
- ✅ CORS configuré
- ✅ Validation des entrées (Pydantic)
- ✅ Requêtes SQL paramétrées (SQLAlchemy)
- ✅ Headers de sécurité basiques

### À Implémenter
- ⏳ Rate limiting
- ⏳ Authentication/Authorization
- ⏳ HTTPS en production
- ⏳ Input sanitization renforcée
- ⏳ Security headers (HSTS, CSP, etc.)

## Performance

### Optimisations Actuelles
- Async handlers (FastAPI)
- Connection pooling (SQLAlchemy)
- Alpine Linux (image légère)
- Requêtes SQL optimisées

### Métriques
- **Temps de réponse moyen**: 3-50ms (endpoints DB)
- **Temps de réponse live**: 700-900ms (scraping externe)
- **Taille de l'image Docker**: ~150MB

### Améliorations Possibles
- Redis caching pour les données statiques
- Compression des réponses (gzip)
- CDN pour les assets statiques (si applicable)
- Connection pooling DB optimisé
- Query optimization (indexes)

## Monitoring & Observability

### Logs
- Format structuré
- Request ID unique
- Temps de traitement
- Status codes
- Client IP

### Métriques (À Implémenter)
- Prometheus metrics endpoint
- Request rate
- Error rate
- Response time percentiles
- DB query time

### Tracing (À Implémenter)
- OpenTelemetry integration
- Distributed tracing
- Span correlation

## Tests

### Tests d'Intégration (Bruno)
- **Location**: `bruno/`
- **Endpoints testés**: 11/11 (100%)
- **Tests**: 29 tests
- **Environnements**: local

### Tests Unitaires (À Implémenter)
- pytest
- pytest-asyncio
- httpx pour client async
- Coverage target: 80%+

## Déploiement

### Development
```bash
docker compose up -d
# Watch mode actif automatiquement
```

### Production (Recommandations)
- Gunicorn + Uvicorn workers
- Reverse proxy (Nginx/Traefik)
- PostgreSQL au lieu de SQLite
- Environment variables via secrets
- Health checks configurés
- Auto-scaling si nécessaire

## Évolution Future

### Court Terme
- [ ] Rate limiting (slowapi)
- [ ] Caching (Redis)
- [ ] Tests unitaires (pytest)
- [ ] CI/CD pipeline

### Moyen Terme
- [ ] Authentication (JWT)
- [ ] PostgreSQL migration
- [ ] Prometheus metrics
- [ ] API versioning v2

### Long Terme
- [ ] WebSocket pour live updates
- [ ] GraphQL endpoint
- [ ] Service mesh (si microservices)
- [ ] Multi-region deployment

## Contribution

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines de développement.

## License

Voir [README.md](README.md) pour les informations de license.
