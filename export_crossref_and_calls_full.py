# export_crossref_and_calls_full.py
# Exports:
#  1) Cross reference CSV (if API available)
#  2) Full POU call graph CSV (from PLCopen XML, covers ST + FBD/CFC)
#  3) Mermaid call graph (graph TD)
#
# Outputs are created in: <project_folder>\Exports\

# Exporting cross reference and a full POU call graph including FBD/CFC
'''
You’ll get two outputs in one run, dropped into an Exports folder beside your .project:
- cross_reference.csv
- pou_call_graph.csv (plus a call_graph.mmd Mermaid file you can render anywhere)
I’ve also made it generic: it auto-detects your project’s folder and looks for a PLCopen XML export there. Since many of your POUs are FBD/CFC, the script parses that XML to capture calls from graphical logic as well as ST.

What you can do with the call graph
- See who-calls-who across Programs, FBs, and Functions.
- Spot dead code (POUs with no inbound edges).
- Identify deep chains that are performance or complexity hotspots.
- Feed it into Mermaid to produce shareable diagrams for your team.

How it works
- Cross reference: uses the IDE’s scripting API. If your SP build does not expose the cross reference programmatically, the script will skip it gracefully (you can still paste-export it manually).
- Call graph: parses a PLCopen XML export for both ST and FBD/CFC bodies. For FBD/CFC, it reads each block’s typeName as a callee. For ST, it detects textual calls.
Tip: Place your PLCopen XML export in the project folder (or Exports). The script will auto-pick the newest .xml there. You can also hard-set a path at the top.

IronPython quick note
IronPython is Python running on .NET inside CODESYS. It can inspect and automate the open project from Tools → Scripting. Comments and commented-out code are ignored by cross reference and won’t pollute results.

'''
import os, re, csv, sys, time
from datetime import datetime

# .NET XML (works in IronPython inside CODESYS)
import clr
from System.Xml import XmlDocument, XmlNamespaceManager
from System.IO import Directory, Path, File

# -----------------------------
# Helpers
# -----------------------------
def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p)

def now_stamp():
    return datetime.now().strftime("%Y-%m-%d %H.%M.%S")

def find_latest_xml(search_dirs):
    # Find the most recently modified .xml file likely to be a PLCopen export
    candidates = []
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            if fname.lower().endswith(".xml"):
                full = os.path.join(d, fname)
                try:
                    candidates.append((os.path.getmtime(full), full))
                except:
                    pass
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]

def read_xml(path):
    doc = XmlDocument()
    doc.Load(path)
    return doc

def ns_manager(doc):
    # PLCopen namespaces commonly used
    nsm = XmlNamespaceManager(doc.NameTable)
    # Main PLCopen TC6 namespace
    nsm.AddNamespace("plc", "http://www.plcopen.org/xml/tc6_0201")
    # Sometimes ST bodies are wrapped in XHTML
    nsm.AddNamespace("xhtml", "http://www.w3.org/1999/xhtml")
    return nsm

def sanitize_identifier(s):
    # basic Mermaid-safe node label
    return re.sub(r"[^A-Za-z0-9_:.]+", "_", s)

# Simple ST call detector: looks for identifiers followed by '(' that match known POUs
def detect_calls_in_st(st_text, pou_names):
    calls = set()
    # Remove comments (// ... EOL) and (* ... *)
    no_line = re.sub(r"//.*?$", "", st_text, flags=re.MULTILINE)
    no_block = re.sub(r"\(\*.*?\*\)", "", no_line, flags=re.DOTALL)
    # Find tokens that look like a call: Name(   but avoid IF(, AND( etc by later filtering against pou_names
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", no_block):
        name = m.group(1)
        if name in pou_names:
            calls.add(name)
    return calls

# Extract calls from FBD/CFC blocks: <block><typeName>Target</typeName>...
def detect_calls_in_fbd(fbd_node, nsm):
    callees = set()
    blocks = fbd_node.SelectNodes(".//plc:block", nsm)
    if blocks is None: 
        return callees
    for b in blocks:
        t = b.SelectSingleNode("./plc:typeName", nsm)
        if t is not None and t.InnerText:
            callees.add(t.InnerText.strip())
    return callees

