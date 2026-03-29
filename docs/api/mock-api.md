# Mock API / Local Data Schemas

**Smart Rental Search Algorithm**

The application uses local CSV datasets instead of live APIs at runtime. This document describes the offline data model and the development-time workflow that regenerates the commute matrix.

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
| `listingId` | String | Yes | Unique identifier (e.g., `L001`, `L002`) |
| `title` | String | Yes | Descriptive title for the property |
| `monthlyRent` | int | Yes | Monthly rent in SGD |
| `hasAircon` | boolean | Yes | Whether the listing has air conditioning |
| `originNodeId` | String | Yes | Origin node ID used to match this listing to the offline transit matrix (maps to `Flat_ID` in `Rental_List.csv` and may be shared by multiple listings at the same covered origin) |
| `address` | String | Yes | Real block and street name |
| `roomType` | String | Yes | Category of room (e.g., "Condo room", "HDB room", "Singleroom") |
| `sourcePlatform` | String | Yes | Source platform (e.g., `PropertyGuru`, `99.co`) |
| `notes` | String | Yes | Additional descriptive notes |

**Example (CSV):**

```csv
listingId,title,monthlyRent,hasAircon,originNodeId,address,roomType,sourcePlatform,notes
L001,City-fringe condo room in Jurong East,1850,true,R01,Blk 123 Jurong East Street 13,Condo room,PropertyGuru,Curated demo listing
L002,Quiet stay near Tiong Bahru,1800,true,R02,Blk 123 Tiong Bahru Road,Condo room,99.co,Near central amenities
```

**Example (JSON representation):**

```json
{
  "listingId": "L001",
  "title": "City-fringe condo room in Jurong East",
  "monthlyRent": 1850,
  "hasAircon": true,
  "originNodeId": "R01",
  "address": "Blk 123 Jurong East Street 13",
  "roomType": "Condo room",
  "sourcePlatform": "PropertyGuru",
  "notes": "Curated demo listing"
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
- Maintain a small but representative listings set, approximately 100 to 180 units across the supported destinations, which is sufficient for exercising destination coverage and commute-filter behavior without overwhelming test execution time
- Track source provenance for travel-time records and listing entries where possible

---

## Offline Commute Dataset

The repository-tracked commute dataset is stored as CSV files under `src/main/resources/commute_data/`.

### [`Rental_List.csv`](../../src/main/resources/commute_data/Rental_List.csv) (Input)

| Field | Type | Description |
|-------|------|-------------|
| `Flat_ID` | String | Unique identifier for the covered rental origin node, for example `R01` |
| `Postal_Code` | String | Six-digit Singapore postal code used for geocoding |
| `Region` | String | Broad Singapore region |
| `Area_Name` | String | Human-readable neighborhood label |

### [`Dst_List.csv`](../../src/main/resources/commute_data/Dst_List.csv) (Input)

| Field | Type | Description |
|-------|------|-------------|
| `ID` | String | Unique destination identifier, for example `D01` |
| `Category` | String | Destination type such as university, office, or healthcare |
| `Location Name` | String | Display label for the destination |
| `Postal Code` | String | Six-digit Singapore postal code used for geocoding |

### [`transit_matrix.csv`](../../src/main/resources/commute_data/transit_matrix.csv) (Generated Output)

| Column Name | Description |
|-------------|-------------|
| `flat_id` | Foreign key matching `Flat_ID` in `Rental_List.csv` |
| `destination_id` | Foreign key matching `ID` in `Dst_List.csv` |
| `pt_total` | Total public-transport journey time in minutes |
| `pt_walk` | Walking time within the public-transport journey |
| `pt_bus` | Minutes spent on bus legs |
| `pt_rail` | Minutes spent on MRT or LRT legs |
| `pt_transit` | Minutes spent inside moving transit vehicles |
| `pt_fare` | Estimated public-transport fare in SGD |
| `drive_total` | Total driving time in minutes |
| `cycle_total` | Total cycling time in minutes |
| `walk_total` | Total walking time in minutes |

The matrix format replaces the earlier station-edge graph assumption. Runtime lookup is keyed by rental origin and destination identifier instead of station adjacency.

---

## Data Generation Workflow

The generator is development-only tooling at [`scripts/generate_travel_data.py`](../../scripts/generate_travel_data.py). It is intentionally kept out of `src/main/resources` so it is not shipped as packaged application data.

1. Install Python 3 and `requests`.
2. Obtain a fresh OneMap token and export it as `ONEMAP_TOKEN`.
3. Run the generator from the repository root:

```bash
python scripts/generate_travel_data.py
```

The script reads the input CSVs, resolves postal codes through OneMap, and rewrites `transit_matrix.csv` with fresh commute data.

Detailed token setup steps are documented in the [Build and Run Guide](../ops/build-and-run.md).

---

## Data Freshness

Since the app uses local data only:

> Display a label such as *"Accurate as of 2025-01-15"*, where the date is derived from the dataset metadata and formatted as ISO 8601 (YYYY-MM-DD).

---

## Troubleshooting

- If the generator reports `ONEMAP_TOKEN environment variable is not set`, export a fresh token before running it.
- If OneMap returns `Unauthorized`, the token likely expired and should be regenerated.
- If the output contains `-1` timings, confirm the input postal codes are valid and rerun.
- If OneMap rate-limits the script, increase the configured delay and rerun.

---

## Related Documents

- [Software Design Document](../design/sdd.md)
- [Architecture Overview](../design/architecture.md)
- [API Spec](./api-spec.md)
- [Build and Run Guide](../ops/build-and-run.md)
