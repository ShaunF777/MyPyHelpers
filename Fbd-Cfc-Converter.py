# -*- coding: utf-8 -*-
"""
Convert FBD and CFC POUs from PLCopen XML to Structured Text (.st files)
Author: Shaun Fourie
"""

import os
import xml.etree.ElementTree as ET

def detect_namespace(root):
    """Extract the default namespace from the root tag."""
    if root.tag.startswith("{"):
        return root.tag.split("}")[0].strip("{")
    return ""

def parse_pous(xml_path, output_dir):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {"plc": detect_namespace(root)}

    # Find all POUs
    for pou in root.findall(".//plc:pou", ns):
        name = pou.get("name")
        body_fbd = pou.find(".//plc:FBD", ns)
        body_cfc = pou.find(".//plc:CFC", ns)

        if body_fbd is not None or body_cfc is not None:
            print(f"Converting {name}...")
            st_code = convert_graphical_to_st(pou, ns)
            save_st_file(output_dir, name, st_code)

def convert_graphical_to_st(pou_elem, ns):
    """Convert a single POU's FBD/CFC body to ST code."""
    lines = []
    # Extract variable declarations from interface
    interface = pou_elem.find("plc:interface", ns)
    if interface is not None:
        lines.extend(parse_interface(interface, ns))
    
    # Convert graphical body
    for lang in ("FBD", "CFC"):
        body = pou_elem.find(f".//plc:{lang}", ns)
        if body is not None:
            lines.extend(parse_blocks(body, ns))
    return "\n".join(lines)

def parse_interface(interface_elem, ns):
    """Generate ST VAR sections from interface."""
    lines = []
    for section_tag, st_section in [
        ("inputVars", "VAR_INPUT"),
        ("outputVars", "VAR_OUTPUT"),
        ("inOutVars", "VAR_IN_OUT"),
        ("localVars", "VAR")
    ]:
        section = interface_elem.find(f"plc:{section_tag}", ns)
        if section is not None:
            lines.append(st_section)
            for var in section.findall("plc:variable", ns):
                vname = var.get("name")
                vtype_elem = var.find("plc:type", ns)
                vtype = None
                if vtype_elem is not None and len(vtype_elem) > 0:
                    vtype = vtype_elem[0].tag.split("}")[-1]
                lines.append(f"    {vname} : {vtype};")
            lines.append("END_" + st_section)
    return lines

def parse_blocks(body_elem, ns):
    """Convert FBD/CFC blocks to ST calls."""
    lines = []
    for block in body_elem.findall(".//plc:block", ns):
        fb_name = block.find("plc:typeName", ns).text
        call_parts = []
        # Inputs
        for var in block.findall(".//plc:inputVariables/plc:variable", ns):
            pname = var.get("formalParameter")
            conn = var.find(".//plc:connectionPointIn/plc:connection", ns)
            if conn is not None:
                target = conn.get("refLocalId") or ""
                call_parts.append(f"{pname} := {target}")
        # Outputs
        for var in block.findall(".//plc:outputVariables/plc:variable", ns):
            pname = var.get("formalParameter")
            conn = var.find(".//plc:connectionPointOut/plc:connection", ns)
            if conn is not None:
                target = conn.get("refLocalId") or ""
                call_parts.append(f"{pname} => {target}")
        # Build ST call
        if call_parts:
            lines.append(f"{fb_name}(\n    " + ",\n    ".join(call_parts) + "\n);")
        else:
            lines.append(f"{fb_name}();")
    return lines

def save_st_file(output_dir, name, st_code):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{name}.st")
    with open(path, "w", encoding="utf-8") as f:
        f.write(st_code)
    print(f"Saved {path}")

if __name__ == "__main__":
    xml_file = r"C:\path\to\your\exported.xml"
    output_folder = r"C:\path\to\st_output"
    parse_pous(xml_file, output_folder)