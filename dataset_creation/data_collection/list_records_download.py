import requests
import xml.etree.ElementTree as ET
import csv
import sys
from tqdm import tqdm
import argparse
from xml.dom.minidom import parseString
import os

# Define a dictionary of available endpoints with short options
ENDPOINTS = {
    "a": "https://www.culturaitalia.it/oaiProviderCI/OAIHandler",
    "b": "https://example1.com/oai",
    "c": "https://example2.com/oai"
}

# Define a dictionary of OAI-PMH verbs with numeric arguments
VERBS = {
    "1": "Identify",
    "2": "ListIdentifiers",
    "3": "ListMetadataFormats",
    "4": "ListSets",
    "5": "ListRecords"  # Default verb
}

def strip_namespace(element):
    """
    Remove namespaces from an XML element and its children.

    Args:
        element (xml.etree.ElementTree.Element): The XML element to process.

    Returns:
        xml.etree.ElementTree.Element: The XML element without namespaces.
    """
    for elem in element.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]  # Remove namespace
        elem.attrib = {key.split('}', 1)[-1]: value for key, value in elem.attrib.items()}  # Remove namespace from attributes
    return element

def save_raw_output(output, output_file, stylesheet=None):
    """
    Save raw output (e.g., XML) to a file with proper formatting and optional XSL stylesheet.

    Args:
        output (str): The raw XML output to save.
        output_file (str): The file to save the output to.
        stylesheet (str, optional): The path to an XSL stylesheet to include in the XML.
    """
    try:
        # Parse the XML and strip namespaces
        root = ET.fromstring(output)
        root = strip_namespace(root)

        # Convert the cleaned XML back to a string
        cleaned_xml = ET.tostring(root, encoding="unicode")

        # Pretty-print the XML
        dom = parseString(cleaned_xml)
        pretty_xml = dom.toprettyxml(indent="  ")

        # Add XML declaration and optional stylesheet
        xml_declaration = '<?xml version="1.0" encoding="UTF-8" ?>\n'
        if stylesheet:
            xml_declaration += f'<?xml-stylesheet type="text/xsl" href="{stylesheet}"?>\n'

        # Combine the declaration, stylesheet, and formatted XML
        formatted_output = xml_declaration + pretty_xml

        # Save the formatted XML to the file
        with open(output_file, mode='w', encoding='utf-8') as file:
            file.write(formatted_output)
    except Exception as e:
        print(f"Error saving raw output to file: {e}")
        sys.exit(1)

def save_to_xml(records, output_file, stylesheet=None):
    """
    Save records to an XML file with optional XSL stylesheet.

    Args:
        records (list): The list of records to save.
        output_file (str): The file to save the XML output to.
        stylesheet (str, optional): The path to an XSL stylesheet to include in the XML.
    """
    try:
        # Create the root element
        root = ET.Element("ListRecords")

        # Add each record as a child element
        for record in records:
            record_elem = ET.SubElement(root, "record")
            for key, value in record.items():
                child = ET.SubElement(record_elem, key)
                child.text = value

        # Convert the XML tree to a string
        cleaned_xml = ET.tostring(root, encoding="unicode")

        # Pretty-print the XML
        dom = parseString(cleaned_xml)
        pretty_xml = dom.toprettyxml(indent="  ")

        # Add XML declaration and optional stylesheet
        xml_declaration = '<?xml version="1.0" encoding="UTF-8" ?>\n'
        if stylesheet:
            xml_declaration += f'<?xml-stylesheet type="text/xsl" href="{stylesheet}"?>\n'

        # Combine the declaration, stylesheet, and formatted XML
        formatted_output = xml_declaration + pretty_xml

        # Save the formatted XML to the file
        with open(output_file, mode='w', encoding='utf-8') as file:
            file.write(formatted_output)
    except Exception as e:
        print(f"Error saving records to XML: {e}")
        sys.exit(1)

