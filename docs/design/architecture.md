# Architecture Overview

**Smart Rental Search Algorithm**

## Design Decision

**Local data only** for routing + listings. No live APIs, geocoding, or real-time scraping.

---

## Component View

![Architecture Diagram](../assets/images/architecture-diagram.png)

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI (GUI)                                 │
│  • Destination selection (MRT station picker)                    │
│  • Filter inputs (max rent, max commute, require aircon)         │
│  • Results list/table                                            │
│  • Details panel/dialog (V1.4: commute breakdown)                │
└────────────────────────────┬────────────────────────────────────┘
                             │ User actions → Logic calls
                             │ Rendered SearchResultViewModel[]
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Logic                                   │
│  • Validate inputs                                               │
│  • Execute search pipeline (load → filter → estimate → rank)     │
│  • Provide view models for UI                                    │
│  • Centralize error handling                                     │
└──────┬──────────────────┬──────────────────┬────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   Services   │  │    Model     │  │     Storage      │
│              │  │              │  │                  │
│ CommuteEst.  │  │ Listing      │  │ StationRepo      │
│ ListingFilter│  │ Station      │  │ TransitGraphRepo │
│ ListingRanker│  │ Preferences  │  │ ListingRepo      │
│ RouteAnalyzer│  │ Results      │  │ UserPrefsRepo    │
└──────────────┘  └──────────────┘  └──────────────────┘
```

---

## Components

### UI (GUI)

- Collects inputs from user
- Displays ranked results
- Displays listing details + commute breakdown (V1.4)

### Logic

- Sets up the search pipeline
- Exposes UI-friendly operations
- See [API Spec](../api/api-spec.md) for operations

### Services

| Service | Responsibility |
|---------|----------------|
| **CommuteEstimator** | Graph shortest path (Dijkstra on transit graph) |
| **ListingFilter** | Rent/time constraints, aircon filter |
| **ListingRanker** | Scoring + sorting |
| **RouteAnalyzer** | Walk-dominant detection, commute breakdown (V1.4) |

### Model

- Entities: `Listing`, `Station`, `Preferences`, `Results`
- Immutable-ish; lightweight DTOs between layers

### Storage

- Loads local datasets: stations, edges, listings
- Optional: persistence of preferences for improved UX

---

## Data Flow

1. **User input** → UI captures destination, max rent, max commute, aircon preference
2. **Logic** loads data from Storage, invokes Services via pipeline
3. **ListingFilter** → **CommuteEstimator** → **ListingRanker** → ranked results
4. **UI** renders `SearchResultViewModel[]`

---

## Related Documents

- [Software Design Document](./sdd.md)
- [API Spec](../api/api-spec.md)
- [Mock API / Data Schemas](../api/mock-api.md)
