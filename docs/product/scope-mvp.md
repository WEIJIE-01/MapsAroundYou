# Product Requirements Document (PRD)

**Project Name:** Smart Rental Search Algorithm
**Module:** CS2103DE Team Project (tP)
**Target Release:** V1.3 (Minimum Viable Product)
**Format:** Standalone Desktop Application (Java/GUI)

## 1. Product Overview
The Smart Rental Search Algorithm is a desktop Java application designed to reverse the conventional location-based property search. Instead of requiring users to know which neighborhood they want to live in, the system allows users to input their primary daily destination (e.g., school or workplace) and their commute constraints. The application then calculates and presents an optimized shortlist of rental units that meet these specific lifestyle needs.

## 2. Target Audience
* **Primary Persona:** International student or newcomer working professional in Singapore.
* **Key Characteristics:** Lacks local geographic and transit knowledge; prioritizes a manageable daily commute and budget over specific postal codes.

## 3. Graphical User Interface (GUI) Requirements
- [ ] **Left Input Panel (Constraints):** Contains text fields, dropdowns, and toggle switches for all user inputs (Destination, Max Rent, Max Commute Time, Air-Conditioning, Walking Tolerance).
- [ ] **Right Display Panel (Results):** A scrollable list displaying the generated shortlist of rental units. Each unit card will show the rent, address, and a breakdown of the commute summary.

## 4. Functional Requirements (MVP Scope)

### 4.1 Destination and Commute Filtering
- [ ] **REQ-1A (Destination Input):** The GUI must provide a dropdown or text field for the user to select their primary destination address (e.g., specific MRT stations or campuses).
- [ ] **REQ-1B (Total Travel Time Cap):** The user must be able to input an acceptable total travel time in minutes. The system will exclude any listings whose pre-calculated commute time to the destination exceeds this cap.

### 4.2 Unit Constraints
- [ ] **REQ-2A (Budget Limit):** The GUI must include a field to set a maximum monthly rent. Listings exceeding this value will not be processed.
- [ ] **REQ-2B (Air-Conditioning):** The GUI must include a checkbox to require air-conditioning.

### 4.3 Anti-Walk-Dominant Routing Logic
- [ ] **REQ-3A (Walking Cap):** The user must be able to set an acceptable walking time per trip segment (defaulting to 10 minutes).
- [ ] **REQ-3B (Route Rejection):** The algorithm must implement a sanity rule to reject routes where the walking time ratio is disproportionately high (e.g., walking ratio <= 0.6 of total time), ensuring practical public transport suggestions.

### 4.4 Output and Display
- [ ] **REQ-4A (Shortlist Generation):** The system must deterministically output a shortlist of the top N listings (default N=10) that pass all filters.
- [ ] **REQ-4B (Commute Summary):** The GUI must display the commute details for each shortlisted listing, explicitly separating "Transit Time" and "Walking Time".

## 5. Data & Architecture Strategy (JAR Constraints)
- [ ] **Static Listing Database:** Rental unit data will be stored locally within the application package (e.g., a bundled listings.json or listings.csv file containing 50-100 sample units with attributes like rent, coordinates/nearest station, and aircon availability).
- [ ] **Pre-Calculated Transit Matrix:** Live mapping APIs (like Google Maps) are excluded. The application will bundle a static Time-Distance Matrix mapping travel times between major transport hubs/stations to simulate realistic routing instantaneously.

## 6. Non-Functional Requirements
- [ ] **Performance:** The filtering algorithm and GUI update must complete the search and display results within 2 seconds of the user clicking "Search."
- [ ] **Portability:** The final product must be fully self-contained within a .jar executable, requiring only a standard Java Runtime Environment (JRE) to run on Windows, macOS, or Linux.
- [ ] **Offline Capability:** The core MVP functionality must operate entirely without an active internet connection.