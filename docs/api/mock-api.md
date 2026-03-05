# Mock API / Local Data Schemas

**Smart Rental Search Algorithm**

The application uses **local data files** (JSON/CSV) instead of live APIs. This document describes the data schemas and structures for mock/demo datasets.

---

## Data Sources

| Repository | File | Description |
|------------|------|-------------|
| `StationRepository` | stations file | MRT stations |
| `TransitGraphRepository` | edges file | Transit graph edges (station-to-station travel times) |
| `ListingRepository` | listings file | Rental listings |
| `UserPrefsRepository` | (optional) | Persisted user preferences |

---

## Schema Definitions

### Stations

| Field | Type | Description |
|-------|------|-------------|
| `stationId` | String | Unique identifier (e.g., MRT station code) |
| `name` | String | Display name |
| `lines` | List&lt;String&gt; | MRT lines (e.g., "NS", "EW"); values should be unique |

**Example (JSON):**

```json
{
  "stationId": "NS1",
  "name": "Jurong East",
  "lines": ["NS", "EW"]
}
```

### Edges (Transit Graph)

| Field | Type | Description |
|-------|------|-------------|
| `fromStationId` | String | Origin station |
| `toStationId` | String | Destination station |
| `travelMinutes` | int | Travel time in minutes |
| `line` | String | MRT line for this segment |

**Example (JSON):**

```json
{
  "fromStationId": "NS1",
  "toStationId": "NS2",
  "travelMinutes": 2,
  "line": "NS"
}
```

### TransitGraph

- Structure: `adj: Map<String, List<Edge>>`
- Adjacency list representation for Dijkstra shortest path

---

### Rental Listings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `listingId` | String | Yes | Unique identifier |
| `title` | String | Yes | Listing title |
| `monthlyRent` | int | Yes | Monthly rent (SGD) |
| `hasAircon` | boolean | Yes | Has air conditioning |
| `nearestStationId` | String | Yes | Closest MRT station |
| `address` | String | No | Full address |
| `roomType` | String | No | e.g., "HDB", "Condo" |
| `notes` | String | No | Additional notes |

**Example (JSON):**

```json
{
  "listingId": "L001",
  "title": "Cozy room near Jurong East",
  "monthlyRent": 1200,
  "hasAircon": true,
  "nearestStationId": "NS1",
  "address": "123 Jurong Street",
  "roomType": "HDB"
}
```

---

### User Preferences (Optional Persistence)

| Field | Type | Description |
|-------|------|-------------|
| `destinationStationId` | String | Primary destination MRT station |
| `maxRent` | int | Max monthly rent filter |
| `maxCommuteMinutes` | int | Max commute time (minutes) |
| `requireAircon` | boolean | Require aircon |
| `transportMode` | enum | MVP default: MRT |

---

## Validation Requirements

- Schema must be validated on load
- Invalid or missing fields should produce clear load errors
- Use a curated demo dataset for development and testing

---

## Data Freshness

Since the app uses local data only:

> Display a label such as *"Accurate as of 2025-01-15"*, where the date is derived from the dataset metadata and formatted as ISO 8601 (YYYY-MM-DD).

---

## Related Documents

- [Software Design Document](../design/sdd.md)
- [Architecture Overview](../design/architecture.md)
- [API Spec](./api-spec.md)
