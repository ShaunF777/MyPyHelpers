# MachineFill-Reporter Implementation Plan

## Project Overview
A Python desktop application that processes oil transaction CSV files and generates per-machine visual reports with pie charts and transaction tables. Output as double-clickable Windows .exe.

## CSV Format (from NavOilBay_mock.csv and IFS_KTK025_log_2026.06.04.csv)
- Columns: TimeStamp, Fluid_Transaction, Liters_Dispensed, FleetNumber, Name, COY Number
- Oil types: 85W-140 Oil, 15W40 Oil, ACX30 Oil, HYD 68 Oil
- Liters may be suffixed with "Ltr" (e.g., "499.45Ltr") or raw floats (e.g., "499.45")
- Name column may be empty; use Coynumber as fallback for Attendant display

## Phase 1: Core Data Processing ✅ COMPLETED

### 1.1 Environment Setup
```powershell
# Already exists in C:\00. Documents\MyPyHelpers\.venv
pip install pandas matplotlib openpyxl
```

### 1.2 CSV Parsing Module (`src/MachineFill.py`)
- Read CSV with pandas
- Parse liters: conditional handler for both raw floats and "Ltr"-suffixed strings
- Skip zero values (0.0 or 0.0Ltr) from all processing
- Sort by FleetNumber, then TimeStamp (per requirements)
- Extract date range for report header

### 1.3 Data Processing Module (`src/MachineFill.py`)
- Group transactions by FleetNumber
- Calculate per-machine totals per oil type
- Calculate percentages
- Return structured data for visualization
- Coynumber column maintained separately; used as fallback for empty Name/Attendant

## Phase 2: HTML Report Generation ✅ COMPLETED

