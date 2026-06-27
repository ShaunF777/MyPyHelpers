import re
import xml.etree.ElementTree as ET

def clean_and_convert_xml(xml_string):
    # Fix Reason 1: Replace non-breaking spaces (\xa0) with standard spaces
    cleaned_string = xml_string.replace('\xa0', ' ')
    
    # Remove xi:include lines so the XML parser doesn't crash on missing web assets
    cleaned_string = re.sub(r'<xi:include[^>]*/>', '', cleaned_string)
    cleaned_string = re.sub(r'<J1939>.*?</J1939>', '', cleaned_string, flags=re.DOTALL)
     
    try:
        root = ET.fromstring(cleaned_string)
        
        # Fix Reason 2 & 3: Turn raw configuration data into a conversational narrative
        markdown_output = "# IoT Oil Monitoring Setup Configuration\n\n"
        
        # Extract Value Definitions
        markdown_output += "## Monitored Telemetry Data Fields:\n"
        for val in root.findall('.//{http://xml.proemion.com/ProemionDataConfiguration/2012/07}ValueDefinition'):
            key = val.get('key', 'Unknown')
            label_elem = val.find('./{http://xml.proemion.com/ProemionDataConfiguration/2012/07}description/{http://xml.proemion.com/ProemionDataConfiguration/2012/07}Label')
            label = label_elem.get('value') if label_elem is not None else "No Description"
            unit_elem = val.find('./{http://xml.proemion.com/ProemionDataConfiguration/2012/07}unit')
            unit = unit_elem.text if unit_elem is not None else "No Unit"
            
            markdown_output += f"- **Field:** {label}\n  - ID: `{key}`\n  - Unit Type: `{unit}`\n\n"
            
        return markdown_output
         
    except ET.ParseError as e:
        return f"Parser Error: {e}. Please ensure XML tags match."

# Read the XML file
with open(r'C:\00. Documents\MyPyHelpers\XMLScrubber\data\Oilfillv10.47.txt', 'r', encoding='utf-8') as f:
    raw_xml = f.read()

# Generate NotebookLM-friendly markdown documentation
clean_markdown = clean_and_convert_xml(raw_xml)

# Save this output as 'config_documentation.md' or 'config.txt' and upload that to NotebookLM!
with open(r'C:\00. Documents\MyPyHelpers\XMLScrubber\data\Oilfillv10.47_scrubbed.md', 'w', encoding='utf-8') as f:
    f.write(clean_markdown)

print("Scrubbing complete! Output saved to Oilfillv10.47_scrubbed.md")
print("First 500 characters of output:")
print(clean_markdown[:500])