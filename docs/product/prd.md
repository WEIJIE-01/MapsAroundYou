# Product Requirements Document (PRD)

**Product:** MapsAroundYou — Smart Rental Search
**Version:** 1.0
**Last Updated:** March 6, 2026
**Status:** Active

---

## 1. Overview

MapsAroundYou is a desktop GUI application that helps newcomers to Singapore — primarily international students and new working professionals — find rental listings that fit their budget and commute constraints. Users specify a primary destination (e.g., an MRT station near their campus or office), set filters such as maximum rent and maximum commute time, and receive a ranked shortlist of rental listings that meet their criteria.

The application runs entirely offline using local datasets for MRT transit graph data and rental listings.

---

## 2. Problem Statement

International students and new working professionals arriving in Singapore face difficulty identifying rental options that are both affordable and close enough to their primary daily destination. Generic property portals surface listings by location or price but do not account for commute time via public transport — the primary mode of travel for this demographic. This forces users to manually cross-reference listings against map apps, which is slow and error-prone.

---

## 3. Goals

- Help users filter rental listings by commute time from a chosen MRT station destination.
- Surface only listings within the user's rent budget and commute time cap.
- Rank results deterministically so the best options appear first.
- Provide a breakdown of transit vs. walking time for each shortlisted listing (V1.4).
- Deliver the product as a runnable offline JAR with a GUI.

### Non-Goals

- Live routing APIs (e.g., Google Maps, OneMap).
- Real-time rental scraping or live listing updates.
- Address geocoding or map rendering.
- User accounts, authentication, or cloud sync.
- Multi-modal routing beyond MRT + walking (V1 scope).

---

## 4. Target Users

### Primary Persona

**International student or newcomer working professional in Singapore.**

- Commutes mainly between home and a fixed primary destination (university campus or office).
- Goal is to minimize daily travel time, not to secure a specific postal code.
- Budget-conscious; typically looking for HDB rooms or small condo units.
- Unfamiliar with Singapore's neighbourhoods and transit network.

---

## 5. Product Roadmap

| Release | Milestone | Target |
|---------|-----------|--------|
| **V1.2** | First Feature Increment — destination + rent filter | Week 9 |
| **V1.3** | MVP — commute time cap + shortlist output | Week 10 |
| **V1.4** | Alpha — anti-walk filter + commute breakdown | Week 11 |

---

## 6. Features and User Stories

### V1.2 — First Feature Increment

#### US1 — Set Primary Destination
As a renter, I want to set a primary destination (e.g., an MRT station) so that listings can be evaluated by commute distance.

**Acceptance Criteria:**
- User can enter a destination via a dropdown or text field in the left input panel.
- System validates the input against a predefined static Time-Distance Matrix of stations/hubs.

#### US2 — Filter by Monthly Rent
As a renter, I want to set a maximum rent limit so that I only see affordable options.

**Acceptance Criteria:**
- System parses a bundled local static dataset (`listings.json` or `.csv`).
- Listings with a rent value higher than the user's limit are not processed.

---

### V1.3 — MVP

#### US3 — Set Commute Time Cap
As a renter, I want to filter listings by a maximum travel time limit so that I can manage my daily travel.

**Acceptance Criteria:**
- User can input a maximum travel time in minutes via the GUI.
- System calculates basic transit time using the pre-calculated matrix and excludes listings exceeding the cap.

#### US4 — Require Air-Conditioning
As a renter, I want to require air-conditioning so that unsuitable listings are removed.

**Acceptance Criteria:**
- User can toggle an "Air-Con Required" checkbox.
- When enabled, listings without the air-con attribute are excluded from the final list.

#### US5 — Generate GUI Output
As a renter, I want to see a clean output of the best matching listings in a display panel so that I can review my options.

**Acceptance Criteria:**
- System outputs the top N listings (default N=10) that pass all filters to the right display panel.
- Each listing card displays the rent, address, and commute summary.

---

### V1.4 — Alpha

#### US6 — Anti-Walk-Dominant Route Filter
As a renter, I want the system to reject routes that are primarily walking so that I receive realistic public transport suggestions.

**Acceptance Criteria:**
- System applies a configured walk-dominant threshold (default 0.6 of total commute time).
- Routes where the walking ratio (`walkMinutes / totalMinutes`) is greater than or equal to the configured threshold are rejected.

#### US7 — Commute Summary Breakdown
As a renter, I want to see the commute details split by transit and walking so that I understand the journey better.

**Acceptance Criteria:**
- The output for each shortlisted item specifies "Transit Time" and "Walking Time".

#### US8 — Set Persona Preset *(Stretch)*
As a renter, I want to select a preset (Student vs. Worker) so that default time caps and budgets are automatically applied.

**Acceptance Criteria:**
- Selecting 'Student' sets max rent and default commute caps automatically based on typical student budgets.
- User can manually override these default values in the left input panel.

---

## 7. Functional Requirements

