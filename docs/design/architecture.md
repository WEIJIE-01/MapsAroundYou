# Architecture Overview

**Smart Rental Search Algorithm**

## Design Decision

**Local data only** for destinations, commute-time lookup, and listings. No live APIs, geocoding, or real-time scraping.

---

## Component View

![Architecture — Component Overview](../assets/diagram_images/architecture-component.svg)

*Figure: Layer and dependency overview. See the Developer Guide's "Architecture & Coupling" section for the full narrative.*

---

## Components

### UI (GUI / CLI)

- **GUI**: Collects inputs, displays ranked results, restores last-used preferences on startup, and renders listing details plus the split commute breakdown (total, transit, walk, transfers, fare). Persists persona preset and dark-mode settings.
- **CLI**: Same search capability through `mapsaroundyou.cli.MapsAroundYouApp` for headless use.
- GUI talks only to `app.GuiSearchService`; CLI talks to `logic.SearchLogic` — neither depends on `storage.*` or `service.*` directly.

### Application (`mapsaroundyou.app`)

- **`ApplicationFactory`** is the sole composition root: the only place concrete repositories and services are instantiated. Exposes `createGuiSearchService()` and `createSearchLogic()`, both returning interface types.
- **`GuiSearchService`** is the narrow GUI-facing facade (search + metadata + preferences). Isolates JavaFX from `SearchLogic` and downstream layers.

### Logic

- Sets up the search pipeline
- Exposes UI-friendly operations
- See [API Spec](../api/api-spec.md) for operations

### Services

| Service | Responsibility |
|---------|----------------|
| **CommuteEstimator** | Local travel-time lookup between listing origin nodes and selected destinations |
| **ListingFilter** | Rent/time constraints, aircon filter |
| **ListingRanker** | Scoring plus selectable sorting |
| **RouteAnalyzer** | Walk-dominant detection and commute breakdown |

### Model

- Entities: `Listing`, `Destination`, `Preferences`, `Results`
- Immutable-ish; lightweight DTOs between layers

### Storage

- Loads local datasets: destinations, travel times, listings
- Persists last-used preferences for improved UX

---

## Data Flow

1. **User input** → GUI captures destination, rent, commute, transfer cap, walking cap, aircon, result count, sort mode, and walk-dominant toggle (CLI collects the same via command-line flags)
2. **Application layer** → GUI goes through `GuiSearchService`; CLI calls `SearchLogic` directly. Both paths are wired by `ApplicationFactory`
3. **Logic** loads data from Storage, invokes Services via pipeline
4. **ListingFilter** → **CommuteEstimator** → **RouteAnalyzer** → **ListingRanker** → ranked results
5. **UI** renders `SearchRow` items built from `SearchResponse.results()` (`SearchResult`)

---

## Related Documents

- [Software Design Document](./sdd.md)
- [API Spec](../api/api-spec.md)
- [Mock API / Data Schemas](../api/mock-api.md)
