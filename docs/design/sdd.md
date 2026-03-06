# Software Design Document (SDD)

**Smart Rental Search Algorithm**

## 1. Purpose and Scope

### Goal

A desktop GUI application that helps newcomers to Singapore find rental listings based on a primary destination (e.g., campus, office, hospital, or landmark) and commute constraints, delivered as a runnable JAR.

### In-scope (by the roadmap)

- **V1.2**: Set primary destination + filter by monthly rent
- **V1.3 (MVP)**: Commute time cap + generate shortlist output
- **V1.4 (Alpha)**: Anti-walk-dominant route filter + commute summary breakdown

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
| **UI (GUI)** | Collects inputs from user, displays ranked results, displays listing details + commute breakdown |
| **Logic** | Sets up the search pipeline and exposes UI-friendly operations |
| **Services** | CommuteEstimator, ListingFilter, ListingRanker, RouteAnalyzer |
| **Model** | Entities (Listing, Destination, Preferences, Results) |
| **Storage** | Loads local datasets (destinations/travel-times/listings), optional persistence of preferences for improved UX |

See [Architecture Overview](./architecture.md) for details.

---

## 3. Module Decomposition

### 3.1 UI (GUI)

**Responsibilities**

- Destination selection UI (supported destination picker)
- Filter inputs: max rent, max commute mins, require aircon
- Results list/table: top matches + basic fields
- Details panel/dialog: full listing + commute breakdown (V1.4)

**Outputs**

- User actions → Logic calls
- Rendered `SearchResultViewModel[]`

### 3.2 Logic

**Responsibilities**

- Validate user inputs
- Execute search pipeline (load → filter → estimate → rank)
- Provide view models for UI
- Centralize error handling (user-friendly messages)

**Primary operations**

- `setDestination(destinationId)`
- `setPreferences(maxRent, maxCommuteMinutes, requireAircon, transportMode)`
- `generateShortlist()` → `List<SearchResult>`
- `getListingDetails(listingId)` → `ListingDetails`
- `getCommuteDetails(listingId)` → `CommuteEstimate` (V1.4)

### 3.3 Services

| Service | Operations |
|---------|------------|
| **ListingFilter** | `filterByRent(listings, maxRent)`, `filterByAircon(listings, requireAircon)` |
| **CommuteEstimator** | `estimate(originNodeId, destinationId, mode)` → `CommuteEstimate` — Implementation: local travel-time matrix lookup |
| **ListingRanker** | Deterministic sorting/scoring (see §5) |
| **RouteAnalyzer** (V1.4) | `isWalkDominant(commuteEstimate)` → `bool`, `summarize(commuteEstimate)` → `CommuteSummary` |

### 3.4 Model (Domain)

Immutable-ish entities; lightweight DTOs between layers.

### 3.5 Storage (Local Data)

- `DestinationRepository` (destinations file)
- `TravelTimeRepository` (travel-times file)
- `ListingRepository` (listings file)
- Optional: `UserPrefsRepository` (save last-used preferences)

---

## 4. Data Model

### 4.1 Entities

| Entity | Fields |
|--------|--------|
| **Destination** | `destinationId: String`, `name: String`, `category: String`, `area: String` |
| **TravelTimeRecord** | `originNodeId: String`, `destinationId: String`, `totalMinutes: int`, optional: `transitMinutes`, `walkMinutes`, `transfers`, `source` |
| **TravelTimeMatrix** | `lookup: Map<String, Map<String, TravelTimeRecord>>` |
| **RentalListing** | `listingId: String`, `title: String`, `monthlyRent: int`, `hasAircon: boolean`, `originNodeId: String`, optional: `address`, `roomType`, `sourcePlatform`, `destinationTags`, `notes` |
| **UserPreferences** | `destinationId: String`, `maxRent: int`, `maxCommuteMinutes: int`, `requireAircon: boolean`, `transportMode: enum` (MVP default: public transport) |
| **CommuteEstimate** | `totalMinutes: int`, `transitMinutes: int`, `walkMinutes: int` (0 for MVP), `transfers: int`, `routeStations: List<String>` |
| **SearchResult** | `listing: RentalListing`, `commute: CommuteEstimate`, `score: double` |

### 4.2 Relationships

