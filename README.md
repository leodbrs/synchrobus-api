# SynchroBus API

> **Unofficial API** for Chambéry bus data

[![FastAPI](https://img.shields.io/badge/FastAPI-0.119+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com)
[![Tests](https://img.shields.io/badge/Tests-29%2F29-success?style=flat)]()

REST API built with FastAPI providing real-time information about bus lines, stops, and schedules for the city of Chambéry.

## Features

- **Static data**: Bus lines, directions, stops
- **Real-time schedules**: Scraping from official Synchro-Bus website
- **Apple Shortcuts compatible**: Dict format for iOS
- **Modern REST API**: FastAPI with Pydantic validation
- **Interactive documentation**: Auto-generated OpenAPI/Swagger
- **Docker ready**: Simplified deployment
- **Complete tests**: 29 integration tests with Bruno

## Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) Bruno CLI for testing

### Installation

```bash
# Clone the repository
git clone https://github.com/leodbrs/synchrobus-api
cd synchrobus-api

# Launch with Docker
docker compose -f compose.dev.yml up -d
```

The API is now available at **http://localhost:8051**

### Interactive Documentation

Access the Swagger documentation: **http://localhost:8051/docs**

## Usage

### Main Endpoints

#### Buses

```bash
# List all buses
GET /v1/bus
# Response: ["A", "B", "C", "D"]

# Buses for a specific direction
GET /v1/bus/direction?direction_id=1
# Response: ["A", "C"]
```

#### Directions

```bash
# All directions
GET /v1/direction
# Response: [{"id": 1, "name": "Université Jacob"}, ...]

# Directions for a bus
GET /v1/direction/bus?bus_id=A
# Response: [{"id": 1, "name": "Université Jacob"}, ...]

# Directions for a stop
GET /v1/direction/bus_stop?bus_stop_id=GAMBE1
# Response: [{"id": 1, "name": "..."}, ...]
```

#### Bus Stops

```bash
# All stops
GET /v1/bus_stop
# Response: [{"id": "GAMBE1", "name": "Gambetta"}, ...]

# Stops for a direction
GET /v1/bus_stop/direction?direction_id=1
# Response: [{"id": "GARE1", "name": "Gare"}, ...]

# Search for a stop
GET /v1/bus_stop/search/université
# Response: [{"id": "UJACO1", "name": "Université Jacob"}, ...]

# Real-time schedules
GET /v1/bus_stop/live/GAMBE1
# Response: [
#   {
#     "line": "A",
#     "direction": "Université Jacob",
#     "time": "14:26",
#     "remaining": "in 3 minutes"
#   }
# ]
```

#### Apple Shortcuts (Dict Format)

```bash
# Directions for iOS Shortcuts
GET /v1/appleshortcuts/direction/bus?bus_id=A
# Response: {"Université Jacob": 1, "Gare": 2}

# Stops for iOS Shortcuts
GET /v1/appleshortcuts/bus_stop/direction?direction_id=1
# Response: {"Gambetta": "GAMBE1", "Gare": "GARE1"}
```

### Examples with curl

```bash
# Get all buses
curl http://localhost:8051/v1/bus

# Search stops
curl http://localhost:8051/v1/bus_stop/search/gare

# Live schedules
curl http://localhost:8051/v1/bus_stop/live/GAMBE1

# Health check
curl http://localhost:8051/health
```

### Examples with Python

```python
import requests

# Simple API client
class SynchroBusAPI:
    BASE_URL = "http://localhost:8051"
    
    def get_all_buses(self):
        return requests.get(f"{self.BASE_URL}/v1/bus").json()
    
    def get_live_times(self, bus_stop_id):
        return requests.get(
            f"{self.BASE_URL}/v1/bus_stop/live/{bus_stop_id}"
        ).json()

# Usage
api = SynchroBusAPI()
buses = api.get_all_buses()
print(f"Available lines: {buses}")

times = api.get_live_times("GAMBE1")
for bus in times:
    print(f"{bus['line']} → {bus['direction']} - {bus['remaining']}")
```

### Examples with JavaScript/Fetch

```javascript
// Get real-time schedules
async function getLiveTimes(busStopId) {
  const response = await fetch(
    `http://localhost:8051/v1/bus_stop/live/${busStopId}`
  );
  const data = await response.json();
  
  data.forEach(bus => {
    console.log(`${bus.line} → ${bus.direction}: ${bus.remaining}`);
  });
}

getLiveTimes('GAMBE1');
```

## Architecture

```
src/
├── api/
│   ├── dependencies.py        # Dependency injection
│   └── routers/               # Routes by domain
│       ├── bus.py
│       ├── direction.py
│       ├── bus_stop.py
│       └── apple_shortcuts.py
├── core/
│   ├── config.py              # Configuration
│   ├── logging_config.py      # Structured logging
│   └── middleware.py          # CORS, logging
├── database/
│   ├── Database.py            # Session factory
│   ├── Table.py               # SQLAlchemy models
│   └── alembic/               # Migrations
├── models/
│   └── schemas.py             # Pydantic schemas
└── main.py                    # FastAPI app
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for more details.

## Tests

### With Bruno (Recommended)

```bash
# Install Bruno CLI
brew install bruno-cli  # macOS
# or npm install -g @usebruno/cli

# Run all tests
cd bruno
bru run --env local .

# Expected result: 29/29 tests ✓
```

### Manual Tests

```bash
# Check that the API works
curl http://localhost:8051/health

# Test an endpoint
curl http://localhost:8051/v1/bus

# View logs
docker compose logs -f
```

## Development

### Local Setup

```bash
# Clone the repo
git clone https://github.com/leodbrs/synchrobus-api
cd synchrobus-api

# Copy configuration
cp .env.example .env

# Launch in dev mode (with hot reload)
docker compose -f compose.dev.yml up -d

# Changes in src/ are automatically synchronized
```

### Database Structure

**Main Tables**:
- `bus`: Bus lines (A, B, C, D)
- `direction`: Line directions
- `bus_stop`: Bus stops

**Relations**:
- `bus_direction`: Bus ↔ Direction
- `bus_stop_direction`: Stop ↔ Direction
- `bus_stop_bus`: Stop ↔ Bus

### Adding an Endpoint

1. **Identify the domain**: bus, direction, bus_stop, apple_shortcuts
2. **Add to the router**: `src/api/routers/{domain}.py`
3. **Create Pydantic schema**: `src/models/schemas.py`
4. **Add Bruno test**: `bruno/New Endpoint.bru`
5. **Test**: `bru run --env local bruno/`

### DB Migration

```bash
# Generate a migration
docker exec synchrobus-api-web-1 alembic revision --autogenerate -m "description"

# Apply
docker exec synchrobus-api-web-1 alembic upgrade head

# Rollback
docker exec synchrobus-api-web-1 alembic downgrade -1
```

## Monitoring

### Logs

```bash
# View logs in real-time
docker compose logs -f

# Logs with Request ID and processing time
# Format: [timestamp] [level] message | Request ID: xxx | Time: 0.04s
```

### Metrics

Each response includes custom headers:
- `X-Request-ID`: Unique request ID
- `X-Process-Time`: Processing time (seconds)

### Health Check

```bash
curl http://localhost:8051/health
# {"status": "healthy", "version": "2.0.0"}
```

## Security

### Implemented
- Input validation (Pydantic)
- Parameterized SQL queries (SQLAlchemy)
- CORS configured
- Basic security headers

### Production Recommendations
- HTTPS mandatory
- Rate limiting (slowapi)
- Authentication if private API
- Security headers (Helmet)
- Centralized logging
- Monitoring (Prometheus/Grafana)

## Production Deployment

### With Docker

```bash
# Build the image
docker build -t synchrobus-api .

# Run in production
docker run -d \
  -p 8080:8080 \
  -e ENVIRONMENT=production \
  -e DB_URL=postgresql://... \
  -e CORS_ORIGINS=https://yourdomain.com \
  synchrobus-api
```

Or use the production compose file:

```bash
docker compose -f compose.prod.yml up -d
```

### Environment Variables

```bash
ENVIRONMENT=production              # production or development
DB_URL=sqlite:///./database/db.sqlite  # or PostgreSQL
HOST=0.0.0.0
PORT=8080
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
LOG_LEVEL=INFO
```

### Recommendations

- Use PostgreSQL instead of SQLite
- Reverse proxy (Nginx/Traefik) for HTTPS
- Monitoring with Prometheus
- Centralized logs (ELK Stack)
- Automatic DB backup
- CI/CD (GitHub Actions)

## Documentation

### For Users
- **[README.md](README.md)** - This file (getting started guide)
- **API Docs** - http://localhost:8051/docs (Interactive Swagger)
- **ReDoc** - http://localhost:8051/redoc (Alternative documentation)

### For Developers
- **[AGENTS.md](AGENTS.md)** - Complete guide for AI assistants
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Detailed technical architecture
- **[docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md)** - FastAPI best practices 2024

### Tests
- **Bruno Collection** - `bruno/` (29 integration tests)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

### Quick Start

```bash
# Fork & clone
git clone https://github.com/YOUR_USERNAME/synchrobus-api

# Create a branch
git checkout -b feature/my-feature

# Develop & test
docker compose -f compose.dev.yml up -d
bru run --env local bruno/

# Commit & Push
git commit -m "feat(bus): add new endpoint"
git push origin feature/my-feature

# Create a Pull Request
```

### Conventions

- **Commits**: `<type>(<scope>): <description>`
  - Types: feat, fix, docs, refactor, test, chore
- **Code**: PEP 8 + type hints
- **Tests**: Add a Bruno test for each endpoint
- **Docs**: Update if API changes

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- City of Chambéry for public data
- [FastAPI](https://fastapi.tiangolo.com/) for the framework
- [Bruno](https://www.usebruno.com/) for the testing tool
- Open-source community

## Support

- **Issues**: [GitHub Issues](https://github.com/leodbrs/synchrobus-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/leodbrs/synchrobus-api/discussions)

## Roadmap

### Version 2.1
- [ ] Redis cache for static data
- [ ] Rate limiting
- [ ] Unit tests (pytest)
- [ ] CI/CD GitHub Actions

### Version 2.2
- [ ] JWT Authentication
- [ ] PostgreSQL migration
- [ ] Prometheus metrics
- [ ] WebSocket for live updates

### Version 3.0
- [ ] API versioning v3
- [ ] GraphQL endpoint
- [ ] Multi-language support
- [ ] Mobile SDK (iOS/Android)

---

<p align="center">
  Made with ❤️ in Chambéry
</p>

<p align="center">
  <a href="https://github.com/leodbrs">GitHub</a> •
  <a href="https://github.com/leodbrs/synchrobus-api/issues">Report Bug</a> •
  <a href="https://github.com/leodbrs/synchrobus-api/issues">Request Feature</a>
</p>
