# Data Generation Guide

This guide explains how to add new rental listings to MapsAroundYou using the data generation workflow.

## Workflow Overview

The application maintains a two-layer CSV data model:

1. **`Rental_List.csv`** - Origin identity and commute reference
   - Source file that defines where rentals are located
   - Used as reference data for listings and transit matrix alignment
   - Treat each row as one covered origin node, not one app listing row
   - Columns: `Flat_ID`, `Postal_Code`, `Region`, `Area_Name`

2. **`listings.csv`** - App-facing listing data
   - Auto-generated from `Rental_List.csv` using the data generation script
   - Contains all fields needed by the CLI app for display and filtering
   - Multiple listing rows may share the same `originNodeId`
   - Columns: `listingId`, `title`, `monthlyRent`, `hasAircon`, `originNodeId`, `address`, `roomType`, `sourcePlatform`, `notes`

3. **`transit_matrix.csv`** - Commute lookup matrix
   - Pre-computed travel times from each origin to destinations
   - Aligned with `Rental_List.csv` via `flat_id` foreign key
   - Columns: `flat_id`, `destination_id`, `pt_total`, `pt_walk`, `pt_bus`, ... (and other transit metrics)

## Adding New Listings

### Prerequisites

- Python 3 on `PATH`
- `requests` installed locally:

```bash
pip install requests
```

- OneMap access if you want live address enrichment during generation
- See [Build and Run Guide](../ops/build-and-run.md) for the broader local setup
### Step 1: Add Origins to `Rental_List.csv`

Open `src/main/resources/commute_data/Rental_List.csv` and add new rows:

```csv
Flat_ID,Postal_Code,Region,Area_Name
R05,200150,East,Bedok / Near Bedok MRT
R06,200160,East,Bedok / Opposite Shopping Mall
```

**Important:** The `Flat_ID` column in `Rental_List.csv` becomes the `originNodeId` in `listings.csv`.

### Step 2: Generate App-Facing Listings

Run the data generation script from the workspace root:

```bash
python scripts/generate_merged_listings.py
```

This will:
- Read your newly added rows from `Rental_List.csv`
- Fetch real addresses from OneMap API (based on postal codes)
- Generate realistic rent prices based on room type
- Create multiple listing rows per covered origin node
- Produce a stronger demo dataset of 180 app-facing listings by default

**Optional arguments:**

```bash
# Custom input/output paths
python scripts/generate_merged_listings.py --input path/to/custom_rental.csv --output path/to/custom_listings.csv

# Override the listing count or deterministic seed
python scripts/generate_merged_listings.py --target-count 180 --seed 2103
```

### Step 3: Expand `transit_matrix.csv`

For each new `Flat_ID` added, you must add corresponding rows to `transit_matrix.csv`:

```csv
flat_id,destination_id,pt_total,pt_walk,pt_bus,pt_rail,pt_transit,pt_fare,drive_total,cycle_total,walk_total
R05,D01,35,8,20,0,20,1.80,15,50,75
R05,D02,60,15,18,20,38,2.40,30,160,220
R05,D03,30,5,10,8,18,1.75,13,60,70
...
```

**Important:** The `flat_id` values in `transit_matrix.csv` MUST match the `Flat_ID` values in `Rental_List.csv`.

## Data Format Details

### CSV Field Mappings

| Rental_List | → | listings.csv |
|---|---|---|
| `Flat_ID` | → | `originNodeId` |
| (generated) | → | `listingId` (L001, L002, ...) |
| (generated) | → | `title` (descriptive, auto-generated) |
| `Postal_Code` | → | `address` (fetched from OneMap API) |
| (generated) | → | `monthlyRent` (random, price-bracket appropriate) |
| (generated) | → | `hasAircon` (boolean: 75% true, 25% false) |
| (generated) | → | `roomType` (e.g., "Condo room", "HDB room") |
| (generated) | → | `sourcePlatform` ("PropertyGuru" or "99.co") |
| (generated) | → | `notes` (e.g., "Curated demo listing") |

### hasAircon Field

- **Type:** Boolean CSV value (`true` / `false`)
- **NOT a nested JSON field** (unlike earlier designs)
- **Direct column in listings.csv** for simple filtering

### One Origin, Multiple Units

- `Rental_List.csv` tracks covered commute origins, not the final unit inventory
- The generator can therefore emit multiple listings for the same `originNodeId`
- This lets the demo app show richer filter results without regenerating the commute matrix

## Troubleshooting

### API Rate Limiting
If you see timeout errors from OneMap API:
- The script includes a polite 0.2s delay between requests
- Consider running in batches (add 10-20 listings at a time)

### Address Not Found
Some postal codes may not be found in OneMap. The script falls back to:
```
Blk [random 1-200] [Area_Name] Road
```

### CSV Encoding Issues
The script handles UTF-8 BOM encoding automatically using `encoding='utf-8-sig'`.

## Key Design Principles

- **No Rental_List2.csv at runtime** - The intermediate file from data generation is not used by the app
- **Two-layer decoupling** - `Rental_List.csv` (identity) stays separate from `listings.csv` (presentation)
- **Repo-portable** - All paths are relative to the repository root
- **Flat_ID alignment** - All three CSVs reference listings by their origin `Flat_ID` (or `originNodeId`)

## See Also

- [API Schema Documentation](../api/mock-api.md) - Full schema details
- [Build and Run Guide](../ops/build-and-run.md) - How to run the CLI application
