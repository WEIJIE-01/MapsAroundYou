import csv
import random
import time
from pathlib import Path

import requests


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "main" / "resources" / "commute_data"
DEFAULT_INPUT_CSV = DATA_DIR / "Rental_List.csv"
DEFAULT_OUTPUT_CSV = DATA_DIR / "listings.csv"
DEFAULT_TARGET_COUNT = 180
DEFAULT_SEED = 2103
REQUEST_DELAY_SECONDS = 0.2

HEADERS = [
    "listingId",
    "title",
    "monthlyRent",
    "hasAircon",
    "originNodeId",
    "address",
    "roomType",
    "sourcePlatform",
    "notes",
]

LISTING_PROFILES = [
    {
        "room_types": ["Singleroom", "Shared room", "Common room"],
        "rent_range": (950, 1450),
        "aircon_probability": 0.68,
        "note_pool": [
            "Affordable option",
            "Good value option",
            "Student-friendly budget",
            "Convenient bus access",
        ],
    },
    {
        "room_types": ["HDB room", "Common room", "Private room"],
        "rent_range": (1350, 1900),
        "aircon_probability": 0.8,
        "note_pool": [
            "Curated demo listing",
            "Near central amenities",
            "Quiet neighborhood",
            "Walkable to town center",
        ],
    },
    {
        "room_types": ["Condo room", "Private room", "HDB room"],
        "rent_range": (1750, 2500),
        "aircon_probability": 0.92,
        "note_pool": [
            "Premium central option",
            "Higher rent but newer estate",
            "Good city access",
            "Popular for east workers",
        ],
    },
    {
        "room_types": ["Shared room", "Common room", "Singleroom"],
        "rent_range": (1100, 1700),
        "aircon_probability": 0.74,
        "note_pool": [
            "Simple central listing",
            "Popular with interns",
            "Practical weekday commute",
            "Balanced price and access",
        ],
    },
]

TITLE_ADJECTIVES = [
    "City-fringe",
    "Quiet stay near",
    "Budget",
    "Studio-style",
    "Central",
    "Premium",
    "Breezy",
    "Cozy",
    "Spacious",
    "Well-connected",
    "Accessible",
    "Modern",
]

SOURCE_PLATFORMS = ["PropertyGuru", "99.co", "SRX", "PropertyLimBrothers"]

# Rail share model for PT allocation:
# - Base rail share starts at 25% for short-to-mid trips where buses still dominate first/last mile.
# - Rail share ramps with distance because MRT/LRT usage grows on longer cross-town routes.
# - Rail share is capped at 80% (0.25 + 0.55) to leave a realistic residual bus portion.
RAIL_SHARE_BASE = 0.25
RAIL_SHARE_DISTANCE_CAP = 0.55
RAIL_SHARE_RAMP_DISTANCE_KM = 25.0

# PT fare model for offline simulation:
# - Base fare starts at 1.09 SGD for short transit trips.
# - Base fare distance threshold is 3.2 km.
# - Beyond that threshold, fare grows linearly at 0.045 SGD per km.
# These values are simplified Singapore-style fare heuristics (not official fare tables).
FARE_BASE_SGD = 1.09
FARE_BASE_DISTANCE_KM = 3.2
FARE_INCREMENT_PER_KM_SGD = 0.045

LISTING_PROFILES = [
    {
        "housing": "HDB",
        "room_types": ["Common room", "HDB room", "Shared room", "Singleroom"],
        "rent_range": (900, 1650),
        "aircon_probability": 0.72,
        "notes": ["Affordable option", "Student-friendly budget", "Practical commute"],
    },
    {
        "housing": "Condo",
        "room_types": ["Condo room", "Private room"],
        "rent_range": (1650, 2800),
        "aircon_probability": 0.93,
        "notes": ["Premium central option", "Newer estate", "Good city access"],
    },
]

