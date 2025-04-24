import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm
import sys

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
    params = {"verb": verb}
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
                for record in root.findall('.//pico:record', ns):
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

                    # Stop fetching if test limit is reached
                    if test_limit and len(records) >= test_limit:
                        print("\nTest limit reached. Stopping fetch.")
                        return records
                
                return records
            else:
                # For other verbs, return the raw XML response
                return ET.tostring(root, encoding="unicode")

    except Exception as e:
        print(f"Error during fetching data: {e}")
        sys.exit(1)