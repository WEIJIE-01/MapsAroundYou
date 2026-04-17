# MapsAroundYou User Guide

MapsAroundYou is an **offline smart rental search** app that helps you shortlist rental listings using a bundled local dataset (listings + precomputed commute times). It’s for users who want **fast, repeatable filtering** (rent/commute/walk/aircon) without relying on live APIs.

![MapsAroundYou logo](../src/main/resources/mapsaroundyou/gui/MapsAroundYou_Logo.png)

This document is the **canonical end-user User Guide** for MapsAroundYou. It focuses on how to run and use the app (GUI + CLI), not on developer internals or data generation.

## Table of Contents

- [Quick Start](#quick-start)
- [CLI command reference](#cli-command-reference)
- [Features](#features)
  - [Notes about usage formats (GUI & CLI)](#notes-about-usage-formats-gui--cli)
  - [GUI: Run a search and view results](#gui-run-a-search-and-view-results)
  - [GUI: View listing details](#gui-view-listing-details)
  - [GUI: Settings (persona preset, dark mode)](#gui-settings-persona-preset-dark-mode)
  - [CLI: Interactive mode](#cli-interactive-mode)
  - [CLI: Flag-driven search](#cli-flag-driven-search)
  - [CLI: Help](#cli-help)
- [End-to-end usage scenario](#end-to-end-usage-scenario)
- [Troubleshooting](#troubleshooting)
- [Maintenance note](#maintenance-note)
- [FAQ](#faq)
- [Known Issues](#known-issues)
- [Summary / Cheat Sheet](#summary--cheat-sheet)

## Quick Start

### 1) Prerequisites

- **Java**: Java **21** or newer installed and available via `PATH` or `JAVA_HOME`.
- **OS**: Windows, macOS, and Linux are supported for normal builds.
- **No separate Gradle install needed**: the repo includes the Gradle wrapper (`gradlew` / `gradlew.bat`).

> [!IMPORTANT]
> The GUI uses JavaFX. **Windows ARM64 is not supported natively by JavaFX**; see [Known Issues](#known-issues).

### 2) Get the app

Clone or download the repository, then open a terminal in the repository root.

### 3) Run the GUI (JavaFX)

**Windows (PowerShell):**

```powershell
.\gradlew runGui
```

**macOS/Linux (bash/zsh):**

```bash
./gradlew runGui
```

### 4) Run the CLI

**Windows (PowerShell):**

```powershell
.\gradlew run
```

**macOS/Linux:**

```bash
./gradlew run
```

### 5) First launch: what you should see

- **GUI**: A window titled **“MapsAroundYou”** with
  - a destination picker,
  - filter inputs (rent/commute/transfers/walk/aircon/result limit),
  - a **Search** button,
  - a results table (initially empty),
  - a details panel for the selected listing,
  - a dataset label such as “Data accurate as of …”.
![gui-first-launch](assets/guide_images/GUI-first-launch.png)
- **CLI**: A banner “MapsAroundYou CLI” plus dataset provenance, then either:
  - **interactive prompts**, or
  - structured command handling if you pass arguments.

### 6) Try these quick actions

- **GUI**:
  1. Choose a destination.
  2. Enter `max rent` and `max commute`.
  3. Click **Search**.
  4. Click a row to see details.
![gui-quick-action](assets/guide_images/GUI-quick-action.png)
- **CLI**:
  1. Run `.\gradlew run`.
  2. Enter a destination id such as `D01` when prompted.
  3. Press **Enter** to accept defaults in brackets for the other prompts.
  4. Type `exit` at the destination prompt to quit.

## CLI command reference

MapsAroundYou’s CLI supports **three** entry flows:

- **Interactive mode**: run with **no arguments**.
- **Flag-driven search**: run `search` with required flags.
- **Help**: run `--help` / `-h` / `help` (or `search --help`).

### Commands

#### Interactive mode (default)

- **Windows**: `.\gradlew run`
- **macOS/Linux**: `./gradlew run`

Interactive mode prints:

- **Supported destinations** list
- `Interactive mode` instructions
- A sequence of prompts (see [CLI: Interactive mode](#cli-interactive-mode))

Exit by typing `exit` or `quit` at:

- the **Destination ID** prompt, or
- the **“Press Enter to search again or type exit”** prompt

#### `search` (one-off search)

Run one search and print results, then exit.

**Required flags**

- `--destination <ID>`
- `--max-rent <SGD>` (integer, \( \ge 0 \))
- `--max-commute <minutes>` (integer, \( \ge 1 \))

**Optional flags**

- `--max-transfers <count>` (integer, \( \ge 0 \); if omitted, uses your saved/default preference)
- `--max-walk <minutes>` (integer, \( \ge 0 \); if omitted, uses your saved/default preference)
- `--result-limit <count>` (integer, \( \ge 1 \); if omitted, uses your saved/default preference)
- `--sort <commute|rent|balanced>` (if omitted, uses your saved/default preference)
- `--require-aircon` (switch; if present, requires aircon)
- `--exclude-walk-dominant` (switch; if present, excludes walk-dominant routes)

**Exit codes**

- `0`: success (including “no results”)
- `1`: user error (unknown command/flag, missing required flag, invalid values, unknown destination) or unexpected failure

#### Help

All of these print usage text:

- `.\gradlew run --args="--help"`
- `.\gradlew run --args="-h"`
- `.\gradlew run --args="help"`
- `.\gradlew run --args="search --help"`

## Features

### Notes about usage formats (GUI & CLI)

#### GUI conventions

- **Required vs optional**:
  - Destination must be selected before searching.
  - Other fields are validated; invalid input shows an error in the status bar.
- **Where results appear**:
  - Results show in a table with columns including **Listing**, **Rent (SGD)**, **Commute**, **A/C**, and **Match**.
- **What “Match” means**:
  - The GUI displays a match score as a percentage (e.g., `82.5%`). Higher is better.

#### CLI conventions

- Words in `<>` are values you provide.
- Flags starting with `--` are named options.
- In **interactive mode**, pressing **Enter** keeps the bracketed default.
- To quit interactive mode, type `exit` or `quit` when prompted.

---

### GUI: Run a search and view results

Runs an offline search using your selected destination and filters, then shows ranked matches.

**How to use**

1. Start the GUI:

   ```powershell
   .\gradlew runGui
   ```

2. In the left panel:
   - Choose a **Destination**.
   - Fill in filters such as:
     - **Max rent (SGD)**
     - **Max commute (minutes)**
     - **Max transfers**
     - **Result limit**
     - **Max walking time (minutes)**
     - **Require aircon**
     - **No walk-dominant routes**
3. Click **Search**.

**Expected behavior**

- While searching, inputs are temporarily disabled and the status shows **“Searching…”**.
- When finished:
  - the results table is populated,
  - the status shows **“Found N result(s).”**,
  - the dataset label reflects the dataset provenance/last updated date.
- If a field is invalid (e.g., not a number), the status shows a user-facing error message and the search does not run.

**Examples**

- A basic search:
  - Destination: choose any supported destination from the dropdown
  - Max rent: `1800`
  - Max commute: `45`
  - Result limit: `10`
  - Click **Search**

**Tips / warnings**

- **Max transfers**: set a high value if you don’t want to filter by interchange count (the CLI help explicitly suggests this).
- **No walk-dominant routes**: excludes commutes where walking dominates the total time (the app uses an internal “walk dominant” threshold).

---

### GUI: View listing details

Shows more information about a listing you select from the results table.

**How to use**

1. Run a search.
2. Click a row in the results table.

**Expected behavior**

- The “Selected Listing” panel updates with details such as:
  - Address, room type, rent, aircon
  - Commute summary
  - Match score
  - Source platform and notes (if available)

**Examples**

- After searching, click the first row. The details panel should populate immediately.

---

### GUI: Settings (persona preset, dark mode)

The GUI includes lightweight settings for onboarding and appearance.

**How to use**

1. Click **Settings** in the top bar.
2. In the settings window:
   - Choose a **Persona preset** (`Student` or `Worker`).
   - Toggle **Dark mode** on/off.
3. Click **Close**.

**Expected behavior**

- **Persona preset** pre-fills some defaults (for example max rent, max commute, and aircon preference).
- **Dark mode** applies a dark theme stylesheet to the UI.
- These settings are saved best-effort using Java’s `Preferences` store (OS-specific).

**Examples**

- Turn on **Dark mode** and close Settings. The app stays in dark mode for future launches (unless the OS blocks preference writes).

---

### CLI: Interactive mode

Interactive mode prompts you for search preferences and allows repeated searches until you exit.

**How to use**

1. Start the CLI:

   ```powershell
   .\gradlew run
   ```

2. Follow prompts for:
   - Destination ID (type `exit` to quit)
   - Max rent (SGD)
   - Max commute (minutes)
   - Max transfers
   - Max walking time (minutes)
   - Require aircon? (`y`/`n`)
   - Result limit
   - Sort mode (`commute`, `rent`, `balanced`)
   - Exclude walk-dominant routes? (`y`/`n`)
3. After results print, press Enter to search again or type `exit`.

**Expected behavior**

- The CLI prints a “Supported destinations” list first.
- Pressing **Enter** accepts the value in brackets.
- The destination prompt is shown as `Destination ID [<default>]:`.
- The sort prompt is shown as `Sort mode (commute/rent/balanced) [<default>]:`.
- A successful search prints a ranked list including rent, commute breakdown (transit/walk), address, room type, and score.
- If a search yields no matches, the CLI prints a “no results” message and continues.

**Examples**

A typical interactive session looks like this (prompts abbreviated):

```text
Destination ID [D01]:
Max rent (SGD) [1800]:
Max commute (minutes) [45]:
...
Press Enter to search again or type exit:
```

---

### CLI: Flag-driven search

Runs a single search using a structured command.

**How to use**

**Windows (PowerShell):**

```powershell
.\gradlew run --args="search --destination D01 --max-rent 2200 --max-commute 45 --max-transfers 1 --max-walk 10 --result-limit 5 --sort balanced --require-aircon --exclude-walk-dominant"
```

**Supported flags**

- `--destination <ID>` *(required)*
- `--max-rent <SGD>` *(required; integer ≥ 0)*
- `--max-commute <minutes>` *(required; integer ≥ 1)*
- `--max-transfers <count>` *(optional; integer ≥ 0)*
- `--max-walk <minutes>` *(optional; integer ≥ 0)*
- `--result-limit <count>` *(optional; integer ≥ 1)*
- `--sort <commute|rent|balanced>` *(optional)*
- `--require-aircon` *(optional switch)*
- `--exclude-walk-dominant` *(optional switch)*

**Expected behavior**

- If you omit an optional flag, the CLI reuses your current stored preference for that field.
- Unknown commands or flags print an error message to stderr (prefixed with `Error:`) plus help text.
- If you pass `search --help`, the CLI prints help (same as `help`).

**Examples**

- Fast commute, limit results, no aircon requirement:

```powershell
.\gradlew run --args="search --destination D05 --max-rent 1800 --max-commute 35 --result-limit 10 --sort commute"
```

---

### CLI: Help

Prints usage and examples.

**How to use**

```powershell
.\gradlew run --args="--help"
```

or

```powershell
.\gradlew run --args="help"
```

## End-to-end usage scenario

This scenario shows a realistic “shortlist apartments for commute + rent” flow end-to-end, using the CLI (works the same way conceptually in the GUI).

### Scenario: shortlist close-to-commute rentals (CLI)

1. Launch interactive CLI:

   ```powershell
   .\gradlew run
   ```

2. Pick a destination ID from the printed “Supported destinations” list, then enter your constraints:
   - Destination ID: `D01`
   - Max rent: `1800`
   - Max commute: `35`
   - Max transfers: `1`
   - Max walking time: `10`
   - Require aircon: `y`
   - Result limit: `10`
   - Sort mode: `commute`
   - Exclude walk-dominant routes: `n`

3. Expected output shape (example):

```text
MapsAroundYou CLI
Offline smart rental search scaffold
Data accurate as of 2026-03-08 | Fixture dataset

Supported destinations:
  D01  NUS                                                    (University)

Interactive mode
Type 'exit' at the destination prompt to quit.
Press Enter to keep the value shown in brackets.
You can leave max transfers high to avoid filtering by interchange count.

Top matches:
1. Fixture Listing [L001]
   Rent: SGD 1500 | Commute: 30 min (20 transit / 10 walk) | Aircon: Yes
   Address: 123 Demo Street | Type: HDB room | Score: 0.50
```

4. If the results look too restrictive, loosen a constraint (e.g., increase max rent or max commute) and search again.

## Troubleshooting

### The CLI prints an error and shows help

If the CLI can’t parse your command, it prints a single-line error to stderr prefixed with `Error:` and then prints help.

Common fixes:

- **Unknown command** (`Error: Unknown command: ...`): use `help` or `search`.
- **Unknown flag** (`Error: Unknown flag: ...`): check spelling (e.g., `--max-rent`, not `--max-rentt`).
- **Missing required flag** (`Error: Missing required flag: --destination`): ensure you passed all required flags for `search`.
- **Missing value for a flag** (`Error: Missing value for flag: --max-rent`): every value-flag must be followed by a value.
- **Invalid integer** (`Error: --max-commute must be a valid integer.`): only whole numbers are accepted.
- **Out-of-range values**:
  - `--max-commute` must be at least 1
  - `--max-rent`, `--max-transfers`, `--max-walk` must be at least 0
  - `--result-limit` must be at least 1

### Interactive mode ended early (piped input / missing lines)

If you see:

- `Error: Interactive mode ended before all inputs were provided.`

Run again and provide a full set of inputs, or avoid piping incomplete stdin.

### Startup error (dataset failed to load)

If you see:

- `Startup error: ...`

Try:

1. Run the quality gate to surface build/runtime issues:

   ```powershell
   .\gradlew clean check
   ```

2. Ensure you didn’t delete or move the bundled dataset under `src/main/resources/commute_data/`.

### The GUI won’t start

First confirm Java 21+ and then try `.\gradlew runGui`. If you are on Windows ARM64, see [Known Issues](#known-issues).

## Maintenance note

If the CLI flags, prompts, or GUI controls change, update this User Guide by cross-checking:

- CLI usage text printed by the app (`help`)
- The CLI parser (`src/main/java/mapsaroundyou/cli/CliCommandParser.java`)
- The interactive prompt flow (`src/main/java/mapsaroundyou/cli/CliApplication.java`)
- The GUI labels/controls (`src/main/java/mapsaroundyou/gui/MapsAroundYouGuiApp.java`)

## FAQ

### Where does MapsAroundYou get its data?

From bundled files under:

- `src/main/resources/commute_data/`

This includes destinations, listings, and a precomputed public-transport travel time matrix. The app does **not** call live APIs at runtime.

### How do I know how fresh the data is?

Both the GUI and CLI show dataset provenance based on:

- `src/main/resources/commute_data/dataset-metadata.properties`

### Where are my search preferences saved?

Last-used search preferences are stored locally at:

- `<user-home>/.mapsaroundyou/user-preferences.properties`

If the file is missing or invalid, the app safely falls back to defaults.

### Where are GUI settings (dark mode / persona) saved?

GUI settings are stored using Java’s `Preferences` (OS-managed storage). On Windows this is typically backed by the registry; on macOS/Linux it’s stored in OS-specific preference locations. If preference writes are blocked, the GUI still works but may not remember these settings.

### How do I reset my saved preferences?

- **Search preferences (CLI/GUI search defaults)**: delete
  - `<user-home>/.mapsaroundyou/user-preferences.properties`
- **GUI settings (dark mode/persona)**: clear the Java `Preferences` entries for the app (OS-specific; may require admin tooling).

### The GUI won’t start—what should I try first?

1. Confirm Java 21+:

   ```powershell
   java -version
   ```

2. Run the quality gate to surface build issues:

   ```powershell
   .\gradlew clean check
   ```

3. If you are on Windows ARM64, see [Known Issues](#known-issues).

## Known Issues

- **Windows ARM64 + JavaFX**: JavaFX does **not** support Windows ARM64 natively. If you are running on Windows ARM64, run the app using an **x64 JDK** (or use the CLI-only flow). The GUI launcher prints a concrete example path and a recommended JDK source.

## Summary / Cheat Sheet

### GUI

| Action | Where | Result |
|---|---|---|
| Start GUI | `.\gradlew runGui` | Opens the MapsAroundYou desktop app |
| Run search | Choose destination → fill filters → **Search** | Populates results table and status message |
| View details | Click a result row | Details panel updates |
| Change persona preset | **Settings** → Persona preset | Updates default values |
| Toggle dark mode | **Settings** → Dark mode | Applies dark theme |

### CLI

| Action | Command | Example |
|---|---|---|
| Start interactive CLI | `.\gradlew run` | `.\gradlew run` |
| Show help | `.\gradlew run --args="--help"` | `.\gradlew run --args="help"` |
| Run a one-off search | `.\gradlew run --args="search ..."` | `.\gradlew run --args="search --destination D01 --max-rent 2200 --max-commute 45 --sort balanced"` |

