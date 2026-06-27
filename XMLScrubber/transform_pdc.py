import re

def transform_pdc(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 3: Increment version
    content = content.replace('customerVersion="00.00.08"', 'customerVersion="00.00.09"')

    # Step 4: Remove old FleetType ValueDefinitions and add new consolidated one
    old_fleettype_ids = [
        'valdef.cb814b6b-fae0-4ea7-b545-9302cee0098c',
        'valdef.587ff346-938a-4202-9f59-4e0e928fa619',
        'valdef.75f43596-8cbb-4f00-964b-1c1d694baf62',
        'valdef.c7c374f6-0f40-4866-a267-5fde8cf3903e',
        'valdef.02a140b7-293c-4fba-a877-46ae292943d6',
        'valdef.136a6f90-e55c-4ddb-8303-0ef0b2a53981',
        'valdef.e6247ecc-5edc-4eae-8e2b-a0cf51563be8',
        'valdef.c0674cb9-80dc-4701-a8e7-c46be32e41d5',
    ]
    
    new_value_def = '''    <ValueDefinition key="valdef.FleetType_Full" managedByDataPlatform="false">
      <description xsi:type="MessageReference" value="label.FleetType_Full"/>
      <unit>predefined.unit.TEXT</unit>
    </ValueDefinition>'''
    
    for vid in old_fleettype_ids:
        pattern = rf'\s*<ValueDefinition key="{vid}">[\s\S]*?</ValueDefinition>\n'
        content = re.sub(pattern, '', content)

    # Insert the new ValueDefinition after the Screen Voltage entry
    insert_after = r'(.*<ValueDefinition key="valdef.772cc014-f255-4b02-8f56-6c710580faf9">[\s\S]*?</ValueDefinition>)'
    match = re.search(insert_after, content)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + '\n' + new_value_def + content[insert_pos:]

    # Step 5: Remove CanMessage entries for CAN IDs 0x76-0x7C
    for can_id in ['0x76', '0x77', '0x78', '0x79', '0x7A', '0x7B', '0x7C']:
        pattern = rf'\s*<CanMessage[^>]*canId="{can_id}"[^>]*>[\s\S]*?</CanMessage>\n'
        content = re.sub(pattern, '', content)

    # Step 5: Modify the CanMessage for 0x75 to use SimpleCharValue
    old_0x75 = '''<CanMessage protocolStyle="GENERIC" mask="0x7ff" canIdLength="29" canId="0x75">
        <Values>
          <IntValue startPos="0" endianness="LITTLE" length="8">
            <valueDefinition ref="valdef.cb814b6b-fae0-4ea7-b545-9302cee0098c" />
          </IntValue>
        </Values>
      </CanMessage>'''
    
    new_0x75 = '''<CanMessage canId="0x75" canIdLength="11" protocolStyle="GENERIC">
        <Values>
          <!-- startPos 0 (bit 0), charset US-ASCII, length 8 CHARs (64 bits) -->
          <SimpleCharValue startPos="0" charset="US-ASCII" continueOnLastPostion="false">
            <valueDefinition ref="valdef.FleetType_Full"/>
            <length type="CHAR" value="8"/>
          </SimpleCharValue>
        </Values>
      </CanMessage>'''
    
    content = content.replace(old_0x75, new_0x75)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    input_file = r'C:\00. Documents\MyPyHelpers\XMLScrubber\data\Oilfillv10.47.pdc'
    output_file = r'C:\00. Documents\MyPyHelpers\XMLScrubber\data\Oilfillv10.47_modified.pdc'
    transform_pdc(input_file, output_file)
    print(f'Transformed file saved to {output_file}')