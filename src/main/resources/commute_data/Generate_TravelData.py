import requests
import csv
import time

# --- 1. CONFIGURATION ---
ONEMAP_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMTc4MCwiZm9yZXZlciI6ZmFsc2UsImlzcyI6Ik9uZU1hcCIsImlhdCI6MTc3MjkwNTE0NCwibmJmIjoxNzcyOTA1MTQ0LCJleHAiOjE3NzMxNjQzNDQsImp0aSI6IjljZjVjN2VkLTYwMTMtNDNlOC1hNWE3LTUwNGM3ZTcxNWFhOSJ9.A3XIS7TBRk26NZjgytD7fQZiX-p3s34SbRoDhU0D9WDyiZiRGIWcyXrT4aVd5JxT8Jb5SkS5gGJ1n8iz2FXbTONmpp6K6BaL7cxBsL8YvI_FBVQG_kl5mYkTT0EpA_ipkk1D1x-jWGVboBpN70PtTc7pkNlvrjqq6wSz9VA-arfadQaj02mhY0oGgvtRkZa9lmkpHdIdTNXGpVMSrl1WPo61FUrdyP0t5pAo9NPYXsCperfDIWYSI5vhxApnfnTPA4JL-39wOTXimKxw_ktjyr0Uz0N0mWMntjastmeO2sy4lLJ44XcFNgtf0nm-eU1ajWrRvr1u82DLF0vTqTusfw"  # Replace with your actual token
HEADERS = {"Authorization": ONEMAP_TOKEN}

# --- RATE LIMITER SETTINGS ---
RATE_LIMIT_DELAY = 0.2  # 5 requests per second limit
last_request_time = 0

def enforce_rate_limit():
    """Ensures that API calls do not exceed the rate limit."""
    global last_request_time
    current_time = time.time()
    time_since_last_req = current_time - last_request_time

    if time_since_last_req < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - time_since_last_req)

    last_request_time = time.time()

# --- 2. API FUNCTIONS (WITH RETRY LOOPS) ---
def get_coordinates(postal_code):
    """Converts a postal code to Lat,Lon using OneMap Search API."""
    url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=Y"

    while True:
        enforce_rate_limit()
        response = requests.get(url)

        # Check for rate limit
        if response.status_code == 429 or "Too Many Requests" in response.text:
            print("  [!] Rate limit hit (Search API). Cooling down for 5 seconds...")
            time.sleep(5)
            continue

        if response.status_code == 200:
            data = response.json()
            if data['found'] > 0:
                lat = data['results'][0]['LATITUDE']
                lon = data['results'][0]['LONGITUDE']
                return f"{lat},{lon}"
        return None

def get_pt_route(start_coords, end_coords, date="03-09-2026", time_str="08:00:00"):
    """Fetches Public Transport route details including fare and transit breakdowns."""
    url = "https://www.onemap.gov.sg/api/public/routingsvc/route"
    params = {
        "start": start_coords,
        "end": end_coords,
        "routeType": "pt",
        "date": date,
        "time": time_str,
        "mode": "TRANSIT"
    }

    while True:
        enforce_rate_limit()
        response = requests.get(url, headers=HEADERS, params=params)

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

                bus_time_sec = 0
                rail_time_sec = 0
                transit_distance_m = 0 # To track total distance on buses/trains for fare estimation

                for leg in best_route.get("legs", []):
                    mode = leg.get("mode", "").upper()
                    leg_duration = leg.get("duration", 0)
                    leg_distance = leg.get("distance", 0)

                    if mode == "BUS":
                        bus_time_sec += leg_duration
                        transit_distance_m += leg_distance
                    elif mode in ["SUBWAY", "TRAM", "RAIL", "MRT", "LRT"]:
                        rail_time_sec += leg_duration
                        transit_distance_m += leg_distance

                bus_time = int(bus_time_sec / 60)
                rail_time = int(rail_time_sec / 60)

                # Parse Fare and apply Distance-Based Fallback Logic
                fare_str = best_route.get("fare", "0")
                try:
                    fare = float(fare_str)
                except ValueError:
                    fare = 0.0

                if fare == 0.0 and transit_distance_m > 0:
                    transit_distance_km = transit_distance_m / 1000.0

                    # Singapore Distance-Based Fare Estimate: $1.09 base up to 3.2km, then ~$0.05 per km
                    if transit_distance_km <= 3.2:
                        fare = 1.09
                    else:
                        fare = round(1.09 + ((transit_distance_km - 3.2) * 0.05), 2)

                return total_time, walk_time, bus_time, rail_time, transit_time, fare
        else:
            print(f"  [!] PT API Error: {response.text}")

        return -1, -1, -1, -1, -1, 0.0

