# Mock API / Local Data Schemas

**Smart Rental Search Algorithm**

The application uses **local data files** (JSON/CSV) instead of live APIs. This document describes the data schemas and structures for mock/demo datasets.

---

## Data Sources

| Repository | File | Description |
|------------|------|-------------|
| `DestinationRepository` | destinations file | Supported destinations such as campuses, offices, hospitals, or places |
| `TravelTimeRepository` | travel-times file | Precomputed travel times between listing origin nodes and destinations |
| `ListingRepository` | listings file | Curated rental or housing listings |
| `UserPrefsRepository` | (optional) | Persisted user preferences |

---

## Schema Definitions

### Destinations

| Field | Type | Description |
|-------|------|-------------|
| `destinationId` | String | Unique identifier |
| `name` | String | Display name |
| `category` | String | Destination type, e.g. `university`, `hospital`, `office`, `shopping` |
| `area` | String | Broad area or district for display |

**Example (JSON):**

```json
{
  "destinationId": "DEST-NUS",
  "name": "National University of Singapore",
  "category": "university",
  "area": "Kent Ridge"
}
```

### Travel Time Records

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `originNodeId` | String | Yes | Listing-side lookup node used for commute estimation |
| `destinationId` | String | Yes | Supported destination identifier |
| `totalMinutes` | int | Yes | End-to-end travel time in minutes |
| `transitMinutes` | int | No | Transit portion of the trip |
| `walkMinutes` | int | No | Walking portion of the trip |
| `transfers` | int | No | Number of transfers |
| `source` | String | No | Provenance, e.g. `LTA`, manual estimate |

**Example (JSON):**

```json
{
  "originNodeId": "ORIGIN-CLEMENTI-AVE-3",
  "destinationId": "DEST-NUS",
  "totalMinutes": 28,
  "transitMinutes": 22,
  "walkMinutes": 6,
  "transfers": 1,
  "source": "LTA"
}
```

### Travel Time Lookup

- Structure: keyed lookup such as `Map<originNodeId, Map<destinationId, TravelTimeRecord>>`
- Precomputed local matrix representation for fast commute lookup during search

---

### Rental Listings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `listingId` | String | Yes | Unique identifier |
| `title` | String | Yes | Listing title |
| `monthlyRent` | int | Yes | Monthly rent (SGD) |
| `hasAircon` | boolean | Yes | Has air conditioning |
| `originNodeId` | String | Yes | Lookup node used to match this listing to the travel-time matrix |
| `address` | String | No | Full address |
| `roomType` | String | No | e.g., "HDB", "Condo" |
| `sourcePlatform` | String | No | Source site, e.g. `PropertyGuru`, `99.co` |
| `destinationTags` | List&lt;String&gt; | No | Optional tags indicating which destinations this listing set was curated around |
| `notes` | String | No | Additional notes |

**Example (JSON):**

```json
{
  "listingId": "L001",
  "title": "Cozy room near Jurong East",
  "monthlyRent": 1200,
  "hasAircon": true,
  "originNodeId": "ORIGIN-CLEMENTI-AVE-3",
  "address": "123 Jurong Street",
  "roomType": "HDB",
  "sourcePlatform": "PropertyGuru",
  "destinationTags": ["DEST-NUS"]
}
```

---

### User Preferences (Optional Persistence)

| Field | Type | Description |
|-------|------|-------------|
| `destinationId` | String | Primary destination from the supported destination list |
| `maxRent` | int | Max monthly rent filter |
| `maxCommuteMinutes` | int | Max commute time (minutes) |
| `requireAircon` | boolean | Require aircon |
| `transportMode` | enum | MVP default: public transport |

---

## Validation Requirements

- Schema must be validated on load
- Invalid or missing fields should produce clear load errors
- Use a curated demo dataset for development and testing
- Maintain a small but representative listings set, approximately 20 to 50 units across the supported destinations
- Track source provenance for travel-time records and listing entries where possible

---

## Data Freshness

Since the app uses local data only:

> Display a label such as *"Accurate as of 2025-01-15"*, where the date is derived from the dataset metadata and formatted as ISO 8601 (YYYY-MM-DD).

---

## Related Documents

- [Software Design Document](../design/sdd.md)
- [Architecture Overview](../design/architecture.md)
- [API Spec](./api-spec.md)
