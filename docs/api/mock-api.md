# Mock API & Data Generation Guide

This guide outlines the workflow for generating the offline travel-time database (`transit_matrix.csv`) used by the **MapsAroundYou** application. To ensure our Java application remains a lightweight, offline-capable JAR file, we pre-generate all routing data using a Python script connected to the OneMap Singapore API.

---

## ⚠️ 1. Critical: The 3-Day API Token Refresh
The OneMap API requires token-based authentication. **Tokens expire automatically every 3 days.** If you attempt to run the data generation script and receive an `{"message":"Unauthorized"}` error, your token has expired.

**How to Refresh the Token:**
1. Go to the [OneMap API Documentation Portal](https://www.onemap.gov.sg/apidocs/).
2. Log in with your registered account credentials.
3. Generate a new Authentication Token.
4. Open the [`Generate_TravelData.py`](./Generate_TravelData.py) script.
5. Replace the string in the `ONEMAP_TOKEN` variable with your new token. 
   *(Note: Do not include the word "Bearer", just paste the raw token string).*

---

## 2. File Overview

The data generation pipeline relies on three main files to produce the final database.

### [`Rental_List.csv`](./Rental_List.csv) (Input)
This file contains our mock database of 50 realistic rental locations, distributed fairly across Singapore's 5 main regions.
* `Flat_ID`: Unique identifier for the rental unit (e.g., `R01`).
* `Postal_Code`: 6-digit Singapore postal code.
* `Region`: General area (Central, East, North, North-East, West).
* `Area_Name`: Specific neighborhood (e.g., Bukit Merah).

### `Dst_List.csv`](./Dst_List.csv) (Input)
This file contains our 10 realistic destination hubs based on our target personas (Students, CBD workers, Industrial engineers, etc.).
* `ID`: Unique identifier for the destination (e.g., `D01`).
* `Category`: Type of destination (e.g., University, CBD Office).
* `Location Name`: Name of the landmark.
* `Postal Code`: 6-digit destination postal code.

### [`Generate_TravelData.py`](./Generate_TravelData.py) (Script)
The Python script that reads the two input CSVs, translates the postal codes into Latitude/Longitude using OneMap's Search API, and then queries the OneMap Routing API to calculate travel times for four modes: Public Transport, Driving, Cycling, and Walking.

---

## 3. How to Generate the Data

Ensure you have Python 3 installed along with the `requests` library (`pip install requests`).

1. Ensure [`Rental_List.csv`](./Rental_List.csv), [`Dst_List.csv`](./Dst_List.csv), and [`Generate_TravelData.py`](./Generate_TravelData.py) are all in the same folder.
2. Verify your `ONEMAP_TOKEN` is up-to-date (less than 3 days old).
3. Open your terminal or command prompt in that folder.
4. Run the script:
   ```bash
   python Generate_TravelData.py
   ```
## 4. Output: `transit_matrix.csv`

Once the script completes successfully, it generates `transit_matrix.csv`. This file acts as the offline relational database for our Java application, utilizing a "Wide Format" to store all transit modes efficiently in a single row per route.

**Data Dictionary:**

| Column Name | Description |
| :--- | :--- |
| `flat_id` | Foreign key matching `Flat_ID` in `Rental_List.csv`. |
| `destination_id` | Foreign key matching `ID` in `Dst_List.csv`. |
| `pt_total` | Total travel time via public transport in minutes. |
| `pt_walk` | Walking time in minutes during the public transport commute (e.g., walking to/from stations). |
| `pt_bus` | Time spent specifically on buses in minutes. |
| `pt_rail` | Time spent specifically on MRT/LRT in minutes. |
| `pt_transit` | Total time spent inside moving public transit vehicles in minutes. |
| `pt_fare` | Estimated public transport fare in SGD. |
| `drive_total` | Total driving time by car in minutes. |
| `cycle_total` | Total cycling time in minutes. |
| `walk_total` | Total walking time for the entire journey in minutes. |

---

## 5. Troubleshooting

* **`-1` Values in Output:** If a row contains `-1` for times, it means the API could not find a valid route between those two coordinates. Check if the postal codes in your input CSVs are valid.
* **`Unauthorized` Errors:** Your OneMap token has expired. See Section 1.
* **Connection Errors / Rate Limiting:** If the script crashes midway, you may be hitting the API too fast. Increase the `time.sleep(0.3)` values inside `Generate_TravelData.py` to `0.5` or `1.0`.