# Team Project - User Stories (MapsAroundYou)

## Persona
**Primary:** International student or newcomer working professional in Singapore.
**Goal:** Commuting mainly between home and a specific destination (campus/office/place) while minimizing daily travel rather than securing a specific postal code.

## Legend
- **Target Release:** V1.2 (First Increment), V1.3 (Add More Features), V1.4 (Alpha)
- Each story includes **Acceptance Criteria (AC)** written to be testable.

---

## V1.2 - First Feature Increment (Week 9)

- [ ] **US1 - Set Primary Destination**
  - **As a** renter, **I want** to set a primary destination (e.g., NUS, NTU, SMU, NUH, Orchard) **so that** listings can be evaluated by commute distance.
  - **AC1:** User can enter a destination via a dropdown or text field in the left input panel.
  - **AC2:** System validates the input against a predefined static destination list and corresponding travel-time data.

- [ ] **US2 - Filter by Monthly Rent**
  - **As a** renter, **I want** to set a maximum rent limit **so that** I only see affordable options.
  - **AC1:** System parses a bundled local static dataset of curated housing listings (`listings.json` or `.csv`).
  - **AC2:** Listings with a rent value higher than the user's limit are not processed.

---

## V1.3 - Add More Features (Week 10)

- [ ] **US3 - Set Commute Time Cap**
  - **As a** renter, **I want** to filter listings by a maximum travel time limit **so that** I can manage my daily travel.
  - **AC1:** User can input a maximum travel time in minutes via the GUI.
  - **AC2:** System looks up basic commute time using the bundled local travel-time matrix and excludes listings exceeding the cap.

- [ ] **US4 - Require Air-Conditioning**
  - **As a** renter, **I want** to require air-conditioning **so that** unsuitable listings are removed.
  - **AC1:** User can toggle an "Air-Con Required" checkbox.
  - **AC2:** When enabled, listings without the air-con attribute are excluded from the final list.

- [ ] **US5 - Generate GUI Output**
  - **As a** renter, **I want** to see a clean output of the best matching listings in a display panel **so that** I can review my options.
  - **AC1:** System outputs the top N listings (default N=10) that pass all filters to the right display panel.
  - **AC2:** Each unit card displays the rent, address, and commute summary.

---

## V1.4 - Alpha Release (Week 11)

- [ ] **US6 - Anti-walk-dominant Route Filter**
  - **As a** renter, **I want** the system to reject routes that are primarily walking **so that** I receive realistic public transport suggestions.
  - **AC1:** System applies a configured walk-dominant threshold (default 0.6 of total commute time).
  - **AC2:** Routes where the walking ratio (`walkMinutes / totalMinutes`) is greater than or equal to the configured threshold are rejected.

- [ ] **US7 - Commute Summary Breakdown**
  - **As a** renter, **I want** to see the commute details split by transit and walking **so that** I understand the journey better.
  - **AC1:** The output for each shortlisted item specifies "Transit Time" and "Walking Time".

- [ ] **US8 - Set Persona Preset (Optional/Stretch)**
  - **As a** renter, **I want** to select a preset (Student vs. Worker) **so that** default time caps and budgets are automatically applied.
  - **AC1:** Selecting 'Student' sets max rent and default commute caps automatically based on typical student budgets.
  - **AC2:** User can manually override these default values in the left input panel.
