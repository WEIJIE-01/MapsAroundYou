# Team Project - User Stories (CS2103DE)

## Persona
**Primary:** International student or newcomer in Singapore, commuting mainly between home and a specific destination (campus/office).

## Legend
- **Target Release:** V1.2 (First Increment), V1.3 (MVP), V1.4 (Alpha)
- Each story includes **Acceptance Criteria (AC)** written to be testable.

---

## V1.2 - First Feature Increment (Week 9)

- [ ] **US1 - Set Primary Destination**
  - **As a** renter, **I want** to set a primary destination (e.g., an MRT station) **so that** listings can be evaluated by commute distance.
  - AC1: User can enter a destination string.
  - AC2: System validates the input against a predefined list of stations/hubs.

- [ ] **US2 - Filter by Monthly Rent**
  - **As a** renter, **I want** to set a maximum rent limit **so that** I only see affordable options.
  - AC1: System parses a local static dataset of listings.
  - AC2: Listings with a rent value higher than the user's limit are excluded from the output.

---

## V1.3 - Minimum Viable Product (Week 10)

- [ ] **US3 - Set Commute Time Cap**
  - **As a** renter, **I want** to filter listings by a maximum travel time limit **so that** I can manage my daily travel.
  - AC1: User can input a maximum travel time in minutes.
  - AC2: System calculates basic transit time (using a predefined matrix or simple logic) and excludes listings exceeding the cap.

- [ ] **US4 - Require Air-Conditioning**
  - **As a** renter, **I want** to require air-conditioning **so that** unsuitable listings are removed.
  - AC1: User can toggle an "Air-Con Required" flag.
  - AC2: When enabled, listings without the aircon attribute are excluded from the final list.

- [ ] **US5 - Generate Shortlist CLI/GUI Output**
  - **As a** renter, **I want** to see a clean output of the best matching listings **so that** I can review my options.
  - AC1: System outputs the top N listings (default N=10) that pass all filters.
  - AC2: Output displays basic listing details (Rent, Commute Time, Address).

---

## V1.4 - Alpha Release (Week 11)

- [ ] **US6 - Anti-walk-dominant Route Filter**
  - **As a** renter, **I want** the system to reject routes that are primarily walking **so that** I receive realistic public transport suggestions.
  - AC1: System identifies the walking segment of the calculated route.
  - AC2: Routes where total walking time exceeds a predefined sanity threshold (e.g., >20 mins) are rejected.

- [ ] **US7 - Commute Summary Breakdown**
  - **As a** renter, **I want** to see the commute details split by transit and walking **so that** I understand the journey better.
  - AC1: The output for each shortlisted item specifies "X mins transit, Y mins walk".

- [ ] **US8 - Set Persona Preset (Optional/Stretch)**
  - **As a** renter, **I want** to select a preset (Student vs. Worker) **so that** default time caps and budgets are automatically applied.
  - AC1: Selecting 'Student' sets max rent to $1500 and commute to 45m.
  - AC2: User can manually override these default values.
