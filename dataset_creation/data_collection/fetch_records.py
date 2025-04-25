import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm
import sys

def fetch_records(endpoint, verb, set_name=None, test_limit=None, resumption_token=None):
    """
    Fetch records from the OAI-PMH endpoint.

    Args:
        endpoint (str): The OAI-PMH endpoint URL.
        verb (str): The OAI-PMH verb to use (e.g., "ListRecords").
        set_name (str, optional): The dataset name (set) to filter records.
        test_limit (int, optional): Limit the number of records for testing.
        resumption_token (str, optional): Token for fetching the next batch of records.

    Returns:
        tuple: A tuple containing the fetched records and the next resumption token (if any).
    """
    params = {"verb": verb}
    if resumption_token:
        params["resumptionToken"] = resumption_token
    else:
        if set_name:
            params["set"] = set_name
        params["metadataPrefix"] = "oai_dc"  # Default metadata format

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching records: {e}")
        sys.exit(1)

    # Parse the XML response
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
        sys.exit(1)

    # Extract records
    records = []
    for record in root.findall(".//{http://www.openarchives.org/OAI/2.0/}record"):
        metadata = record.find(".//{http://www.openarchives.org/OAI/2.0/}metadata")
        if metadata is not None:
            records.append(ET.tostring(metadata, encoding="unicode"))

    # Extract resumptionToken
    resumption_token_element = root.find(".//{http://www.openarchives.org/OAI/2.0/}resumptionToken")
    next_resumption_token = resumption_token_element.text if resumption_token_element is not None else None

    return records, next_resumption_token