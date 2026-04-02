import csv
import os
import time
import argparse
from pathlib import Path

import requests


ONEMAP_TOKEN = os.getenv("ONEMAP_TOKEN")
HEADERS = {"Authorization": ONEMAP_TOKEN} if ONEMAP_TOKEN else {}
RATE_LIMIT_DELAY = 0.2
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "main" / "resources" / "commute_data"
DEST_FILE = DATA_DIR / "Dst_List.csv"
ORIGIN_NODES_FILE = DATA_DIR / "origin_nodes.csv"
OUTPUT_CSV = DATA_DIR / "transit_matrix.csv"
last_request_time = 0.0


def configure_auth_headers(token: str | None = None) -> None:
    """Configure auth headers and fail only when execution actually needs them."""
    selected_token = token or os.getenv("ONEMAP_TOKEN")
    if not selected_token:
        raise RuntimeError(
            "ONEMAP_TOKEN environment variable is not set. "
            "Generate a fresh token and export it before running this script."
        )

    global HEADERS
    HEADERS = {"Authorization": selected_token}


def enforce_rate_limit():
    global last_request_time
    current_time = time.time()
    time_since_last_request = current_time - last_request_time

    if time_since_last_request < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - time_since_last_request)

    last_request_time = time.time()


def get_coordinates(postal_code):
    url = (
        "https://www.onemap.gov.sg/api/common/elastic/search"
        f"?searchVal={postal_code}&returnGeom=Y&getAddrDetails=Y"
    )

    while True:
        enforce_rate_limit()
        response = requests.get(url, timeout=30)

        if response.status_code == 429 or "Too Many Requests" in response.text:
            print("  [!] Rate limit hit (Search API). Cooling down for 5 seconds...")
            time.sleep(5)
            continue

        if response.status_code == 200:
            data = response.json()
            if data["found"] > 0:
                lat = data["results"][0]["LATITUDE"]
                lon = data["results"][0]["LONGITUDE"]
                return f"{lat},{lon}"
        return None


def get_pt_route(start_coords, end_coords, date="03-09-2026", time_str="08:00:00"):
    url = "https://www.onemap.gov.sg/api/public/routingsvc/route"
    params = {
        "start": start_coords,
        "end": end_coords,
        "routeType": "pt",
        "date": date,
        "time": time_str,
        "mode": "TRANSIT",
    }

    while True:
        enforce_rate_limit()
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)

        if response.status_code == 429 or "Too Many Requests" in response.text:
            print("  [!] Rate limit hit (PT API). Cooling down for 5 seconds...")
            time.sleep(5)
            continue

        if response.status_code == 200:
            data = response.json()
            if "plan" in data and data["plan"].get("itineraries"):
                best_route = data["plan"]["itineraries"][0]

                total_time = int(best_route.get("duration", 0) / 60)
                walk_time = int(best_route.get("walkTime", 0) / 60)
                transit_time = int(best_route.get("transitTime", 0) / 60)

                bus_time_seconds = 0
                rail_time_seconds = 0
                transit_distance_meters = 0
                transit_legs = 0

                for leg in best_route.get("legs", []):
                    mode = leg.get("mode", "").upper()
                    leg_duration = leg.get("duration", 0)
                    leg_distance = leg.get("distance", 0)

                    if mode == "BUS":
                        transit_legs += 1
                        bus_time_seconds += leg_duration
                        transit_distance_meters += leg_distance
                    elif mode in ["SUBWAY", "TRAM", "RAIL", "MRT", "LRT"]:
                        transit_legs += 1
                        rail_time_seconds += leg_duration
                        transit_distance_meters += leg_distance

                bus_time = int(bus_time_seconds / 60)
                rail_time = int(rail_time_seconds / 60)
                transfers = max(0, transit_legs - 1)

                fare_string = best_route.get("fare", "0")
                try:
                    fare = float(fare_string)
                except ValueError:
                    fare = 0.0

                if fare == 0.0 and transit_distance_meters > 0:
                    transit_distance_km = transit_distance_meters / 1000.0
                    if transit_distance_km <= 3.2:
                        fare = 1.09
                    else:
                        fare = round(1.09 + ((transit_distance_km - 3.2) * 0.05), 2)

                return total_time, walk_time, bus_time, rail_time, transit_time, transfers, fare
        else:
            print(f"  [!] PT API Error: {response.text}")

        return -1, -1, -1, -1, -1, -1, 0.0