def get_drive_walk_cycle_route(start_coords, end_coords, route_type):
    """Fetches Drive, Walk, or Cycle route details."""
    url = "https://www.onemap.gov.sg/api/public/routingsvc/route"
    params = {"start": start_coords, "end": end_coords, "routeType": route_type}

    while True:
        enforce_rate_limit()
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 429 or "Too Many Requests" in response.text:
            print(f"  [!] Rate limit hit ({route_type.capitalize()} API). Cooling down for 5 seconds...")
            time.sleep(5)
            continue

        if response.status_code == 200:
            data = response.json()
            if "route_summary" in data:
                return int(data["route_summary"]["total_time"] / 60)
        else:
            print(f"  [!] {route_type.capitalize()} API Error: {response.text}")

        return -1

# --- 3. MAIN SCRIPT ---
def generate_matrix():
    dest_file = "Dst_List.csv"
    rental_file = "Rental_List.csv"
    output_csv = "transit_matrix.csv"

    dest_coords_map = {}
    print(f"Translating Destination Postal Codes from {dest_file}...")

    with open(dest_file, mode='r', encoding='utf-8-sig') as d_file:
        d_reader = csv.DictReader(d_file)
        for row in d_reader:
            dest_id = row['ID']
            postal = str(row['Postal Code']).strip()
            coords = get_coordinates(postal)
            if coords:
                dest_coords_map[dest_id] = coords

    print(f"\nTranslating Rental Postal Codes from {rental_file} and calculating routes...")
    with open(rental_file, mode='r', encoding='utf-8-sig') as r_file, \
            open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:

        r_reader = csv.DictReader(r_file)
        writer = csv.writer(outfile)

        writer.writerow([
            "flat_id", "destination_id",
            "pt_total", "pt_walk", "pt_bus", "pt_rail", "pt_transit", "pt_fare",
            "drive_total", "cycle_total", "walk_total"
        ])

        for row in r_reader:
            flat_id = row['Flat_ID']
            postal = str(row['Postal_Code']).strip()

            print(f"Processing Flat {flat_id} (Postal: {postal})...")
            flat_coords = get_coordinates(postal)

            if not flat_coords:
                print(f"  [!] Skipping {flat_id}: Invalid postal code.")
                continue

            for dest_id, dest_coords in dest_coords_map.items():

                pt_total, pt_walk, pt_bus, pt_rail, pt_transit, pt_fare = get_pt_route(flat_coords, dest_coords)
                drive_total = get_drive_walk_cycle_route(flat_coords, dest_coords, "drive")
                cycle_total = get_drive_walk_cycle_route(flat_coords, dest_coords, "cycle")
                walk_total = get_drive_walk_cycle_route(flat_coords, dest_coords, "walk")

                writer.writerow([
                    flat_id, dest_id,
                    pt_total, pt_walk, pt_bus, pt_rail, pt_transit, pt_fare,
                    drive_total, cycle_total, walk_total
                ])

    print(f"\nSuccess! Your offline database has been saved to '{output_csv}'")

if __name__ == "__main__":
    generate_matrix()