def fetch_records(endpoint, verb, set_name=None, metadata_prefix="pico", test_limit=None):
    """
    Fetch records or perform other OAI-PMH operations from the endpoint.

    Args:
        endpoint (str): The OAI-PMH endpoint URL.
        verb (str): The OAI-PMH verb to use (e.g., "ListRecords").
        set_name (str, optional): The dataset name (set) for "ListRecords" or "ListIdentifiers".
        metadata_prefix (str, optional): The metadata prefix (default: "pico").
        test_limit (int, optional): Limit the number of records fetched for testing purposes.

    Returns:
        list or str: A list of fetched records (for ListRecords) or raw XML output (for other verbs).
    """
    records = []
    params = {
        "verb": verb
    }
    if set_name and verb in ["ListRecords", "ListIdentifiers"]:
        params["set"] = set_name
    if metadata_prefix and verb in ["ListRecords", "ListIdentifiers"]:
        params["metadataPrefix"] = metadata_prefix

    try:
        with tqdm(desc=f"Fetching {verb.lower()}", unit="record", bar_format="{l_bar}{bar}| {n_fmt} records [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
            response = requests.get(endpoint, params=params)
            if response.status_code != 200:
                print(f"Error: Unable to fetch data. HTTP Status Code: {response.status_code}")
                sys.exit(1)
            
            root = ET.fromstring(response.content)
            ns = {
                'oai': 'http://www.openarchives.org/OAI/2.0/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'pico': 'http://purl.org/pico/1.0/',
                'dcterms': 'http://purl.org/dc/terms/'
            }
            
            if verb == "ListRecords":
                found_records = False
                for record in root.findall('.//pico:record', ns):  # Adjusted to find <pico:record>
                    identifier = record.find('dc:identifier', ns)
                    title = record.find('dc:title', ns)
                    description = record.find('dc:description', ns)
                    
                    # Handle multiple dc:subject elements
                    subjects = record.findall('dc:subject', ns)
                    subject_values = "; ".join(subject.text or "" for subject in subjects if subject is not None)
                    
                    # Handle multiple dc:type elements
                    types = record.findall('dc:type', ns)
                    type_values = "; ".join(type_.text or "" for type_ in types if type_ is not None)
                    
                    records.append({
                        "identifier": identifier.text if identifier is not None else "",
                        "title": title.text if title is not None else "",
                        "description": description.text if description is not None else "",
                        "type": type_values,
                        "subject": subject_values
                    })
                    pbar.update(1)
                    found_records = True

                    # Stop fetching if test limit is reached
                    if test_limit and len(records) >= test_limit:
                        print("\nTest limit reached. Stopping fetch.")
                        return records
                
                if not found_records:
                    print("No records found.")
                return records
            else:
                # For other verbs, return the raw XML response
                return ET.tostring(root, encoding="unicode")

    except Exception as e:
        print(f"Error during fetching data: {e}")
        sys.exit(1)

def save_to_csv(records, output_file):
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

def main():
    parser = argparse.ArgumentParser(
        description="Fetch and save records or perform other OAI-PMH operations.",
        epilog="Available endpoints:\n" + "\n".join([f"-{key}: {url}" for key, url in ENDPOINTS.items()]) +
               "\n\nAvailable verbs:\n" + "\n".join([f"-{key}: {verb}" for key, verb in VERBS.items()]),
        formatter_class=argparse.RawTextHelpFormatter  # Preserve formatting in the help message
    )
    parser.add_argument("dataset_name", nargs="?", help="The name of the dataset to fetch (required for ListRecords and ListIdentifiers).")
    parser.add_argument("output_file", help="The file to save the fetched data.")
    parser.add_argument(
        "-e", "--endpoint",
        choices=ENDPOINTS.keys(),
        required=True,
        help="The endpoint to fetch data from. Choose from the available endpoints."
    )
    parser.add_argument(
        "-v", "--verb",
        choices=VERBS.keys(),
        required=True,
        help="The OAI-PMH verb to use. Choose from the available verbs."
    )
    parser.add_argument("--test", action="store_true", help="Limit the fetch to 20 records for testing purposes.")
    parser.add_argument("--save-xml", action="store_true", help="Save the ListRecords output as an XML file.")
    args = parser.parse_args()
    
    # Determine the selected endpoint and verb
    endpoint = ENDPOINTS[args.endpoint]
    verb = VERBS[args.verb]
    dataset_name = args.dataset_name
    output_file = args.output_file
    test_limit = 20 if args.test else None  # Set test limit to 20 if --test is specified
    
    if verb in ["ListRecords", "ListIdentifiers"] and not dataset_name:
        print(f"Error: The dataset_name argument is required for the '{verb}' verb.")
        sys.exit(1)
    
    print(f"Fetching data using verb '{verb}' from endpoint: {endpoint}")
    result = fetch_records(endpoint, verb, set_name=dataset_name, test_limit=test_limit)
    
    if verb == "ListRecords":
        print(f"Fetched {len(result)} records.")
        print(f"Saving records to {output_file}")
        save_to_csv(result, output_file)

        # Save as XML if the --save-xml flag is provided
        if args.save_xml:
            xml_output_file = output_file.replace(".csv", ".xml")
            xslt_path = os.path.join("xslt", "oai2.xsl")
            print(f"Saving records to {xml_output_file} with stylesheet {xslt_path}")
            save_to_xml(result, xml_output_file, stylesheet=xslt_path)
    else:
        # Use the XSLT file for styling
        xslt_path = os.path.join("xslt", "oai2.xsl")
        print(f"Saving raw output to {output_file} with stylesheet {xslt_path}")
        save_raw_output(result, output_file, stylesheet=xslt_path)
    
    print("Done.")

if __name__ == "__main__":
    main()