def get_drive_walk_cycle_route(start_coords, end_coords, route_type):
    url = "https://www.onemap.gov.sg/api/public/routingsvc/route"
    params = {"start": start_coords, "end": end_coords, "routeType": route_type}

    while True:
        enforce_rate_limit()
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)

        if response.status_code == 429 or "Too Many Requests" in response.text:
            print(
                f"  [!] Rate limit hit ({route_type.capitalize()} API). Cooling down for 5 seconds..."
            )
            time.sleep(5)
            continue

        if response.status_code == 200:
            data = response.json()
            if "route_summary" in data:
                return int(data["route_summary"]["total_time"] / 60)
        else:
            print(f"  [!] {route_type.capitalize()} API Error: {response.text}")

        return -1


def generate_matrix():
    configure_auth_headers()

    dest_coords_map = {}
    print(f"Translating destination postal codes from {DEST_FILE}...")

    with DEST_FILE.open(mode="r", encoding="utf-8") as dest_handle:
        dest_reader = csv.DictReader(dest_handle)
        for row in dest_reader:
            dest_id = row["ID"]
            postal_code = str(row["Postal Code"]).strip()
            coords = get_coordinates(postal_code)
            if coords:
                dest_coords_map[dest_id] = coords

    print(
        f"\nTranslating rental postal codes from {ORIGIN_NODES_FILE} and calculating routes..."
    )
    with ORIGIN_NODES_FILE.open(mode="r", encoding="utf-8") as rental_handle, OUTPUT_CSV.open(
        mode="w", newline="", encoding="utf-8"
    ) as output_handle:
        rental_reader = csv.DictReader(rental_handle)
        writer = csv.writer(output_handle)

        writer.writerow(
            [
                "flat_id",
                "destination_id",
                "pt_total",
                "pt_walk",
                "pt_bus",
                "pt_rail",
                "pt_transit",
                "pt_transfers",
                "pt_fare",
                "drive_total",
                "cycle_total",
                "walk_total",
            ]
        )

        for row in rental_reader:
            flat_id = row["Flat_ID"]
            postal_code = str(row["Postal_Code"]).strip()

            print(f"Processing Flat {flat_id} (Postal: {postal_code})...")
            flat_coords = get_coordinates(postal_code)

            if not flat_coords:
                print(f"  [!] Skipping {flat_id}: invalid postal code.")
                continue

            for dest_id, dest_coords in dest_coords_map.items():
                pt_total, pt_walk, pt_bus, pt_rail, pt_transit, pt_transfers, pt_fare = get_pt_route(
                    flat_coords, dest_coords
                )
                drive_total = get_drive_walk_cycle_route(flat_coords, dest_coords, "drive")
                cycle_total = get_drive_walk_cycle_route(flat_coords, dest_coords, "cycle")
                walk_total = get_drive_walk_cycle_route(flat_coords, dest_coords, "walk")

                writer.writerow(
                    [
                        flat_id,
                        dest_id,
                        pt_total,
                        pt_walk,
                        pt_bus,
                        pt_rail,
                        pt_transit,
                        pt_transfers,
                        pt_fare,
                        drive_total,
                        cycle_total,
                        walk_total,
                    ]
                )

    print(f"\nSuccess! The offline database has been saved to '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generate transit_matrix.csv from origin_nodes.csv and Dst_List.csv "
            "using OneMap APIs."
        )
    )
    parser.parse_args()
    generate_matrix()