### 2.1 Color Configuration
Fixed color mapping (Phase 4 GUI will allow overrides):
- ACX30: blue (#1f77b4)
- 15W40: orange (#ff7f0e)
- 68HYD: green (#2ca02c)
- 85W140: red (#d62728)
- Fallback: gray (#7f7f7f)

### 2.2 Visualization Module (`src/MachineFill.py`)
- Generate pie charts per machine using matplotlib
- Labels format: "[Oil Type] - [X]Ltr" (no percentages)
- Startangle: 90 degrees
- Save charts as `assets/chart_[FleetNumber].png`
- Clear plot memory after saving
- No pie chart title (removed `ax.set_title()`)

### 2.3 Report Builder (`src/MachineFill.py`)
- HTML template with:
  - H1 banner: filename + date range
  - Company logo: `assets/Thungela logo.png` (204 x 59 pixels) positioned top-left via flexbox
  - Per-machine sections:
    - H2 (centered): "Summerised oil consumption for FleetNumber : {id}"
    - Left: pie chart (1/3 width)
    - Right: summary table (Oil Type, Total-Consumed, Percentage)
    - Full-width: sorted transaction table (Timestamp, Attendant, Coynumber, Oil Type, Liters)
- Liters rounded to 0.1 precision in all outputs
- Zero-liter transactions filtered out before processing

## Phase 3: Local PDF Generation Engine

### 3.1 PDF Export Automation
- ... (existing items)
- **User feedback summary (last 8 questions)**:
  - Abbreviated comments on Figure size and axes: `fig, ax = plt.subplots(figsize=(6.2, 4.8))`; radius 0.95 suggestion; startangle 135.
  - Clarified conditional banner placement: `if page_idx == 0:` with `[0.0, 0.87, 1.0, 0.12]` facecolor.
  - Explained conditional Axes dimensions for charts: `[0.02, 0.26 if page_idx == 0 else 0.38, 0.54, 0.66]`.
  - Requested removal of 1.5 multiplier, direct size increase.
  - Noted shared PNG usage between HTML and PDF.
  - Asked for exact breakdown of `ax_img = fig.add_axes([...])` arguments.
 ⏳ IN PROGRESS

### 3.1 PDF Export Automation
- Create dedicated function `export_to_pdf(machine_groups, output_path)`
- Save to `reports/machine_consumption_summary.pdf`
- Mirror HTML layout structure:
  - First page: H1 Header Banner with source filename and date boundaries
    - Include colored background (#2c3e50) matching HTML
    - Include company logo: `assets/Thungela logo.png` (204 x 59 pixels) top-left
    - Logo and heading should have a unified background banner
    - Remove axis numbers/tick marks from background banner (no visible graph axes)
      - Fix: Do not use `axis('off')` on banner axes as it hides the background color
      - Instead hide only tick labels and spines while preserving the #2c3e50 background
    - Heading and date range should be positioned center-to-right of the background banner (not overlapping logo)
  - Per FleetNumber section on clean page boundaries:
    - H2 Machine Heading: "Visual breakdown of oil consumption for FleetNumber : [FleetNumber]"
    - Pre-generated pie chart image on left (fixed size consistent with HTML, enlarged by 50%)
    - Summary table (3x4) on right: [Oil Type, Total, Percentage]
      - Reduce cell padding (20-30% smaller) to make space for larger pie charts
      - Move table closer to H2 heading (reduce margin)
    - Full-width transactional history grid: Timestamp, Attendant, Oil Type, Liters
- Chart sizing consistency fix:
  - Ensure all charts render at identical dimensions regardless of slice count
  - Enlarge pie charts by at least 50% while maintaining consistency
  - Use fixed axes/bounding box for chart images to prevent size variation between machines
- First page should show first machine's H2 and report content (not blank)
- Each machine gets its own page
- Wrap PDF compilation in try/except block
- Handle file system locks with clear terminal warning to close PDF

### 3.2 Execution Flow
- HTML generation completes first
- PDF compilation triggers automatically immediately after successful HTML generation

## Phase 4: GUI Evolution ⏳ PENDING

### 4.1 GUI with Tkinter (`MachineFill.py`)
- Drag-and-drop zone for CSV files
- Color pickers for each oil type (4 color selectors)
  - Default colors from Phase 2 hex codes
  - Allow user overrides
- Interactive Date Filtering:
  - Initially load and preview all CSV data
  - "Begin Date" and "End Date" buttons for specific date range selection
  - Restricted to scope of loaded CSV data
- "Generate Report" button
- Preview window (optional)

### 4.2 File Structure
```
MachineFill-Reporter/
├── MachineFill.py           # Main entry point + GUI
├── src/
│   └── MachineFill.py      # Core logic + report generation
├── data/
│   └── NavOilBay_mock.csv
├── reports/
│   └── (generated reports)
└── assets/
    └── (icons, Thungela logo.png)
```

## Implementation Steps

### Step 1: Install Dependencies
```powershell
cd "C:\00. Documents\MyPyHelpers"
.venv\Scripts\activate
pip install pandas matplotlib pyinstaller
```

### Step 2: Create Folder Structure
```
MachineFill-Reporter/
├── MachineFill.py           # Main entry point + GUI + core logic
├── src/
│   └── MachineFill.py
├── data/
│   └── NavOilBay_mock.csv
├── reports/
└── assets/
```

### Step 3: CSV Parser Implementation
- Load CSV with pandas
- Clean `Liters_Dispensed`: conditional handler for raw floats and "Ltr" strings
- Skip zero values (0.0 or 0.0Ltr)
- Sort: FleetNumber ascending, then TimeStamp ascending
- Return DataFrame ready for processing

### Step 4: Data Processor Implementation
- Group by FleetNumber
- Aggregate: sum liters per Fluid_Transaction
- Calculate percentages (total / sum per machine)
- Return dict: `{fleetnumber: {fluid: {total_liters, percentage}}}`

### Step 5: Visualizer (matplotlib)
- Create figure with pie chart (no percentages in labels)
- Labels format: "ACX30 - 640Ltr" (as specified)
- Small slices → label outside with connecting lines
- Fixed colors per oil type (stored in config)

### Step 6: Report Builder
- Generate HTML report per machine
- Layout: H1 banner → H2 fleet section → pie+table → transaction table
- Export to PDF using matplotlib's `PdfPages` or reportlab

### Step 7: GUI (Tkinter)
- File dialog for CSV selection (drag-and-drop optional)
- Checkboxes: pie chart, summary table, transaction table
- Color pickers: 4 buttons for each oil type
- Date range selectors: Begin Date and End Date
- Preview window with scrollbars
- Save/export button

### Step 8: PyInstaller Packaging
```powershell
pyinstaller --onefile --windowed --add-data "data;data" --add-data "assets;assets" MachineFill.py
```

## Key Decisions Made

1. **Oil colors**: Fixed mapping from Phase 2 (#1f77b4, #ff7f0e, #2ca02c, #d62728)
2. **COY Number**: Maintained as separate column; used as fallback for empty Name/Attendant
3. **Report organization**: One combined HTML/PDF with all machines, each machine gets its own section
4. **Date period**: Auto-detect from CSV min/max timestamps for H1 banner; GUI will allow custom range
5. **Logo**: Thungela logo.png (204 x 59 pixels) positioned top-left via flexbox
6. **Liters precision**: 0.1 precision rounding in all outputs
7. **Zero values**: Filtered out before processing (0.0 or 0.0Ltr)