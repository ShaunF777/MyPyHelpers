MachineFill Reporter v0.4
=========================

MachineFill Reporter processes oil transaction CSV files exported from the
NavOilBay system and generates per-machine visual reports showing oil
consumption by type, with pie charts and full transaction tables.

WHAT IT DOES
- Reads a CSV file of oil fill transactions
- Groups transactions by Fleet Number (machine)
- Summarizes liters consumed per oil type (ACX30, 15W40, 68HYD, 85W140)
- Generates a PDF report with one page per machine, including a pie chart,
  summary table, and full transaction history

HOW TO USE
1. Double-click MachineFill.exe to start the application.
2. Step 1 — Click "Browse" to select your .csv file.
   The app will auto-detect the date range in the file.
3. Step 2 — (Optional) Select a company logo image for the report header.
   A default logo is bundled if none is selected.
4. Step 3 — Adjust the report date range if needed, or click "Clear Dates"
   to reset to the full range.
5. Step 4 — (Optional) Change the oil type colors.
6. Click "Generate Report".
7. The PDF is saved in the "Machinefill-Reports" folder next to the .exe.
8. Click "Open Output Folder" to view your reports.

SUPPORTED FILE FORMATS
- Standard NavOilBay CSV exports (with header row)
- Files without a header row
- Files containing NUL characters (common in raw system exports)

All of these are handled automatically — no manual cleanup needed.

TROUBLESHOOTING
- If something goes wrong, check the Status panel at the bottom of the
  window. It shows exactly which step succeeded or failed.
- Click "Copy Status Report" to copy the full log, or "Save Status Report"
  to save it as a .txt file. Send this file to your developer for support.

OUTPUT
- PDF reports: Machinefill-Reports\<csvname>_<days>Days_<enddate>.pdf
- Settings (colors, logo): %LOCALAPPDATA%\MachineFillReporter\

No installation or Python required. This is a standalone portable application.
