# SynchroBus API

API **non-officielle** permettant de récuperer des données sur les lignes de bus de la ville de Chambéry.

- [Installation](#installation)
- [Routes](#routes)
  - [`GET` `/v1/bus`](#get-v1bus)
  - [`GET` `/v1/bus/direction?id={bus_id}`](#get-v1busdirectionidbus_id)
  - [`GET` `/v1/direction`](#get-v1direction)
  - [`GET` `/v1/direction/bus?id={bus_id}`](#get-v1directionbusidbus_id)
  - [`GET` `/v1/direction/bus_stop?id={bus_stop_id}`](#get-v1directionbus_stopidbus_stop_id)
  - [`GET` `/v1/appleshortcuts/direction/bus?id={bus_id}`](#get-v1appleshortcutsdirectionbusidbus_id)
  - [`GET` `/v1/bus_stop`](#get-v1bus_stop)
  - [`GET` `/v1/bus_stop/direciton?id={direction_id}`](#get-v1bus_stopdirecitoniddirection_id)
  - [`GET` `/v1/appleshortcuts/bus_stop/direction?id={direction_id}`](#get-v1appleshortcutsbus_stopdirectioniddirection_id)
  - [`GET` `/v1/bus_stop/live/{bus_stop_id}`](#get-v1bus_stoplivebus_stop_id)
  - [`GET` `/v1/bus_stop/search/{query}`](#get-v1bus_stopsearchquery)

## Installation

```bash
git clone https://github.com/leodbrs/synchrobus-api
cd synchrobus-api
docker compose up -d
```

## Routes

### `GET` `/v1/bus`
Retourne la liste des bus
```json
[
  "A",
  "B",
  "C",
  "D"
]
```

### `GET` `/v1/bus/direction?id={bus_id}`
Retourne le bus d'**une direction**

```json
[
  "D"
]
```

### `GET` `/v1/direction`
Retourne toutes les directions

```json
[
  {
    "id": 1,
    "name": "Plage / technolac / landiers sud / gare"
  },
  {
    "id": 2,
    "name": "Universite jacob"
  },
  {
    "id": 4,
    "name": "Lorem ipsum dolor sit amet tation lorem."
  }
]
```

### `GET` `/v1/direction/bus?id={bus_id}`
Retourne les directions d'**un bus**

```json
[
  {
    "id": 1,
    "name": "Plage / technolac / landiers sud / gare"
  },
  {
    "id": 2,
    "name": "Universite jacob"
  }
]
```

### `GET` `/v1/direction/bus_stop?id={bus_stop_id}`
Retourne les directions d'**un arrêt de bus**

```json
[
  {
    "id": 1,
    "name": "Plage / technolac / landiers sud / gare"
  },
  {
    "id": 2,
    "name": "Universite jacob"
  }
]
```

### `GET` `/v1/appleshortcuts/direction/bus?id={bus_id}`
Retourne les directions d'**un bus** avec un format pour les shortcuts d'Apple

```json
{
  "Plage / technolac / landiers sud / gare": 1,
  "Universite jacob": 2
}
```

### `GET` `/v1/bus_stop`
Retourne tous les arrêts de bus

```json
[
  {
    "id": "GAMBE1",
    "name": "Gambetta"
  },
  {
    "id": "GAMBE2",
    "name": "Gambetta"
  },
  {
    "id": "GARE1",
    "name": "Gare"
  },
  {
    "id": "GARE2",
    "name": "Gare"
  }
]
```

### `GET` `/v1/bus_stop/direction?id={direction_id}`
Retourne les arrêts de bus d'**une direction**

```json
[
  {
    "id": "INES1",
    "name": "INES Sud"
  },
  {
    "id": "INES2",
    "name": "INES Sud"
  },
  {
    "id": "INSEC1",
    "name": "Technolac"
  },
  {
    "id": "INSEC2",
    "name": "Technolac"
  }
]
```

### `GET` `/v1/appleshortcuts/bus_stop/direction?id={direction_id}`
Retourne les arrêts de bus d'**une direction** avec un format pour les shortcuts d'Apple

```json
{
  "Chamoux": "HTCHA1",
  "Sources": "SOURC1",
  "Laitière": "LAITI1",
  "Croix De Bissy": "CRXBI1",
  "Bisseraine": "BISSE1",
  "Petite Forêt": "PTFOR1",
  "Debussy": "DEBUS1",
  "Victor Hugo": "VHUGO1",
  "Lycée Agricole": "LYAGR1",
  "Eglise Cognin": "EGCOG1",
  "Forgerie": "FORGE1",
  "Cognin Centre": "CECOG1",
  "Bosco": "BOSCO1",
  "Buet": "BUET1",
  "Hôpital Maché": "CHOSP1",
  "Château Des Ducs": "CHATE1",
  "Halles": "HALLE1",
  "Ducs": "DUCS1",
  "Clos Savoiroux": "CLSAV2",
  "Mérande": "MERAN2",
  "Tunnel": "TUNEL2",
  "Gonrat": "GONRA2",
  "Hôpital Bassens": "HOBAS2",
  "Bassens Centre": "CBASS2",
  "Boulodrome": "BOULO2",
  "Perrot": "PEROT2",
  "Marquises": "MARQU2",
  "Saint Alban Centre": "CSALB2",
  "Perrodière": "PEROD2",
  "Barillettes": "BARIL2",
  "Plaine Des Sports": "PLASP2"
}
```

### `GET` `/v1/bus_stop/live/{bus_stop_id}`
Retourne les horaires en direct d'un arrêt de bus

```json
[
  {
    "line": "A",
    "direction": "Université Jacob",
    "time": "20:26",
    "remaining": "dans 26 secondes"
  },
  {
    "line": "C",
    "direction": "Challes Centre",
    "time": "20:35",
    "remaining": "dans 7 minutes"
  },
  {
    "line": "A",
    "direction": "Université Jacob",
    "time": "20:46",
    "remaining": "dans 18 minutes"
  }
]
```


### `GET` `/v1/bus_stop/search/{query}`

Retourne les arrêts de bus correspondant à la recherche

```json
[
  {
    "id": "UBOUR1",
    "name": "Université Le Bourget"
  },
  {
    "id": "UBOUR2",
    "name": "Université Le Bourget"
  },
  {
    "id": "UJACO1",
    "name": "Université Jacob"
  },
  {
    "id": "UJACO2",
    "name": "Université Jacob"
  }
]
```