import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import csv
import sys

def save_to_xml(records, output_file, stylesheet=None):
    """
    Save records to an XML file with optional XSL stylesheet.
    """
    try:
        root = ET.Element("ListRecords")
        for record in records:
            record_elem = ET.SubElement(root, "record")
            for key, value in record.items():
                if key in ["type", "subject"] and value:
                    for item in value.split("; "):
                        child = ET.SubElement(record_elem, key)
                        child.text = item
                else:
                    child = ET.SubElement(record_elem, key)
                    child.text = value

        cleaned_xml = ET.tostring(root, encoding="unicode")
        dom = parseString(cleaned_xml)
        pretty_xml = dom.toprettyxml(indent="  ")

        xml_declaration = '<?xml version="1.0" encoding="UTF-8" ?>\n'
        if stylesheet:
            xml_declaration += f'<?xml-stylesheet type="text/xsl" href="{stylesheet}"?>\n'

        formatted_output = xml_declaration + pretty_xml
        with open(output_file, mode='w', encoding='utf-8') as file:
            file.write(formatted_output)
    except Exception as e:
        print(f"Error saving records to XML: {e}")
        sys.exit(1)

def save_to_csv(records, output_file):
    """
    Save records to a CSV file.
    """
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["identifier", "title", "description", "type", "subject"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        sys.exit(1)