- `RentalListing.originNodeId` → `TravelTimeRecord.originNodeId`
- `UserPreferences.destinationId` → `Destination.destinationId`
- TravelTimeMatrix contains TravelTimeRecords keyed by origin and destination
- SearchResult composes RentalListing + CommuteEstimate

---

## 5. Core Workflows

### Workflow A — Set Primary Destination (V1.2)

1. User selects a supported destination in the GUI.
2. UI calls `Logic.setDestination(destinationId)`.
3. Logic stores `destinationId` in `UserPreferences`.
4. (Optional) Storage persists preferences for improved UX.

### Workflow B — Generate Shortlist (MVP V1.3)

1. User sets maxRent, maxCommuteMinutes, requireAircon and clicks Search.
2. UI calls `Logic.generateShortlist()`.
3. Logic loads listings (Storage).
4. ListingFilter applies rent + aircon filters.
5. For each remaining listing: `CommuteEstimator.estimate(listing.originNodeId, destinationId, 'PUBLIC_TRANSPORT')` — discard if `totalMinutes > maxCommuteMinutes`.
6. In V1.4, `RouteAnalyzer.isWalkDominant()` discards routes where `walkMinutes / totalMinutes` is greater than or equal to the configured threshold.
7. ListingRanker computes score and sorts results.
8. UI displays ranked results.

```mermaid
flowchart TD
    A([User sets filters & clicks Search]) --> B[UI calls Logic.generateShortlist]
    B --> C[Storage: load listings dataset]
    C --> D{Schema valid?}
    D -- No --> E[/DataLoadException → UI error message/]
    D -- Yes --> F[ListingFilter.filterByRent]
    F --> G[ListingFilter.filterByAircon]
    G --> H{Any listings remaining?}
    H -- None --> I[/NoResultsException → UI empty-state message/]
    H -- Yes --> J[For each listing: CommuteEstimator.estimate via travel-time lookup]
    J --> K{totalMinutes > maxCommuteMinutes?}
    K -- Yes --> L[Discard listing]
    K -- No --> M[RouteAnalyzer.isWalkDominant]
    M --> N{walkMinutes / totalMinutes >= threshold?}
    N -- Yes --> O[Discard listing]
    N -- No --> P[Keep listing]
    L --> Q{More listings?}
    O --> Q
    P --> Q
    Q -- Yes --> J
    Q -- No --> R{Results non-empty?}
    R -- None --> I
    R -- Yes --> S[ListingRanker: sort by commute → rent → listingId]
    S --> T[Return SearchResultViewModel list]
    T --> U([UI renders ranked results panel])
```

### Workflow C — Commute Breakdown (V1.4)

1. User opens listing details (click result).
2. Logic returns CommuteEstimate + route summary.
3. `RouteAnalyzer.summarize()` formats the transit, walking, transfer, and total-time breakdown.
4. UI displays breakdown: transit vs walking, transfers, total time.

```mermaid
flowchart TD
    A([User clicks a listing result]) --> B[UI calls Logic.getCommuteDetails listingId]
    B --> C[Storage: retrieve listing + CommuteEstimate]
    C --> D{listingId valid?}
    D -- No --> E[/ListingNotFoundException → UI error message/]
    D -- Yes --> F[RouteAnalyzer.summarize commuteEstimate]
    F --> G[Return CommuteSummary: transitMinutes, walkMinutes, transfers, total]
    G --> H([UI renders commute breakdown panel])
```
---

## 6. Ranking and Scoring (Deterministic)

**Default sort** (for stability; dataset shouldn't be too large):

1. Lowest `commute.totalMinutes`
2. Lowest `listing.monthlyRent`
3. Tie-breaker: `listingId` (stable ordering)

**Optional score function** (for display):

```
score = w1 * (normalizedCommute) + w2 * (normalizedRent)
```

(weights fixed in config)

---

## 7. Constraints and Assumptions

### Constraints

- MVP runs offline
- GUI required for all core user flows
- Deliverable must be runnable as a JAR
- Data loaded from local files (JSON/CSV); schema must be validated on load

### Assumptions

- Destination is represented as a supported campus, office, hospital, or place from a finite list
- Each listing provides `originNodeId` for travel-time lookup (no geocoding in MVP)
- Commute times are approximations derived from precomputed local travel-time records
- MVP transport mode defaults to public transport; walking modeled minimally (V1.4)

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
