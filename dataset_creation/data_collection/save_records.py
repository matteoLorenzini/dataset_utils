import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import csv
import sys
import os

def save_to_xml(records, output_file, stylesheet=None):
    """
    Save records to an XML file with an optional XSL stylesheet.
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

        # Convert the XML tree to a string
        cleaned_xml = ET.tostring(root, encoding="unicode")
        dom = parseString(cleaned_xml)
        pretty_xml = dom.toprettyxml(indent="  ")

        # Add optional XSL stylesheet
        if stylesheet:
            stylesheet_declaration = f'<?xml-stylesheet type="text/xsl" href="{stylesheet}"?>\n'
            pretty_xml = pretty_xml.replace('<?xml version="1.0" encoding="UTF-8"?>', f'<?xml version="1.0" encoding="UTF-8"?>\n{stylesheet_declaration}')

        # Save the formatted XML to the file
        with open(output_file, mode='w', encoding='utf-8') as file:
            file.write(pretty_xml)
    except Exception as e:
        print(f"Error saving records to XML: {e}")
        sys.exit(1)

def save_to_csv(records, output_file):
    """
    Save records to a CSV file.
    """
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["title", "description", "type", "subject"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for record in records:
                writer.writerow(record)
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        sys.exit(1)