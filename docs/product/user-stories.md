# Team Project - User Stories (MapsAroundYou)

## Persona
[cite_start]**Primary:** International student or newcomer working professional in Singapore[cite: 374].
[cite_start]**Goal:** Commuting mainly between home and a specific destination (campus/office) while minimizing daily travel rather than securing a specific postal code[cite: 415].

## Legend
- **Target Release:** V1.2 (First Increment), V1.3 (MVP), V1.4 (Alpha)
- Each story includes **Acceptance Criteria (AC)** written to be testable.

---

## V1.2 - First Feature Increment (Week 9)

- [ ] **US1 - Set Primary Destination**
  - [cite_start]**As a** renter, **I want** to set a primary destination (e.g., an MRT station) [cite: 383] **so that** listings can be evaluated by commute distance.
  - [cite_start]AC1: User can enter a destination via a dropdown or text field in the left input panel[cite: 378, 383].
  - [cite_start]AC2: System validates the input against a predefined static Time-Distance Matrix of stations/hubs[cite: 400].

- [ ] **US2 - Filter by Monthly Rent**
  - [cite_start]**As a** renter, **I want** to set a maximum rent limit [cite: 387] **so that** I only see affordable options.
  - [cite_start]AC1: System parses a bundled local static dataset (`listings.json` or `.csv`)[cite: 398].
  - [cite_start]AC2: Listings with a rent value higher than the user's limit are not processed[cite: 388].

---

## V1.3 - Add More Features (Week 10)

- [ ] **US3 - Set Commute Time Cap**
  - [cite_start]**As a** renter, **I want** to filter listings by a maximum travel time limit [cite: 384] **so that** I can manage my daily travel.
  - [cite_start]AC1: User can input a maximum travel time in minutes via the GUI[cite: 384].
  - [cite_start]AC2: System calculates basic transit time using the pre-calculated matrix and excludes listings exceeding the cap[cite: 385, 400].

- [ ] **US4 - Require Air-Conditioning**
  - [cite_start]**As a** renter, **I want** to require air-conditioning [cite: 389] **so that** unsuitable listings are removed.
  - [cite_start]AC1: User can toggle an "Air-Con Required" checkbox[cite: 389].
  - [cite_start]AC2: When enabled, listings without the aircon attribute are excluded from the final list[cite: 398].

- [ ] **US5 - Generate GUI Output**
  - [cite_start]**As a** renter, **I want** to see a clean output of the best matching listings in a display panel [cite: 379] **so that** I can review my options.
  - [cite_start]AC1: System outputs the top N listings (default N=10) that pass all filters to the right display panel[cite: 379, 394].
  - [cite_start]AC2: Each unit card displays the rent, address, and commute summary[cite: 380].

---

## V1.4 - Alpha Release (Week 11)

- [ ] **US6 - Anti-walk-dominant Route Filter**
  - [cite_start]**As a** renter, **I want** the system to reject routes that are primarily walking [cite: 392] [cite_start]**so that** I receive realistic public transport suggestions[cite: 392].
  - [cite_start]AC1: User can set an acceptable walking time per trip segment (default 10 mins)[cite: 391].
  - [cite_start]AC2: Routes where walking ratio is disproportionately high (e.g., <= 0.6 of total time) are rejected[cite: 392].

- [ ] **US7 - Commute Summary Breakdown**
  - [cite_start]**As a** renter, **I want** to see the commute details explicitly separated by transit and walking [cite: 395] **so that** I understand the journey better.
  - [cite_start]AC1: The output for each shortlisted item specifies "Transit Time" and "Walking Time"[cite: 395].

- [ ] **US8 - Set Persona Preset (Optional/Stretch)**
  - **As a** renter, **I want** to select a preset (Student vs. Worker) **so that** default time caps and budgets are automatically applied.
  - AC1: Selecting 'Student' sets max rent and default commute caps automatically based on typical student budgets.
  - AC2: User can manually override these default values in the left input panel.