# Sector-specific suffix ranges. Values represent the last 4 digits in SSxxxx
# and ensure generated postcodes follow sector trends like 520001-529999.
POSTAL_SUFFIX_RANGE_BY_PREFIX = {
    "12": (1, 9999),
    "15": (1, 9999),
    "31": (1, 9999),
    "33": (1, 9999),
    "46": (1, 9999),
    "51": (1, 9999),
    "52": (1, 9999),
    "53": (1, 9999),
    "54": (1, 9999),
    "56": (1, 9999),
    "60": (1, 9999),
    "64": (1, 9999),
    "65": (1, 9999),
    "68": (1, 9999),
    "73": (1, 9999),
    "75": (1, 9999),
    "76": (1, 9999),
    "82": (1, 9999),
}

AREA_CATALOG = [
    {"region": "Central", "area": "Bukit Merah", "street": "Jalan Bukit Merah", "postal_prefix": "15"},
    {"region": "Central", "area": "Toa Payoh", "street": "Lorong 7 Toa Payoh", "postal_prefix": "31"},
    {"region": "Central", "area": "Kallang", "street": "Boon Keng Road", "postal_prefix": "33"},
    {"region": "East", "area": "Bedok North", "street": "Bedok North Street 3", "postal_prefix": "46"},
    {"region": "East", "area": "Tampines", "street": "Tampines Street 21", "postal_prefix": "52"},
    {"region": "East", "area": "Pasir Ris", "street": "Pasir Ris Drive 6", "postal_prefix": "51"},
    {"region": "North", "area": "Woodlands", "street": "Woodlands Street 13", "postal_prefix": "73"},
    {"region": "North", "area": "Yishun", "street": "Yishun Avenue 5", "postal_prefix": "76"},
    {"region": "North", "area": "Sembawang", "street": "Wellington Circle", "postal_prefix": "75"},
    {"region": "North-East", "area": "Ang Mo Kio", "street": "Ang Mo Kio Avenue 3", "postal_prefix": "56"},
    {"region": "North-East", "area": "Hougang", "street": "Hougang Avenue 3", "postal_prefix": "53"},
    {"region": "North-East", "area": "Punggol", "street": "Punggol Field", "postal_prefix": "82"},
    {"region": "North-East", "area": "Sengkang", "street": "Rivervale Walk", "postal_prefix": "54"},
    {"region": "West", "area": "Jurong East", "street": "Jurong East Street 13", "postal_prefix": "60"},
    {"region": "West", "area": "Jurong West", "street": "Boon Lay Place", "postal_prefix": "64"},
    {"region": "West", "area": "Clementi", "street": "Clementi Avenue 5", "postal_prefix": "12"},
    {"region": "West", "area": "Bukit Batok", "street": "Bukit Batok West Avenue 8", "postal_prefix": "65"},
    {"region": "West", "area": "Choa Chu Kang", "street": "Choa Chu Kang Avenue 4", "postal_prefix": "68"},
]

# Approximate Singapore postal sector centroids (lat, lon).
SECTOR_COORDS = {
    "01": (1.2850, 103.8490),
    "11": (1.3170, 103.8460),
    "12": (1.3150, 103.7650),
    "14": (1.2890, 103.8040),
    "15": (1.2830, 103.8240),
    "16": (1.2860, 103.8180),
    "18": (1.2820, 103.8540),
    "20": (1.3050, 103.8580),
    "23": (1.3040, 103.8320),
    "30": (1.3320, 103.8480),
    "31": (1.3360, 103.8510),
    "33": (1.3140, 103.8630),
    "40": (1.3190, 103.8940),
    "42": (1.3030, 103.9050),
    "46": (1.3340, 103.9360),
    "48": (1.3350, 103.9570),
    "51": (1.3730, 103.9480),
    "52": (1.3530, 103.9440),
    "53": (1.3670, 103.8920),
    "54": (1.3900, 103.8950),
    "55": (1.3690, 103.8730),
    "56": (1.3700, 103.8470),
    "60": (1.3330, 103.7420),
    "63": (1.3470, 103.6830),
    "64": (1.3460, 103.7060),
    "65": (1.3500, 103.7510),
    "68": (1.3780, 103.7420),
    "73": (1.4370, 103.7800),
    "75": (1.4510, 103.8180),
    "76": (1.4310, 103.8350),
    "82": (1.4050, 103.9050),
}


