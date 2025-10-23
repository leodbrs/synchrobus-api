# 📚 Documentation Technique - SynchroBus API

Ce dossier contient la documentation technique détaillée du projet.

## 📑 Index

### [ARCHITECTURE.md](ARCHITECTURE.md)
**Architecture technique complète du projet**

Contenu :
- Vue d'ensemble de l'architecture
- Stack technique détaillée
- Structure du projet
- Schéma de base de données
- Flux de données
- Patterns de design utilisés
- Configuration et sécurité
- Performance et optimisations
- Monitoring et observability
- Plan d'évolution

**Public** : Développeurs, architectes, DevOps

---

### [BEST_PRACTICES.md](BEST_PRACTICES.md)
**Guide des best practices FastAPI 2024**

Contenu :
- Structure de projet recommandée
- Sécurité (HTTPS, CORS, validation, rate limiting)
- Logging (configuration, middleware)
- Base de données (sessions, ORM, migrations)
- Modèles Pydantic
- Tests (structure, async client)
- Performance (async/sync, caching, pooling)
- Checklist de déploiement
- Outils recommandés

**Public** : Développeurs Python/FastAPI

---

## 🤖 Documentation pour Agents IA

### [../AGENTS.md](../AGENTS.md)
**Guide complet pour assistants IA (Cursor, Claude Code, GitHub Copilot)**

⚠️ **Note**: Ce fichier est à la racine du projet pour être lu automatiquement par les agents IA.

Contenu :
- Vue d'ensemble rapide
- Stack technique
- Patterns de code
- Workflows communs
- Règles à suivre/éviter
- FAQ
- Exemples complets

**Public** : Assistants IA, développeurs assistés par IA

---

## 📖 Documentation Utilisateur

### [../README.md](../README.md)
**Documentation principale pour les utilisateurs de l'API**

Contenu :
- Guide de démarrage rapide
- Exemples d'utilisation
- Liste des endpoints
- Exemples curl/Python/JavaScript
- Déploiement
- Contribution

**Public** : Utilisateurs de l'API, développeurs externes

---

## 🗂️ Organisation de la Documentation

```
synchrobus-api/
├── README.md                # Documentation utilisateur (démarrage rapide)
├── AGENTS.md                # Guide pour IA (contexte complet)
│
└── docs/                    # Documentation technique
    ├── README.md            # Ce fichier (index)
    ├── ARCHITECTURE.md      # Architecture détaillée
    └── BEST_PRACTICES.md    # Best practices FastAPI
```

---

## 🎯 Quel Document Lire ?

### Je veux utiliser l'API
→ **[README.md](../README.md)**

### Je veux développer sur le projet
→ **[AGENTS.md](../AGENTS.md)** (quick start)  
→ **[BEST_PRACTICES.md](BEST_PRACTICES.md)** (conventions)

### Je veux comprendre l'architecture
→ **[ARCHITECTURE.md](ARCHITECTURE.md)**

### Je suis un agent IA
→ **[AGENTS.md](../AGENTS.md)** (tout le contexte nécessaire)

### Je veux déployer en production
→ **[BEST_PRACTICES.md](BEST_PRACTICES.md)** (section déploiement)  
→ **[README.md](../README.md)** (section déploiement)

---

## 📝 Contribuer à la Documentation

### Mise à Jour

Lors de modifications du code :
- Mettre à jour **AGENTS.md** si patterns de code changent
- Mettre à jour **ARCHITECTURE.md** si structure change
- Mettre à jour **README.md** si API change
- Mettre à jour **BEST_PRACTICES.md** si nouvelles pratiques

### Format

- Markdown avec emojis pour la lisibilité
- Exemples de code avec syntaxe highlighting
- Sections clairement délimitées
- TOC (table des matières) pour documents longs
- Exemples concrets et testés

---

**Dernière mise à jour** : 2025-10-23  
**Maintenu par** : Équipe de développement
