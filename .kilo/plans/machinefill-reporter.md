# MachineFill-Reporter Implementation Plan

## Project Overview
A Python desktop application that processes oil transaction CSV files and generates per-machine visual reports with pie charts and transaction tables. Output as double-clickable Windows .exe.

## CSV Format (from NavOilBay_mock.csv)
- Columns: TimeStamp, Fluid_Transaction, Liters_Dispensed, FleetNumber, Name, COY Number
- Oil types: 85W-140 Oil, 15W40 Oil, ACX30 Oil, HYD 68 Oil
- Liters are suffixed with "Ltr" (e.g., "499.45Ltr")

## Phase 1: Core Data Processing (VS Code testing)

### 1.1 Environment Setup
```powershell
# Already exists in C:\00. Documents\MyPyHelpers\.venv
pip install pandas matplotlib openpyxl
```

### 1.2 CSV Parsing Module (`src/csv_parser.py`)
- Read CSV with pandas
- Parse liters: strip "Ltr" suffix and convert to float
- Sort by FleetNumber, then TimeStamp (per requirements)
- Extract date range for report header

### 1.3 Data Processing Module (`src/data_processor.py`)
- Group transactions by FleetNumber
- Calculate per-machine totals per oil type
- Calculate percentages
- Return structured data for visualization

## Phase 2: Report Generation (HTML/PDF output)

### 2.1 Color Configuration
Default color mapping (configurable via GUI radio buttons later):
- 85W-140 Oil: red (#FF6B6B)
- 15W40 Oil: orange (#FF9F43)
- ACX30 Oil: green (#2ECC71)
- HYD 68 Oil: blue (#3498DB)

### 2.2 Visualization Module (`src/visualizer.py`)
- Generate pie charts per machine using matplotlib
- No percentages in pie slices (only oil name + liters)
- Small slices positioned toward top-right
- Save charts as images

### 2.3 Report Builder (`src/report_builder.py`)
- HTML template with:
  - H1 banner: filename + date range
  - Per-machine sections:
    - H2: "Visual breakdown of oil consumption for FleetNumber: {id}"
    - Left: pie chart (1/3 width)
    - Right: summary table (Oil Type, Total-Consumed, Percentage)
    - Full-width: sorted transaction table
- Export to PDF via matplotlib or reportlab

## Phase 3: GUI Application

### 3.1 GUI with Tkinter (`MachineFill.py`)
- Drag-and-drop zone for CSV files
- Radio buttons to toggle:
  - Show pie chart (on/off)
  - Show summary table (on/off)
  - Show transaction table (on/off)
- Color pickers for each oil type (4 color selectors)
- "Generate Report" button
- Preview window (optional)

### 3.2 File Structure
```
MachineFill-Reporter/
├── MachineFill.py           # Main entry point + GUI
├── src/
│   ├── csv_parser.py      # CSV loading and parsing
│   ├── data_processor.py  # Data grouping/aggregation
│   ├── visualizer.py      # Chart generation
│   └── report_builder.py  # HTML/PDF report assembly
├── data/
│   └── NavOilBay_mock.csv
├── reports/
│   └── (generated reports)
└── assets/
    └── (icons, colors.json)
```

## Phase 4: Packaging

### 4.1 PyInstaller Build
```powershell
pip install pyinstaller
pyinstaller --onefile --windowed MachineFill.py
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
│   ├── csv_parser.py
│   ├── data_processor.py
│   ├── visualizer.py
│   └── report_builder.py
├── data/
│   └── NavOilBay_mock.csv
├── reports/
└── assets/
```

### Step 3: CSV Parser Implementation
- Load CSV with pandas
- Clean `Liters_Dispensed`: strip "Ltr" suffix → float
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
- Preview window with scrollbars
- Save/export button

### Step 8: PyInstaller Packaging
```powershell
pyinstaller --onefile --windowed --add-data "data;data" --add-data "assets;assets" MachineFill.py
```

## Key Decisions Needed

1. **Oil colors**: Will use the pie chart mock for reference - if specific colors are shown, adopt those.

2. **COY Number**: Your requirements mention "who the service attendant was" - Name column covers this. COY Number can be added to transaction table if needed.

3. **Report organization**: One combined PDF with all machines, each machine gets its own section.

4. **Date period**: Will auto-detect from CSV min/max timestamps for the H1 banner.