@dataclass
class OriginLocation:
    """Origin location model used for appending rental/listing/transit rows.

    Input: values from random generation or manual user input.
    Returns: structured origin metadata used by row builders.
    """

    flat_id: str
    postal_code: str
    region: str
    area_name: str
    street_name: str
    housing_hint: str


def parse_max_numeric_id(values: list[str], prefix: str) -> int:
    """Return the largest numeric suffix for IDs that match a prefix.

    Input: list of IDs and expected prefix (for example, "R" or "L").
    Returns: maximum numeric part found, or 0 when none is valid.
    """
    max_value = 0
    for value in values:
        text = (value or "").strip()
        if not text.startswith(prefix):
            continue
        numeric = text[len(prefix) :]
        if numeric.isdigit():
            max_value = max(max_value, int(numeric))
    return max_value


def deterministic_fraction(seed_text: str) -> float:
    """Create a deterministic [0, 1) fraction from text.

    Input: any stable text key.
    Returns: pseudo-random fraction for deterministic jitter.
    """
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big") / float(2**64)


def postal_to_coord(postal_code: str) -> tuple[float, float]:
    """Map a Singapore-like postal code to approximate coordinates.

    Input: 6-digit postal code string.
    Returns: (latitude, longitude) in Singapore bounds.
    """
    clean = (postal_code or "").strip()
    sector = clean[:2] if len(clean) >= 2 else "31"
    base_lat, base_lon = SECTOR_COORDS.get(sector, (1.3521, 103.8198))
    lat_jitter = (deterministic_fraction(clean + "lat") - 0.5) * 0.018
    lon_jitter = (deterministic_fraction(clean + "lon") - 0.5) * 0.02
    return base_lat + lat_jitter, base_lon + lon_jitter


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Compute great-circle distance in kilometers.

    Input: two coordinates as (lat, lon).
    Returns: distance in kilometers.
    """
    lat1, lon1 = a
    lat2, lon2 = b
    radius = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    part = (
        math.sin(d_lat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(d_lon / 2) ** 2
    )
    return radius * (2 * math.atan2(math.sqrt(part), math.sqrt(1 - part)))


def estimate_transit_metrics(distance_km: float, rng: random.Random) -> dict[str, int | float]:
    """Estimate logical commute metrics without calling external APIs.

    Input: straight-line distance in kilometers and random generator.
    Returns: transit and modal durations, plus estimated fare.
    """
    # Use a 1.3x multiplier to approximate real-world network distance (indirect routes,
    # turns, and access paths) from straight-line distance, and clamp to a minimum of
    # 0.15 km so that extremely short or co-located trips still produce non-zero
    # durations and fares in downstream calculations.
    effective_km = max(0.15, distance_km * 1.3)

    # Singapore urban walking speed accounting for traffic signals and pedestrian infrastructure
    WALKING_SPEED_KM_H = 4.8
    # Average Singapore MRT/bus speed including stops and transfers
    TRANSIT_SPEED_KM_H = 24.0
    # Average cycling speed in Singapore
    CYCLING_SPEED_KM_H = 14.0
    # Average driving speed in Singapore
    DRIVING_SPEED_KM_H = 28.0

    walk_total = max(3, int(round((effective_km / WALKING_SPEED_KM_H) * 60)))
    cycle_total = max(4, int(round((effective_km / CYCLING_SPEED_KM_H) * 60 + rng.uniform(0, 3))))
    drive_total = max(4, int(round((effective_km / DRIVING_SPEED_KM_H) * 60 + rng.uniform(3, 8))))

    if effective_km <= 0.5:
        pt_walk = walk_total
        pt_bus = 0
        pt_rail = 0
        pt_transit = 0
        pt_total = walk_total
    elif effective_km <= 2.0:
        pt_walk = max(6, int(round((effective_km / 4.8) * 60 * 0.55)) + rng.randint(1, 3))
        pt_bus = max(4, int(round((effective_km / 18.0) * 60)) + rng.randint(1, 4))
        pt_rail = 0
        pt_transit = pt_bus
        pt_total = pt_walk + pt_transit + rng.randint(2, 5)
    else:
        pt_walk = max(6, min(20, int(round((effective_km / 4.8) * 60 * 0.35)) + rng.randint(2, 6)))
        pt_transit = max(8, int(round((effective_km / 24.0) * 60)) + rng.randint(4, 10))
        rail_share = RAIL_SHARE_BASE + min(
            RAIL_SHARE_DISTANCE_CAP,
            effective_km / RAIL_SHARE_RAMP_DISTANCE_KM,
        )
        pt_rail = int(round(pt_transit * rail_share))
        pt_bus = max(0, pt_transit - pt_rail)
        pt_total = pt_walk + pt_transit + rng.randint(4, 10)

    fare = estimate_fare(effective_km, pt_transit)
    return {
        "pt_total": pt_total,
        "pt_walk": pt_walk,
        "pt_bus": pt_bus,
        "pt_rail": pt_rail,
        "pt_transit": pt_transit,
        "pt_fare": fare,
        "drive_total": drive_total,
        "cycle_total": cycle_total,
        "walk_total": walk_total,
    }


def estimate_fare(distance_km: float, pt_transit: int) -> float:
    """Estimate MRT/bus fare based on distance brackets.

    Input: effective travel distance and transit minutes.
    Returns: fare in SGD rounded to 2 decimals.
    """
    if pt_transit <= 0:
        return 0.0
    if distance_km <= FARE_BASE_DISTANCE_KM:
        return FARE_BASE_SGD
    return round(
        FARE_BASE_SGD
        + (distance_km - FARE_BASE_DISTANCE_KM) * FARE_INCREMENT_PER_KM_SGD,
        2,
    )


def ensure_file_has_header(file_path: Path, headers: list[str]) -> None:
    """Create CSV file with header if it does not exist.

    Input: output path and ordered header fields.
    Returns: None.
    """
    if file_path.exists():
        return
    with file_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)


def read_csv_rows(file_path: Path) -> list[dict[str, str]]:
    """Read all rows from a CSV file.

    Input: CSV file path.
    Returns: list of dictionary rows.
    """
    if not file_path.exists():
        return []
    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def append_dict_rows(file_path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    """Append dictionary rows to CSV.

    Input: target path, fieldnames, and rows.
    Returns: None.
    """
    if not rows:
        return
    with file_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writerows(rows)


def next_origin_id(existing_rows: list[dict[str, str]]) -> int:
    """Get next origin numeric ID.

    Input: current Rental_List rows.
    Returns: next numeric suffix after max Flat_ID.
    """
    max_existing = parse_max_numeric_id([row.get("Flat_ID", "") for row in existing_rows], "R")
    return max_existing + 1


def next_listing_id(existing_rows: list[dict[str, str]]) -> int:
    """Get next listing numeric ID.

    Input: current listings rows.
    Returns: next numeric suffix after max listingId.
    """
    max_existing = parse_max_numeric_id([row.get("listingId", "") for row in existing_rows], "L")
    return max_existing + 1


def build_postal_code(prefix: str, rng: random.Random) -> str:
    """Build a 6-digit Singapore-like postal code.

    Input: 2-digit postal sector prefix and random generator.
    Returns: 6-digit postal code string.
    """
    normalized_prefix = prefix.strip().zfill(2)[:2]
    suffix_start, suffix_end = POSTAL_SUFFIX_RANGE_BY_PREFIX.get(
        normalized_prefix,
        (1, 9999),
    )
    suffix = rng.randint(suffix_start, suffix_end)
    return f"{normalized_prefix}{suffix:04d}"


def build_random_origins(
    count: int,
    start_index: int,
    rng: random.Random,
) -> list[OriginLocation]:
    """Generate random but logical Singapore origin locations.

    Input: origin count, starting Flat_ID number, and RNG.
    Returns: list of OriginLocation records.
    """
    origins: list[OriginLocation] = []

    # Reflects approximate Singapore private housing proportion in rental market
    CONDO_PROBABILITY = 0.28

    for idx in range(count):
        area = rng.choice(AREA_CATALOG)
        flat_num = start_index + idx
        flat_id = f"R{flat_num:02d}"
        postal_code = build_postal_code(area["postal_prefix"], rng)
        housing_hint = "Condo" if rng.random() < CONDO_PROBABILITY else "HDB"
        origins.append(
            OriginLocation(
                flat_id=flat_id,
                postal_code=postal_code,
                region=area["region"],
                area_name=area["area"],
                street_name=area["street"],
                housing_hint=housing_hint,
            )
        )
    return origins


def prompt_manual_origins(start_index: int) -> list[OriginLocation]:
    """Interactively collect user-specified origin locations.

    Input: starting Flat_ID number.
    Returns: list of OriginLocation records from terminal input.
    """
    while True:
        raw_count = input("How many locations do you want to add? ").strip()
        if raw_count.isdigit() and int(raw_count) > 0:
            count = int(raw_count)
            break
        print("Please enter a positive integer.")

    print("Enter values for each location. Example region: Central, East, North, North-East, West")
    origins: list[OriginLocation] = []
    for i in range(count):
        flat_id = f"R{start_index + i:02d}"
        print(f"\nLocation {i + 1} ({flat_id})")
        region = input("Region: ").strip() or "Central"
        area_name = input("Area_Name: ").strip() or "Unknown Area"
        street = input("Street name (for listings address): ").strip() or f"{area_name} Road"
        postal_code = input("Postal_Code (6 digits): ").strip()
        while not (postal_code.isdigit() and len(postal_code) == 6):
            postal_code = input("Postal_Code must be 6 digits. Re-enter: ").strip()
        raw_housing = input("Housing hint [HDB/Condo] (default HDB): ")
        housing_normalized = raw_housing.strip().upper()
        housing = housing_normalized if housing_normalized in {"HDB", "CONDO"} else "HDB"

        origins.append(
            OriginLocation(
                flat_id=flat_id,
                postal_code=postal_code,
                region=region,
                area_name=area_name,
                street_name=street,
                housing_hint=housing,
            )
        )
    return origins


def build_rental_rows(origins: list[OriginLocation]) -> list[dict[str, object]]:
    """Convert origin records into Rental_List CSV rows.

    Input: origin records.
    Returns: list of rows for Rental_List.csv append.
    """
    return [
        {
            "Flat_ID": item.flat_id,
            "Postal_Code": item.postal_code,
            "Region": item.region,
            "Area_Name": item.area_name,
        }
        for item in origins
    ]


def listing_profile_for_origin(origin: OriginLocation, rng: random.Random) -> dict[str, object]:
    """Pick listing profile biased by housing hint.

    Input: origin metadata and RNG.
    Returns: listing profile dictionary.
    """
    if origin.housing_hint == "Condo":
        return LISTING_PROFILES[1]
    if origin.housing_hint == "HDB":
        return LISTING_PROFILES[0]
    return rng.choice(LISTING_PROFILES)


def build_listing_rows(
    origins: list[OriginLocation],
    listings_per_origin: int,
    start_listing_index: int,
    rng: random.Random,
) -> list[dict[str, object]]:
    """Build app-facing listing rows for each new origin.

    Input: origin records, listings count per origin, start listing ID, RNG.
    Returns: list of listing rows for append.
    """
    rows: list[dict[str, object]] = []
    listing_idx = start_listing_index
    for origin in origins:
        block = rng.randint(1, 999)
        for slot in range(listings_per_origin):
            profile = listing_profile_for_origin(origin, rng)
            room_type = rng.choice(profile["room_types"])
            adjective = rng.choice(TITLE_ADJECTIVES)
            lower, upper = profile["rent_range"]
            monthly_rent = rng.randint(lower // 10, upper // 10) * 10
            floor = rng.randint(2, 25)
            stack = rng.randint(1, 40)
            rows.append(
                {
                    "listingId": f"L{listing_idx:03d}",
                    "title": f"{adjective} {room_type.lower()} in {origin.area_name}",
                    "monthlyRent": monthly_rent,
                    "hasAircon": "true" if rng.random() < profile["aircon_probability"] else "false",
                    "originNodeId": origin.flat_id,
                    "address": f"Blk {block} {origin.street_name}, #{floor:02d}-{stack:02d}",
                    "roomType": room_type,
                    "sourcePlatform": rng.choice(SOURCE_PLATFORMS),
                    "notes": rng.choice(profile["notes"]),
                }
            )
            listing_idx += 1
    return rows


def destination_coord_map() -> dict[str, tuple[float, float]]:
    """Load destination IDs and derive deterministic coordinates from postal codes.

    Input: none.
    Returns: map of destination ID to coordinate tuple.
    """
    rows = read_csv_rows(DEST_FILE)
    mapping: dict[str, tuple[float, float]] = {}
    for row in rows:
        destination_id = (row.get("ID") or "").strip()
        postal_code = (row.get("Postal Code") or "").strip()
        if destination_id and postal_code:
            mapping[destination_id] = postal_to_coord(postal_code)
    return mapping


def build_transit_rows(
    origins: list[OriginLocation],
    existing_transit_rows: list[dict[str, str]],
    rng: random.Random,
) -> list[dict[str, object]]:
    """Build transit matrix rows for new origins against all destinations.

    Input: new origins, existing matrix rows, and RNG.
    Returns: list of new transit rows to append.
    """
    destinations = destination_coord_map()
    existing_pairs = {
        ((row.get("flat_id") or "").strip(), (row.get("destination_id") or "").strip())
        for row in existing_transit_rows
    }

    rows: list[dict[str, object]] = []
    for origin in origins:
        origin_coord = postal_to_coord(origin.postal_code)
        for destination_id, destination_coord in destinations.items():
            key = (origin.flat_id, destination_id)
            if key in existing_pairs:
                continue
            distance_km = haversine_km(origin_coord, destination_coord)
            metrics = estimate_transit_metrics(distance_km, rng)
            rows.append(
                {
                    "flat_id": origin.flat_id,
                    "destination_id": destination_id,
                    **metrics,
                }
            )
    return rows


def run_generation_pipeline(
    location_mode: str,
    new_origin_count: int,
    listings_per_origin: int,
    seed: int,
) -> None:
    """Append new rows into Rental_List, listings, and transit matrix.

    Input: location mode, number of new origins, listings per origin, and random seed.
    Returns: None.
    """
    ensure_file_has_header(RENTAL_FILE, RENTAL_HEADERS)
    ensure_file_has_header(LISTINGS_FILE, LISTING_HEADERS)
    ensure_file_has_header(TRANSIT_FILE, TRANSIT_HEADERS)

    rng = random.Random(seed)

    try:
        with Path(input_csv).open(mode="r", encoding="utf-8-sig") as infile:
            origin_rows = list(csv.DictReader(infile))

        counts = listing_count_per_origin(len(origin_rows), target_count)
        address_cache = {}
        print(
            f"Reading from {input_csv} and generating {target_count} listings "
            f"across {len(origin_rows)} covered origin nodes..."
        )

        with Path(output_csv).open(mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=HEADERS)
            writer.writeheader()

            listing_index = 1
            for row, listing_count in zip(origin_rows, counts):
                print(
                    f"  Generating {listing_count} listings for "
                    f"{row['Flat_ID']} (Postal: {row['Postal_Code']})..."
                )
                for slot_index in range(listing_count):
                    writer.writerow(
                        build_listing(
                            row=row,
                            index=listing_index,
                            slot_index=slot_index,
                            address_cache=address_cache,
                            rng=rng,
                        )
                    )
                    listing_index += 1
                time.sleep(REQUEST_DELAY_SECONDS)

        print(
            f"\nSuccess! Generated '{output_csv}' with {target_count} "
            "app-facing listing rows."
        )
    except FileNotFoundError:
        print(f"[!] Error: Could not find '{input_csv}'. Please verify the path or pass --input.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Generate app-facing listings.csv rows from Rental_List.csv. "
            "Defaults to 180 listings across the covered origin set."
        )
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_CSV),
        help="Input rental CSV path (default: repo-relative Rental_List.csv).",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_CSV),
        help="Output CSV path (default: repo-relative listings.csv).",
    )
    parser.add_argument(
        "--target-count",
        type=int,
        default=DEFAULT_TARGET_COUNT,
        help="Total number of listing rows to generate across the origin set.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Deterministic random seed for reproducible demo datasets.",
    )
    args = parser.parse_args()

    generate_merged_listings(args.input, args.output, args.target_count, args.seed)
