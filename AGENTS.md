# 🤖 SynchroBus API - Guide pour Agents IA

> **Note**: Ce fichier fournit tout le contexte nécessaire pour les agents IA (Cursor Agent CLI, GitHub Copilot, etc.)  
> **Objectif**: Permettre aux IA de coder efficacement sur ce projet sans assistance humaine

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Stack Technique](#stack-technique)
3. [Architecture](#architecture)
4. [Patterns de Code](#patterns-de-code)
5. [Workflows Communs](#workflows-communs)
6. [Règles Importantes](#règles-importantes)
7. [Documentation Détaillée](#documentation-détaillée)

---

## Vue d'Ensemble

### Projet
- **Nom**: SynchroBus API
- **Type**: API REST
- **Framework**: FastAPI (Python 3.11)
- **Objectif**: API non-officielle pour les données de bus de Chambéry
- **Status**: Développement actif
- **Branch actuelle**: `learning-vibe-coding`

### Fonctionnalités
- 🚍 Données statiques (bus, directions, arrêts)
- ⏱️ Horaires en temps réel (web scraping)
- 📱 Endpoints compatibles Apple Shortcuts
- 📊 Documentation OpenAPI auto-générée
- ✅ Tests d'intégration avec Bruno (29/29)

### Commandes Essentielles

```bash
# Développement
docker compose up -d              # Démarrer (watch mode actif)
docker compose logs -f            # Logs en temps réel
docker compose down               # Arrêter

# Tests
cd bruno && bru run --env local . # Tous les tests (29/29)

# Database
docker exec synchrobus-api-web-1 alembic revision --autogenerate -m "description"
docker exec synchrobus-api-web-1 alembic upgrade head
docker exec synchrobus-api-web-1 alembic downgrade -1

# Debug
curl http://localhost:8051/health          # Health check
curl http://localhost:8051/v1/bus          # Test endpoint
open http://localhost:8051/docs            # Swagger UI
```

---

## Stack Technique

| Composant | Technologie | Version | Notes |
|-----------|-------------|---------|-------|
| Framework | FastAPI | 0.119+ | ASGI, async support |
| Python | CPython | 3.11 | Type hints obligatoires |
| Database | SQLite | Latest | PostgreSQL en prod |
| ORM | SQLAlchemy | 2.0 | Utiliser `select()` syntax |
| Validation | Pydantic | v2 | `ConfigDict` pas `Config` |
| Migrations | Alembic | Latest | Auto-generate + review |
| Server | Uvicorn | Latest | ASGI server |
| Container | Docker | Latest | Alpine Linux base |
| Tests | Bruno CLI | Latest | Integration tests |

---

## Architecture

### Structure des Dossiers

```
synchrobus-api/
├── src/                        # Code source
│   ├── api/                    # Couche API
│   │   ├── dependencies.py     # Dependency injection
│   │   └── routers/            # Routes par domaine
│   │       ├── bus.py          # GET /v1/bus/*
│   │       ├── direction.py    # GET /v1/direction/*
│   │       ├── bus_stop.py     # GET /v1/bus_stop/*
│   │       └── apple_shortcuts.py  # GET /v1/appleshortcuts/*
│   │
│   ├── core/                   # Configuration
│   │   ├── config.py           # Variables d'environnement
│   │   ├── logging_config.py   # Logging structuré
│   │   └── middleware.py       # CORS + logging middleware
│   │
│   ├── database/               # Données
│   │   ├── Database.py         # Session factory
│   │   ├── Table.py            # Modèles SQLAlchemy
│   │   └── alembic/            # Migrations DB
│   │
│   ├── models/                 # Validation
│   │   └── schemas.py          # Schémas Pydantic v2
│   │
│   ├── services/               # Logique métier (vide pour l'instant)
│   ├── InitDb.py               # Script init DB
│   ├── main.py                 # FastAPI app
│   └── config.py               # Backward compatibility
│
├── bruno/                      # Tests d'intégration
├── docs/                       # Documentation technique
├── .cursor/rules/              # Règles Cursor par contexte
├── .env.example                # Template config
├── compose.yml                 # Docker Compose
├── Dockerfile                  # Multi-stage build
├── requirements.txt            # Dépendances Python
├── AGENTS.md                   # Ce fichier
└── README.md                   # Doc utilisateur
```

### Schéma de Base de Données

**Tables principales** :
```sql
bus (id TEXT PK)                    -- Lignes: A, B, C, D
direction (id INTEGER PK, name TEXT)
bus_stop (id TEXT PK, name TEXT)    -- Ex: GAMBE1, GARE1
```

**Relations Many-to-Many** :
```sql
bus_direction (bus_id FK, direction_id FK)
bus_stop_direction (bus_stop_id FK, direction_id FK)
bus_stop_bus (bus_stop_id FK, bus_id FK)
```

### Flux de Requête

```
Client → Uvicorn → FastAPI → CORS Middleware → Logging Middleware
  → Router → Pydantic Validation → get_db() DI → Handler
  → SQLAlchemy Query → SQLite → Pydantic Response → JSON
```

---

## Patterns de Code

### 1. Structure d'un Router

```python
# src/api/routers/domain.py
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db
from database.Table import Model, RelatedModel
from models.schemas import ResponseModel
from core.logging_config import logger

router = APIRouter(prefix="/v1/domain", tags=["domain"])


@router.get("/", response_model=list[ResponseModel])
async def get_all_items(db: Session = Depends(get_db)):
    """
    Get all items.
    
    Returns:
        list[ResponseModel]: List of all items
    """
    logger.info("GET /v1/domain - Fetching all items")
    res = db.execute(select(Model.id, Model.name)).fetchall()
    return [{"id": item[0], "name": item[1]} for item in res]


@router.get("/by-param", response_model=list[ResponseModel])
async def get_items_by_param(
    param_id: Union[int, None] = Query(None, description="Parameter ID"),
    db: Session = Depends(get_db)
):
    """
    Get items filtered by parameter.
    
    Args:
        param_id: The parameter ID to filter by
        
    Returns:
        list[ResponseModel]: Filtered items
        
    Raises:
        HTTPException: 400 if param_id is not provided
    """
    if not param_id:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier un paramètre"
        )
    
    logger.info(f"GET /v1/domain/by-param?param_id={param_id}")
    
    query = select(Model.id, Model.name).where(
        Model.id.in_(
            select(RelatedModel.model_id).where(
                RelatedModel.param_id == param_id
            )
        )
    )
    res = db.execute(query).fetchall()
    return [{"id": item[0], "name": item[1]} for item in res]
```

### 2. Schémas Pydantic v2

```python
# src/models/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ItemBase(BaseModel):
    """Base schema for items."""
    name: str = Field(..., min_length=1, max_length=100, description="Item name")


class ItemCreate(ItemBase):
    """Schema for creating an item."""
    id: str = Field(..., description="Unique identifier")


class ItemResponse(ItemBase):
    """Schema for item response."""
    id: str
    
    # Pydantic v2 syntax (NOT orm_mode!)
    model_config = ConfigDict(from_attributes=True)


class ItemListResponse(BaseModel):
    """Schema for paginated item list."""
    items: list[ItemResponse]
    total: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [{"id": "A", "name": "Line A"}],
                "total": 1
            }
        }
    )
```

### 3. Dependency Injection pour DB

```python
# src/api/dependencies.py
from typing import Generator
from sqlalchemy.orm import Session
import config
from database.Database import APIDatabase


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database session.
    
    Automatically closes session after request.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = APIDatabase(config.DB_URL)
    try:
        yield db
    finally:
        db.close()


# Utilisation dans les routers
@router.get("/endpoint")
async def handler(db: Session = Depends(get_db)):
    # db est injecté et fermé automatiquement
    return db.query(Model).all()
```

### 4. Gestion des Erreurs

```python
from fastapi import HTTPException
from core.logging_config import logger


@router.get("/endpoint/{item_id}")
async def get_item(item_id: str, db: Session = Depends(get_db)):
    """Get a specific item."""
    
    # Validation input
    if not item_id:
        raise HTTPException(
            status_code=400,
            detail="ID de l'item requis"
        )
    
    # Query
    item = db.query(Model).filter(Model.id == item_id).first()
    
    # Not found
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Item {item_id} non trouvé"
        )
    
    # Success
    return {"id": item.id, "name": item.name}


@router.post("/endpoint")
async def create_item(data: ItemCreate):
    """Create new item."""
    try:
        # Logic
        result = process(data)
        return result
    except ValueError as e:
        # Expected error
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error creating item: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la création de l'item"
        )
```

### 5. Queries SQLAlchemy

```python
from sqlalchemy import select

# ✅ GOOD - Parameterized queries
query = select(Bus.id).where(Bus.id == bus_id)

# ✅ GOOD - Subqueries
query = select(Direction.id, Direction.name).where(
    Direction.id.in_(
        select(BusDirection.direction_id).where(
            BusDirection.bus_id == bus_id
        )
    )
)

# ✅ GOOD - Multiple conditions
query = select(BusStop).where(
    BusStop.name.like(f"%{search}%"),
    BusStop.active == True
)

# ❌ BAD - SQL injection risk!
query = f"SELECT * FROM bus WHERE id = '{bus_id}'"

# ❌ BAD - Don't use raw SQL
db.execute(f"SELECT * FROM {table} WHERE id = {id}")
```

---

## Workflows Communs

### Ajouter un Nouveau Endpoint

**Checklist** :
1. [ ] Identifier le domaine (bus/direction/bus_stop/apple_shortcuts)
2. [ ] Créer/mettre à jour le schéma Pydantic dans `models/schemas.py`
3. [ ] Ajouter la route dans `api/routers/{domain}.py`
4. [ ] Ajouter docstring avec description, args, returns, raises
5. [ ] Implémenter la logique avec `get_db()` DI
6. [ ] Gérer les erreurs (validation, not found, etc.)
7. [ ] Ajouter logs (`logger.info()`)
8. [ ] Créer un test Bruno dans `bruno/`
9. [ ] Tester : `bru run --env local bruno/`
10. [ ] Vérifier les logs : `docker compose logs -f`

**Exemple complet** :

```python
# 1. Modèle Pydantic (models/schemas.py)
class NewItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# 2. Route (api/routers/domain.py)
@router.get("/new-endpoint/{item_id}", response_model=NewItemResponse)
async def get_new_item(
    item_id: int = Path(..., description="Item ID"),
    db: Session = Depends(get_db)
):
    """
    Get a specific item by ID.
    
    Args:
        item_id: Unique identifier of the item
        
    Returns:
        NewItemResponse: Item details
        
    Raises:
        HTTPException: 404 if item not found
    """
    logger.info(f"GET /v1/domain/new-endpoint/{item_id}")
    
    query = select(Model).where(Model.id == item_id)
    result = db.execute(query).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    
    return result[0]


# 3. Test Bruno (bruno/Get New Item.bru)
meta {
  name: Get New Item
  type: http
  seq: 12
}

get {
  url: {{baseUrl}}/v1/domain/new-endpoint/1
  body: none
  auth: none
}

tests {
  test("Status code is 200", function() {
    expect(res.status).to.equal(200);
  });
  
  test("Response has correct structure", function() {
    expect(res.body).to.have.property('id');
    expect(res.body).to.have.property('name');
  });
}
```

### Modifier le Schéma de Base de Données

**Workflow** :
1. [ ] Modifier `database/Table.py` (ajouter/modifier modèle)
2. [ ] Générer migration : `alembic revision --autogenerate -m "add field"`
3. [ ] **IMPORTANT** : Reviewer le fichier de migration généré
4. [ ] Appliquer : `alembic upgrade head`
5. [ ] Mettre à jour schémas Pydantic si nécessaire
6. [ ] Mettre à jour routes si nécessaire
7. [ ] Tester manuellement
8. [ ] Mettre à jour tests Bruno
9. [ ] Commit migration + code

**Exemple** :

```python
# 1. Modifier Table.py
class BusStop(Base):
    __tablename__ = "bus_stop"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)  # ← Nouveau champ
    longitude = Column(Float, nullable=True)  # ← Nouveau champ

# 2. Migration
docker exec synchrobus-api-web-1 alembic revision --autogenerate -m "add coordinates to bus_stop"

# 3. Review
# Vérifier le fichier généré dans database/alembic/versions/

# 4. Apply
docker exec synchrobus-api-web-1 alembic upgrade head

# 5. Mettre à jour Pydantic
class BusStopResponse(BaseModel):
    id: str
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
```

---

## Règles Importantes

### ✅ À TOUJOURS Faire

1. **Type hints partout**
   ```python
   def function(param: str) -> dict[str, int]:
       pass
   ```

2. **Dependency injection pour DB**
   ```python
   async def handler(db: Session = Depends(get_db)):
       pass
   ```

3. **Pydantic v2 syntax**
   ```python
   model_config = ConfigDict(from_attributes=True)
   # PAS class Config: orm_mode = True
   ```

4. **SQLAlchemy select() syntax**
   ```python
   query = select(Table).where(conditions)
   # PAS de SQL brut
   ```

5. **Docstrings sur toutes les routes**
   ```python
   """
   Description claire.
   
   Args:
       param: Description
       
   Returns:
       Type: Description
       
   Raises:
       HTTPException: Conditions
   """
   ```

6. **Logs pour les opérations importantes**
   ```python
   logger.info(f"Operation: {details}")
   logger.error(f"Error: {error}", exc_info=True)
   ```

7. **Tests Bruno pour chaque endpoint**

8. **Gestion d'erreurs explicite**
   ```python
   if not param:
       raise HTTPException(status_code=400, detail="Message clair")
   ```

### ❌ À NE JAMAIS Faire

1. **SQL brut avec string formatting**
   ```python
   # ❌ DANGER: SQL injection!
   query = f"SELECT * FROM table WHERE id = '{user_input}'"
   ```

2. **Blocking I/O dans async**
   ```python
   # ❌ Bloque l'event loop!
   async def handler():
       time.sleep(5)
   ```

3. **Sessions DB non fermées**
   ```python
   # ❌ Memory leak!
   def handler():
       db = APIDatabase(config.DB_URL)
       return db.query(Model).all()
       # Pas de db.close()!
   ```

4. **Pydantic v1 syntax**
   ```python
   # ❌ Obsolète!
   class Model(BaseModel):
       class Config:
           orm_mode = True
   ```

5. **Hardcoder des valeurs**
   ```python
   # ❌ Utiliser config!
   CORS_ORIGINS = ["http://localhost:3000"]
   ```

6. **Modifier ces fichiers sans raison**
   - `Dockerfile`
   - `entrypoint.sh`
   - `compose.yml` (sauf ajout de service)

7. **Oublier les tests**

---

## Documentation Détaillée

### Dans docs/

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture technique complète
  - Flux de données détaillé
  - Patterns de design
  - Performance et optimisations
  - Monitoring et observability
  - Évolution future

- **[docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md)** - Best practices FastAPI
  - Structure de projet
  - Sécurité (HTTPS, CORS, validation)
  - Logging et middleware
  - Base de données
  - Tests
  - Performance
  - Checklist de déploiement

### À la Racine

- **[README.md](README.md)** - Documentation utilisateur
  - Guide de démarrage rapide
  - Exemples d'utilisation
  - API endpoints
  - Déploiement

### Documentation Interactive

- **Swagger UI** : http://localhost:8051/docs
- **ReDoc** : http://localhost:8051/redoc

---

## 🔧 Configuration

### Variables d'Environnement

```bash
# .env
DB_URL=sqlite:///./database/db.sqlite
HOST=0.0.0.0
PORT=8080
RELOAD=false
CORS_ORIGINS=http://localhost:3000,http://localhost:8051
LOG_LEVEL=INFO
```

### Docker Watch Mode

- **Auto-sync** : Changements dans `src/**/*.py` synchronisés sans rebuild
- **Auto-rebuild** : Changements dans `requirements.txt` déclenchent rebuild
- Pas besoin de redémarrer manuellement !

---

## 🐛 Debugging

### Logs

```bash
# Temps réel
docker compose logs -f

# Par service
docker compose logs web

# Filtrer
docker compose logs | grep ERROR
docker compose logs | grep "Request ID"

# Dernières N lignes
docker compose logs --tail 50
```

### Tests Manuels

```bash
# Health check
curl http://localhost:8051/health

# Test GET
curl http://localhost:8051/v1/bus

# Test GET avec params
curl "http://localhost:8051/v1/direction/bus?bus_id=A"

# Test avec verbose
curl -v http://localhost:8051/v1/bus

# Test response time
curl -w "@-" -o /dev/null -s http://localhost:8051/v1/bus <<'EOF'
    time_total: %{time_total}s\n
EOF
```

### Swagger UI

Open http://localhost:8051/docs

- Tester tous les endpoints
- Voir les schémas
- Générer des exemples

---

## 📊 Métriques & Performance

### Response Times Actuels

- **Endpoints DB** : 3-50ms
- **Endpoint live** (`/bus_stop/live`) : 700-900ms (scraping externe)
- **Health check** : <1ms

### Headers Personnalisés

Chaque réponse inclut :
- `X-Request-ID` : UUID unique de la requête
- `X-Process-Time` : Temps de traitement en secondes

---

## ❓ FAQ pour Agents IA

### Q: Comment ajouter un nouveau champ à une réponse ?
1. Modifier le modèle SQLAlchemy (`database/Table.py`)
2. Générer migration Alembic
3. Appliquer migration
4. Mettre à jour schéma Pydantic (`models/schemas.py`)
5. Tests

### Q: Où ajouter de la logique métier complexe ?
Dans `src/services/` (actuellement vide). Créer un fichier de service et l'importer dans le router.

### Q: Comment gérer le scraping web ?
Voir `api/routers/bus_stop.py` → `get_bus_stop_live_info()` pour un exemple avec BeautifulSoup.

### Q: Async ou sync pour les fonctions ?
- **Async** : I/O bound (DB, HTTP requests, file I/O)
- **Sync** : CPU bound (calculs, transformations)

### Q: Comment tester sans Docker ?
Possible mais non recommandé. Docker garantit l'environnement cohérent.

---

## 📞 Ressources Externes

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Bruno Documentation](https://docs.usebruno.com/)

---

**Dernière mise à jour** : 2025-10-23  
**Version** : 2.0.0  
**Maintenu par** : Équipe de développement assistée par IA