# -----------------------------
# Entry
# -----------------------------
proj = projects.primary
if proj is None:
    raise Exception("No project open.")

proj_path = proj.path
proj_dir  = os.path.dirname(proj_path)
export_dir = os.path.join(proj_dir, "Exports")
ensure_dir(export_dir)

print("Project:", proj_path)
print("Exports folder:", export_dir)

# -----------------------------
# 1) Cross reference CSV (best-effort)
# -----------------------------
crossref_csv = os.path.join(export_dir, "cross_reference.csv")
crossref_ok = False
try:
    cross_ref = proj.get_cross_reference()
    with open(crossref_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Variable", "Location", "Type", "Access", "POU", "Line"])
        for e in cross_ref:
            # Some builds expose different attribute names; try safely
            name  = getattr(e, "name", "")
            loc   = getattr(e, "location", "")
            typ   = getattr(e, "type", "")
            acc   = getattr(e, "access", "")
            pou   = getattr(e, "pou", "")
            line  = getattr(e, "line", "")
            w.writerow([name, loc, typ, acc, pou, line])
    crossref_ok = True
    print("Cross reference exported:", crossref_csv)
except Exception as ex:
    print("Note: Could not export cross reference via API on this build. Skipping. Error:", ex)

# -----------------------------
# 2) Build POU call graph CSV from PLCopen XML
# -----------------------------
# Strategy:
#  - Auto-discover the newest .xml in project root or Exports
#  - Parse <project>/<types>/<pous>/<pou name=...>
#  - For each POU:
#      ST: parse <body><ST> text -> detect calls to other POUs
#      FBD/CFC: parse <body><FBD|CFC> blocks' <typeName> as callees

search_dirs = [proj_dir, export_dir]
PLCOPEN_XML_HINT = None  # You can hard-set e.g.: r"C:\...\your_export.xml"

xml_path = PLCOPEN_XML_HINT or find_latest_xml(search_dirs)
if xml_path is None:
    raise Exception("No PLCopen XML export was found in the project folder or Exports. Please export your project to PLCopen XML and place it there.")

print("Using PLCopen XML:", xml_path)

doc = read_xml(xml_path)
nsm = ns_manager(doc)

# Gather POU names
pou_nodes = doc.SelectNodes("//plc:project/plc:types/plc:pous/plc:pou", nsm)
if pou_nodes is None or pou_nodes.Count == 0:
    # Some exports nest differently; try a more general lookup
    pou_nodes = doc.SelectNodes("//plc:pou", nsm)

pou_names = set()
for pn in pou_nodes:
    nm = pn.GetAttribute("name")
    if nm:
        pou_names.add(nm)

edges = set()

for pn in pou_nodes:
    caller = pn.GetAttribute("name")
    if not caller:
        continue

    # ST bodies
    st_nodes = pn.SelectNodes(".//plc:ST", nsm)
    for st in st_nodes or []:
        # ST may embed XHTML. Gather all text
        st_text = st.InnerText or ""
        # Detect calls to known POUs
        callees = detect_calls_in_st(st_text, pou_names)
        for c in callees:
            if c != caller:
                edges.add((caller, c))

    # FBD/CFC bodies
    for lang in ("FBD", "CFC"):
        body_nodes = pn.SelectNodes(".//plc:%s" % lang, nsm)
        for body in body_nodes or []:
            callees = detect_calls_in_fbd(body, nsm)
            for c in callees:
                if c != caller:
                    edges.add((caller, c))

# Write CSV
callgraph_csv = os.path.join(export_dir, "pou_call_graph.csv")
with open(callgraph_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Caller", "Callee"])
    for a, b in sorted(edges):
        w.writerow([a, b])

print("POU call graph exported:", callgraph_csv)

# Also write Mermaid
mermaid_path = os.path.join(export_dir, "call_graph.mmd")
with open(mermaid_path, "w", encoding="utf-8") as f:
    f.write("graph TD\n")
    for a, b in sorted(edges):
        f.write("    %s --> %s\n" % (sanitize_identifier(a), sanitize_identifier(b)))

print("Mermaid call graph exported:", mermaid_path)

print("All done. Outputs are in:", export_dir)

