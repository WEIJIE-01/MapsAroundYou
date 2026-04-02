import csv
import random
import time
from pathlib import Path

import requests


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "main" / "resources" / "commute_data"
DEFAULT_INPUT_CSV = DATA_DIR / "origin_nodes.csv"
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


def get_real_address(postal_code, fallback_area, rng):
    """Fetch the base block and street name for an origin node."""
    url = (
        "https://www.onemap.gov.sg/api/common/elastic/search"
        f"?searchVal={postal_code}&returnGeom=N&getAddrDetails=Y"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        try:
            data = response.json()
        except ValueError:
            data = None

        if isinstance(data, dict):
            found = data.get("found", 0) or 0
            results = data.get("results") or []
            if found and isinstance(results, list) and results:
                result = results[0] or {}
                blk = (result.get("BLK_NO") or "").strip()
                road = (result.get("ROAD_NAME") or "").strip()
                blk_valid = bool(blk) and blk.upper() != "NIL"
                road_valid = bool(road) and road.upper() != "NIL"
                if blk_valid and road_valid:
                    return f"Blk {blk} {road.title()}"
                if blk_valid:
                    return f"Blk {blk}"
                if road_valid:
                    return road.title()
    except requests.exceptions.RequestException:
        pass

    return f"Blk {rng.randint(1, 200)} {fallback_area} Road"


def add_unit_suffix(base_address, unit_number):
    floor = 2 + (unit_number % 18)
    stack = 1 + ((unit_number * 3) % 20)
    return f"{base_address}, #{floor:02d}-{stack:02d}"


def listing_count_per_origin(origin_count, target_count):
    if origin_count <= 0:
        return []
    if target_count < origin_count:
        raise ValueError("target_count must be at least the number of origin rows")

    base_count = target_count // origin_count
    remainder = target_count % origin_count
    counts = [base_count] * origin_count
    for index in range(remainder):
        counts[index] += 1
    return counts


def price_for_profile(profile, rng):
    lower, upper = profile["rent_range"]
    return rng.randint(lower // 10, upper // 10) * 10


def build_listing(row, index, slot_index, address_cache, rng):
    flat_id = row["Flat_ID"]
    postal = str(row["Postal_Code"]).strip()
    area = row["Area_Name"].split(" / ")[0].strip()
    profile = LISTING_PROFILES[slot_index % len(LISTING_PROFILES)]
    room_type = rng.choice(profile["room_types"])
    adjective = rng.choice(TITLE_ADJECTIVES)
    base_address = address_cache.setdefault(
        flat_id,
        get_real_address(postal, area, rng),
    )

    return {
        "listingId": f"L{index:03d}",
        "title": f"{adjective} {room_type.lower()} in {area}",
        "monthlyRent": price_for_profile(profile, rng),
        "hasAircon": "true" if rng.random() < profile["aircon_probability"] else "false",
        "originNodeId": flat_id,
        "address": add_unit_suffix(base_address, slot_index + 1),
        "roomType": room_type,
        "sourcePlatform": rng.choice(SOURCE_PLATFORMS),
        "notes": rng.choice(profile["note_pool"]),
    }


def generate_merged_listings(
    input_csv=DEFAULT_INPUT_CSV,
    output_csv=DEFAULT_OUTPUT_CSV,
    target_count=DEFAULT_TARGET_COUNT,
    seed=DEFAULT_SEED,
):
    """
    Generate app-facing listings from the covered origin-node set.

    Each origin_node row represents one origin location, not one housing unit.
    Multiple listing rows may therefore share the same originNodeId.
    """
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
