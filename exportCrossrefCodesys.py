# exportCrossrefCodesys.py
# Dumps Cross Reference and POU Call Graph to CSV files in a subfolder of the current project.
# Run inside CODESYS: Tools → Scripting → Execute Script File...

import csv
import os

proj = projects.primary
if proj is None:
    raise Exception("No project is currently open.")

# Detect project folder
proj_path = proj.path  # Full path to .project file
proj_dir = os.path.dirname(proj_path)

# Create export folder
export_dir = os.path.join(proj_dir, "Exports")
if not os.path.exists(export_dir):
    os.makedirs(export_dir)

# ---------------------------
# 1. Export Cross Reference
# ---------------------------
crossref_path = os.path.join(export_dir, "cross_reference.csv")
cross_ref = proj.get_cross_reference()

with open(crossref_path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Variable", "Location", "Type", "Access", "POU", "Line"])
    for entry in cross_ref:
        writer.writerow([
            entry.name,
            entry.location,
            entry.type,
            entry.access,
            entry.pou,
            entry.line
        ])

print("Cross reference exported to:", crossref_path)

# ---------------------------
# 2. Export POU Call Graph
# ---------------------------
callgraph_path = os.path.join(export_dir, "pou_call_graph.csv")

# Helper: get all POUs
pous = [pou for pou in proj.get_pous()]

# Build call relationships
edges = []
for pou in pous:
    # Search for calls to other POUs in this POU's text
    try:
        code = pou.text  # Works for ST; for FBD/CFC, you'd parse XML
    except:
        code = ""
    for target in pous:
        if target.name != pou.name and target.name in code:
            edges.append((pou.name, target.name))

# Write CSV
with open(callgraph_path, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Caller", "Callee"])
    for caller, callee in sorted(set(edges)):
        writer.writerow([caller, callee])

print("POU call graph exported to:", callgraph_path)

print("All exports complete. Files are in:", export_dir)