### 7.1 Destination and Preference Input

| ID | Requirement |
|----|-------------|
| FR-01 | User can select a destination MRT station from a predefined list via a dropdown or text field. |
| FR-02 | User can set a maximum monthly rent (SGD integer). |
| FR-03 | User can set a maximum commute time in minutes. |
| FR-04 | User can toggle an "Air-Con Required" filter. |
| FR-05 | System validates all inputs before executing a search. Invalid destination station IDs return a user-friendly error. |

### 7.2 Search and Filtering

| ID | Requirement |
|----|-------------|
| FR-06 | System loads listings from a local static dataset on search. |
| FR-07 | System excludes listings with `monthlyRent > maxRent`. |
| FR-08 | System excludes listings without air-con when the aircon filter is enabled. |
| FR-09 | System computes commute time from each listing's nearest MRT station to the destination using Dijkstra shortest-path on the local transit graph. |
| FR-10 | System excludes listings where computed `totalMinutes > maxCommuteMinutes`. |

### 7.3 Ranking and Results Display

| ID | Requirement |
|----|-------------|
| FR-11 | Shortlisted listings are ranked deterministically: ascending commute time, then ascending rent, then `listingId` as tie-breaker. |
| FR-12 | Results panel displays the top N listings (default N=10) with rent, address, and commute summary per card. |
| FR-13 | User can click a listing to view full details including commute breakdown (V1.4). |

### 7.4 Commute Breakdown (V1.4)

| ID | Requirement |
|----|-------------|
| FR-14 | System provides transit time, walking time, number of transfers, and route stations for each listing. |
| FR-15 | System flags and rejects listings where the walking ratio (`walkMinutes / totalMinutes`) is greater than or equal to the configured walk-dominant threshold. |

### 7.5 Data Freshness Notice

| ID | Requirement |
|----|-------------|
| FR-16 | The UI displays a notice such as "Data accurate as of \<last-updated date\>" based on dataset metadata. |

---

## 8. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Application runs fully offline; no network calls are made at runtime. |
| NFR-02 | Application is delivered as a runnable JAR. |
| NFR-03 | GUI is required for all core user flows; no CLI-only mode. |
| NFR-04 | Search results must be returned in a time acceptable for interactive use (target: < 2 seconds for typical dataset sizes). |
| NFR-05 | Data files (JSON/CSV) are schema-validated on load; load errors are surfaced to the user with a clear message. |
| NFR-06 | Domain logic must reside in the Logic/Services layers; no business logic in the UI layer. |
| NFR-07 | Ranking must be deterministic — identical inputs always produce the same result ordering. |

---

## 9. Data Model Summary

| Entity | Key Fields |
|--------|------------|
| **Station** | `stationId`, `name`, `lines` |
| **Edge** | `fromStationId`, `toStationId`, `travelMinutes`, `line` |
| **TransitGraph** | Adjacency list: `Map<stationId, List<Edge>>` |
| **RentalListing** | `listingId`, `title`, `monthlyRent`, `hasAircon`, `nearestStationId`, `address`, `roomType`, `notes` |
| **UserPreferences** | `destinationStationId`, `maxRent`, `maxCommuteMinutes`, `requireAircon`, `transportMode` |
| **CommuteEstimate** | `totalMinutes`, `transitMinutes`, `walkMinutes`, `transfers`, `routeStations` |
| **SearchResult** | `listing`, `commute`, `score` |

All data is loaded from local files. The MVP transport mode defaults to MRT; walking is modelled minimally (V1.4).

---

## 10. Constraints and Assumptions

- Destination must be an MRT station from the finite predefined set.
- Each listing provides `nearestStationId`; no geocoding is performed.
- Commute times are approximations derived from transit graph edge weights.
- The application must be runnable as a JAR (Java desktop GUI).
- Data files must be bundled with the application or placed in a known local path.

---

## 11. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Local dataset incomplete or inconsistent | Empty or incorrect results | Schema validation on load; curated demo dataset; clear load error messages |
| Routing bugs in shortest-path algorithm | Wrong commute times shown | Unit tests with small, deterministic fixture graphs |
| GUI scope creep | Delivery delays | Minimal screen set: Search + Results + Details dialog |
| UI–Logic coupling | Integration pain | Strict interfaces + view models; no domain logic in UI |
| Performance with large listing datasets | Slow search | Cache shortest paths per destination; precompute station-to-destination distances |
| Ambiguous walk-dominant threshold | Feature disagreement | Define threshold (e.g., `walkMinutes / totalMinutes >= T`) in config; document in SDD |

---

## 12. Related Documents

- [User Stories](./user-stories.md)
- [MVP Scope](./scope-mvp.md)
- [Architecture Overview](../design/architecture.md)
- [Software Design Document](../design/sdd.md)
- [API Specification](../api/api-spec.md)
- [Mock API / Data Schemas](../api/mock-api.md)
- [Test Plan](../testing/test-plan.md)
