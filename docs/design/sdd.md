# Software Design Document (SDD)

**Smart Rental Search Algorithm**

## 1. Purpose and Scope

### Goal

A desktop GUI application that helps newcomers to Singapore find rental listings based on a primary destination (e.g., campus, office, hospital, or landmark) and commute constraints, delivered as a runnable JAR.

### In-scope for the current `v0.4` release

- Primary destination selection plus monthly rent filtering
- Commute, transfer, and walking caps with ranked shortlist output
- Walk-dominant route rejection and commute summary breakdown
- Persona presets, dark mode, and local preference persistence
- Domain-specific error handling at CLI and GUI boundaries
- Public API documentation enforced through Javadoc-oriented quality checks
- JavaFX access routed through the application-layer `GuiSearchService` facade
- Results and details surfaces tuned to show walking time, transfers, and split commute facts more clearly

### Out-of-scope (SDD-level assumptions)

- Live routing APIs (e.g., Google Maps)
- Address geocoding / map rendering
- Real-time rental scraping; user accounts

> *Prof suggested against this by strongly recommending using local data*

Since we use local data, our app will be accurate only up to the last dataset update date, and the UI should display a notice like "Data accurate as of <last-updated date>" based on dataset metadata.

---

## 2. Architecture Overview

**Design decision**: Local data only for destinations, commute times, and listings

### Component View

| Component | Description |
|-----------|-------------|
| **UI (GUI / CLI)** | Collects inputs, displays ranked results, manages settings, and shows listing details plus commute breakdown; entry points call into the layers below |
| **Application (`mapsaroundyou.app`)** | Composition root and narrow facades: `ApplicationFactory` wires storage adapters and domain services; JavaFX uses `GuiSearchService` (search + metadata + preferences) so the GUI does not depend on `SearchLogic` directly |
| **Logic** | Sets up the search pipeline and exposes workflow operations (`SearchLogic`) |
| **Services** | CommuteEstimator, ListingFilter, ListingRanker, RouteAnalyzer |
| **Model** | Entities (Listing, Destination, Preferences, Results) |
| **Storage** | Loads local datasets (destinations/travel-times/listings) and persists last-used preferences for improved UX |

**Dependency direction (summary):** `mapsaroundyou.gui` → `mapsaroundyou.app` (facades) → `mapsaroundyou.logic` → `mapsaroundyou.service` + `mapsaroundyou.storage`. Storage is reached through repository interfaces; service helpers (`CommuteEstimator`, `ListingFilter`, `ListingRanker`, `RouteAnalyzer`) are concrete but injected into `DefaultSearchLogic` via constructor, keeping the wiring open to future interface extraction. The CLI entry point uses `ApplicationFactory.createSearchLogic()` and depends on `mapsaroundyou.logic` with the same composed stack. Concrete CSV/properties adapters in `mapsaroundyou.storage` are instantiated only from `ApplicationFactory`.

See [Architecture Overview](./architecture.md) for details.

---

## 3. Module Decomposition

### 3.1 UI (GUI)

**Responsibilities**

- Destination selection UI (supported destination picker)
- Filter inputs: max rent, max commute mins, max transfers, max walk mins, require aircon, result limit, sort mode, walk-dominant toggle
- Results list/table: top matches + rent, total commute, walk time, transfers, and aircon
- Settings surface: persona preset and dark-mode toggle
- Details panel/dialog: full selected-listing details, including match score + split commute breakdown (V1.4)

**Outputs**

- User actions → application-layer search API (`GuiSearchService`)
- Rendered result rows and details

### 3.2 Application (`mapsaroundyou.app`)

**Responsibilities**

- **Composition:** `ApplicationFactory` constructs repositories, validates bundled datasets, and wraps `DefaultSearchLogic` with `PersistentSearchLogic` and `PropertiesUserPrefsRepository`.
- **GUI boundary:** `GuiSearchService` / `DefaultGuiSearchService` expose typed `SearchRequest` / `SearchResponse` flows and guard errors for the JavaFX layer, delegating to `SearchLogic`.

**Dependency rule:** GUI code depends on types in `mapsaroundyou.app` and `mapsaroundyou.model`, not on concrete storage or the full `SearchLogic` surface area.

### 3.3 Logic

**Responsibilities**

- Validate user inputs
- Execute search pipeline (load → filter → estimate → rank)
- Provide view models for UI
- Centralize error handling (user-friendly messages)
- Restore and persist last-used preferences through storage

**Primary operations**

- `updatePreferences(preferences)`
- `generateShortlist()` → `List<SearchResult>`
- `getListingDetails(listingId)` → `ListingDetails`
- `getCommuteDetails(listingId)` → `CommuteEstimate`

### 3.4 Services

| Service | Operations |
|---------|------------|
| **ListingFilter** | `filterByRent(listings, maxRent)`, `filterByAircon(listings, requireAircon)` |
| **CommuteEstimator** | `estimate(originNodeId, destinationId, mode)` → `CommuteEstimate` — Implementation: local travel-time matrix lookup |
| **ListingRanker** | Deterministic selectable sorting/scoring (see §5) |
| **RouteAnalyzer** | `isWalkDominant(commuteEstimate)` → `bool`, `summarize(commuteEstimate)` → `CommuteSummary` |

### 3.5 Model (Domain)

Immutable-ish entities; lightweight DTOs between layers.

### 3.6 Storage (Local Data)

- `DestinationRepository` (destinations file)
- `TravelTimeRepository` (travel-times file)
- `ListingRepository` (listings file)
- `UserPrefsRepository` (save last-used preferences)

---

## 4. Data Model

### 4.1 Entities

