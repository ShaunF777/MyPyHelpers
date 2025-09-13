# exportCrossrefCodesys.py
# Dumps the current project's cross reference to a CSV file.
# Run inside CODESYS: Tools → Scripting → Execute Script File...

import csv
import os

# Get the active project
proj = projects.primary
if proj is None:
    raise Exception("No project is currently open.")

# Ask user where to save
save_path = os.path.join(os.path.expanduser("~"), "codesys_crossref.csv")

# Access the cross reference
cross_ref = proj.get_cross_reference()

# Prepare CSV
with open(save_path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Variable", "Location", "Type", "Access", "POU", "Line"])
    
    for entry in cross_ref:
        # entry has: .name, .location, .type, .access, .pou, .line
        writer.writerow([
            entry.name,
            entry.location,
            entry.type,
            entry.access,
            entry.pou,
            entry.line
        ])

print("Cross reference exported to:", save_path)