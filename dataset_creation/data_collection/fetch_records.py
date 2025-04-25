import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm
import sys

def fetch_records(endpoint, verb, set_name=None, test_limit=None, resumption_token=None):
    """
    Fetch records from the OAI-PMH endpoint.
    """
    params = {"verb": verb}
    if resumption_token:
        params["resumptionToken"] = resumption_token
    else:
        if set_name:
            params["set"] = set_name
        params["metadataPrefix"] = "oai_dc"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(endpoint, params=params, headers=headers)
        print(f"Request URL: {response.url}")  # Debugging: Print the full request URL
        print(f"Request Headers: {response.request.headers}")  # Debugging: Print request headers
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.reason}")
        print(f"Response Content: {response.text}")  # Print the full response content
        print(f"Request URL: {response.url}")  # Print the full request URL
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching records: {e}")
        sys.exit(1)

    # Parse the XML response
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
        sys.exit(1)

    # Extract records and resumptionToken
    records = []
    for record in root.findall(".//{http://www.openarchives.org/OAI/2.0/}record"):
        metadata = record.find(".//{http://www.openarchives.org/OAI/2.0/}metadata")
        if metadata is not None:
            records.append(ET.tostring(metadata, encoding="unicode"))

    resumption_token_element = root.find(".//{http://www.openarchives.org/OAI/2.0/}resumptionToken")
    next_resumption_token = resumption_token_element.text if resumption_token_element is not None else None

    return records, next_resumption_token