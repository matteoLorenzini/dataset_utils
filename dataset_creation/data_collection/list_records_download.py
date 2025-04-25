import requests
import xml.etree.ElementTree as ET
import csv
import sys
from tqdm import tqdm
import argparse
from xml.dom.minidom import parseString
import os
import glob

# Use pyreadline3 on Windows, readline on other platforms
if os.name == "nt":
    try:
        import pyreadline3 as readline
    except ImportError:
        print("pyreadline3 is not installed. Install it using 'pip install pyreadline3'.")
        sys.exit(1)
else:
    import readline

def complete_path(text, state):
    """
    Autocomplete function for directory paths.
    """
    matches = glob.glob(text + '*')
    return matches[state] if state < len(matches) else None

# Enable tab-completion for input
if os.name != "nt":
    # On Unix-like systems, use readline to enable tab-completion
    readline.set_completer(complete_path)
    readline.parse_and_bind("tab: complete")

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
        list: A list of fetched records.
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
            while True:
                response = requests.get(endpoint, params=params)
                if response.status_code != 200:
                    print(f"Error: Unable to fetch data. HTTP Status Code: {response.status_code}")
                    sys.exit(1)

                root = ET.fromstring(response.content)
                ns = {
                    'oai': 'http://www.openarchives.org/OAI/2.0/',
                    'dc': 'http://purl.org/dc/elements/1.1/',
                    'pico': 'http://purl.org/pico/1.0/'
                }

                if verb == "ListRecords":
                    for record in root.findall('.//oai:record', ns):
                        metadata = record.find('oai:metadata', ns)
                        if metadata is not None:
                            pico_record = metadata.find('pico:record', ns)
                            if pico_record is not None:
                                identifier = pico_record.find('dc:identifier', ns)
                                title = pico_record.find('dc:title', ns)
                                description = pico_record.find('dc:description', ns)

                                # Handle multiple dc:subject elements
                                subjects = pico_record.findall('dc:subject', ns)
                                subject_values = "; ".join(subject.text or "" for subject in subjects if subject is not None)

                                # Handle multiple dc:type elements
                                types = pico_record.findall('dc:type', ns)
                                type_values = "; ".join(type_.text or "" for type_ in types if type_ is not None)

                                records.append({
                                    "identifier": identifier.text if identifier is not None else "",
                                    "title": title.text if title is not None else "",
                                    "description": description.text if description is not None else "",
                                    "type": type_values,
                                    "subject": subject_values
                                })
                                pbar.update(1)

                                # Stop fetching if test limit is reached
                                if test_limit and len(records) >= test_limit:
                                    print("\nTest limit reached. Stopping fetch.")
                                    return records

                    # Check for resumptionToken for pagination
                    resumption_token = root.find('.//oai:resumptionToken', ns)
                    if resumption_token is None or resumption_token.text is None:
                        break
                    params = {
                        "verb": "ListRecords",
                        "resumptionToken": resumption_token.text
                    }
                else:
                    # For other verbs, return the raw XML response
                    return ET.tostring(root, encoding="unicode")

    except Exception as e:
        print(f"Error during fetching data: {e}")
        sys.exit(1)

    return records

def save_to_csv(records, output_file):
    """
    Save records to a CSV file.

    Args:
        records (list): The list of records to save.
        output_file (str): The file to save the CSV output to.
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
                if key in ["type", "subject"] and value:  # Handle splitting for 'type' and 'subject'
                    for item in value.split("; "):  # Split by "; " and create separate tags
                        child = ET.SubElement(record_elem, key)
                        child.text = item
                else:
                    child = ET.SubElement(record_elem, key)
                    child.text = value

        # Convert the XML tree to a string
        cleaned_xml = ET.tostring(root, encoding="unicode")

        # Pretty-print the XML
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

def main():
    print("Welcome to the OAI-PMH Records Fetcher Wizard!")

    # Step 1: Select the endpoint
    print("\nStep 1: Select the endpoint:")
    for key, url in ENDPOINTS.items():
        print(f"  {key}: {url}")
    endpoint_key = input("Enter the endpoint key (default: 'a'): ").strip().lower() or "a"
    if endpoint_key not in ENDPOINTS:
        print("Invalid endpoint key. Exiting.")
        sys.exit(1)
    endpoint = ENDPOINTS[endpoint_key]

    # Step 2: Select the verb
    print("\nStep 2: Select the OAI-PMH verb:")
    for key, verb in VERBS.items():
        print(f"  {key}: {verb}")
    verb_key = input("Enter the verb key (default: '5' for ListRecords): ").strip() or "5"
    if verb_key not in VERBS:
        print("Invalid verb key. Exiting.")
        sys.exit(1)
    verb = VERBS[verb_key]

    # Step 3: Enter the dataset name (optional)
    dataset_name = input("\nStep 3: Enter the dataset name (optional, press Enter to skip): ").strip() or None

    # Step 4: Enter the directory path for saving the output
    output_dir = input("\nStep 4: Enter the directory path to save the output (default: current directory): ").strip() or "."
    if not os.path.exists(output_dir):
        print(f"Directory '{output_dir}' does not exist. Exiting.")
        sys.exit(1)

    # Step 5: Enter the output file name
    output_file = input("\nStep 5: Enter the output file name (default: 'output'): ").strip() or "output"

    # Step 6: Choose test mode
    test_mode = input("\nStep 6: Enable test mode? (y/n, default: 'n'): ").strip().lower() == "y"

    # Step 7: Choose output formats
    save_xml = input("\nStep 7: Save as XML? (y/n, default: 'n'): ").strip().lower() == "y"
    save_csv = input("Save as CSV? (y/n, default: 'n'): ").strip().lower() == "y"

    # Confirm the selections
    print("\nSummary of your selections:")
    print(f"  Endpoint: {endpoint}")
    print(f"  Verb: {verb}")
    print(f"  Dataset Name: {dataset_name}")
    print(f"  Output Directory: {output_dir}")
    print(f"  Output File: {output_file}")
    print(f"  Test Mode: {'Enabled' if test_mode else 'Disabled'}")
    print(f"  Save as XML: {'Yes' if save_xml else 'No'}")
    print(f"  Save as CSV: {'Yes' if save_csv else 'No'}")

    confirm = input("\nDo you want to proceed? (y/n, default: 'y'): ").strip().lower() or "y"
    if confirm != "y":
        print("Operation canceled.")
        sys.exit(0)

    # Fetch records or perform the requested OAI-PMH operation
    print(f"\nFetching data from endpoint: {endpoint} with verb: {verb}")
    if verb == "ListRecords":
        records = fetch_records(endpoint, verb, set_name=dataset_name, test_limit=20 if test_mode else None)
        if save_xml:
            xml_output_file = os.path.join(output_dir, output_file if output_file.endswith(".xml") else f"{output_file}.xml")
            print(f"Saving records as XML to {xml_output_file}")
            save_to_xml(records, xml_output_file)
        if save_csv:
            csv_output_file = os.path.join(output_dir, output_file if output_file.endswith(".csv") else f"{output_file}.csv")
            print(f"Saving records as CSV to {csv_output_file}")
            save_to_csv(records, csv_output_file)
    else:
        # For other verbs, fetch raw XML output
        raw_output = fetch_records(endpoint, verb, set_name=dataset_name)
        if save_xml:
            xml_output_file = os.path.join(output_dir, output_file if output_file.endswith(".xml") else f"{output_file}.xml")
            print(f"Saving raw output as XML to {xml_output_file}")
            save_raw_output(raw_output, xml_output_file)

    print("\nOperation completed successfully.")

if __name__ == "__main__":
    main()