| Entity | Fields |
|--------|--------|
| **Destination** | `destinationId: String`, `name: String`, `category: String`, `area: String` |
| **TravelTimeRecord** | `originNodeId: String`, `destinationId: String`, `totalMinutes: int`, optional: `transitMinutes`, `walkMinutes`, `transfers`, `source` |
| **TravelTimeMatrix** | `lookup: Map<String, Map<String, TravelTimeRecord>>` |
| **RentalListing** | `listingId: String`, `title: String`, `monthlyRent: int`, `hasAircon: boolean`, `originNodeId: String`, optional: `address`, `roomType`, `sourcePlatform`, `destinationTags`, `notes` |
| **UserPreferences** | `destinationId: String`, `maxRent: int`, `maxCommuteMinutes: int`, `maxTransfers: int`, `maxWalkMinutes: int`, `requireAircon: boolean`, `transportMode: enum`, `resultLimit: int`, `sortMode: enum`, `excludeWalkDominantRoutes: boolean` |
| **CommuteEstimate** | `totalMinutes: int`, `transitMinutes: int`, `walkMinutes: int`, `transfers: int`, `routeStations: List<String>` |
| **SearchResult** | `listing: RentalListing`, `commute: CommuteEstimate`, `score: double` |

### 4.2 Relationships

- `RentalListing.originNodeId` → `TravelTimeRecord.originNodeId`
- `UserPreferences.destinationId` → `Destination.destinationId`
- TravelTimeMatrix contains TravelTimeRecords keyed by origin and destination
- SearchResult composes RentalListing + CommuteEstimate

---

## 5. Core Workflows

### Workflow A — Set Primary Destination

1. User selects a supported destination and other search preferences in the GUI or CLI.
2. GUI calls `GuiSearchService.search(request)` (which delegates to `SearchLogic.updatePreferences`); CLI calls `SearchLogic.updatePreferences(preferences)` directly after `ApplicationFactory.createSearchLogic()`.
3. Logic stores the complete `UserPreferences`.
4. Storage persists preferences after a successful search (via the `PersistentSearchLogic` decorator).

### Workflow B — Generate Shortlist

1. User sets destination, maxRent, maxCommuteMinutes, maxTransfers, maxWalkMinutes, requireAircon, resultLimit, sortMode, and optional walk-dominant rejection, then clicks Search.
2. GUI calls `GuiSearchService.search(request)` which invokes `SearchLogic.generateShortlist()` (CLI calls `SearchLogic.generateShortlist()` directly).
3. Logic loads listings (Storage).
4. ListingFilter applies rent plus aircon filters.
5. For each remaining listing: `CommuteEstimator.estimate(listing.originNodeId, destinationId, 'PUBLIC_TRANSPORT')` — discard if `totalMinutes > maxCommuteMinutes`.
6. Discard listings where `transfers > maxTransfers`.
7. Discard listings where `walkMinutes > maxWalkMinutes`.
8. If enabled, `RouteAnalyzer.isWalkDominant()` discards routes where `walkMinutes / totalMinutes` is greater than or equal to the configured threshold.
9. ListingRanker computes score and sorts results according to `sortMode`.
10. Logic truncates the ranked results to `resultLimit`.
11. UI displays ranked results.

![Generate Shortlist — Activity](../assets/diagram_images/activity-generate-shortlist.svg)

*Figure: Generate Shortlist activity diagram.*

### Workflow C — Commute Breakdown

1. User opens listing details (click result).
2. GUI calls `GuiSearchService.getListingDetails(listingId)`, which delegates to `SearchLogic.getListingDetails(listingId)`; the response carries the listing plus an `Optional<CommuteEstimate>`.
3. `RouteAnalyzer.summarize()` formats the transit, walking, transfer, and total-time breakdown.
4. GUI displays breakdown: total time, transit, walking, transfers, and fare.

![Commute Breakdown — Sequence](../assets/diagram_images/sequence-commute-breakdown.svg)

*Figure: Commute Breakdown sequence diagram covering listing-absent and destination-unset branches.*

---

## 6. Ranking and Scoring (Deterministic)

**Supported sorts**

1. `COMMUTE`: Lowest `commute.totalMinutes`, then lowest `listing.monthlyRent`, then `listingId`
2. `RENT`: Lowest `listing.monthlyRent`, then lowest `commute.totalMinutes`, then `listingId`
3. `BALANCED`: Highest score, then lowest `commute.totalMinutes`, then lowest `listing.monthlyRent`, then `listingId`

**Score function** (for display and balanced sorting):

```
score = w1 * (normalizedCommute) + w2 * (normalizedRent)
```

(weights fixed in config)

---

## 7. Constraints and Assumptions

### Constraints

- Current release runs offline
- GUI required for all core user flows
- Deliverable must be runnable as a JAR
- Data loaded from local files (JSON/CSV); schema must be validated on load

### Assumptions

- Destination is represented as a supported campus, office, hospital, or place from a finite list
- Each listing provides `originNodeId` for travel-time lookup (no geocoding in the shipped release)
- Commute times are approximations derived from precomputed local travel-time records
- Transport mode defaults to public transport; walking and transfers are included in shipped commute output

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Local dataset incomplete/inconsistent | Empty/incorrect results | Schema validation + curated demo dataset + clear load errors |
| Travel-time lookup mistakes | Wrong commute times | Unit tests with deterministic fixtures; verify representative origin-destination pairs |
| GUI scope creep | Time blow-up | Minimal screens: Search + Results + Details dialog |
| UI–Logic coupling | Integration pain | Strict interfaces + view models; no domain logic in UI |
| Performance with many listings | Slow search | Keep demo dataset curated; index travel times by origin and destination |
| Ambiguous "walk-dominant" definition | Feature disagreement | Define threshold (e.g., `walkMinutes / totalMinutes >= T`) in config and document it |
