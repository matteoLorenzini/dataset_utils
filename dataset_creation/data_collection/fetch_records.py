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
        if test_limit:
            params["metadataPrefix"] = "oai_dc"
            params["test_limit"] = test_limit  # Custom parameter for testing

    response = requests.get(endpoint, params=params)
    response.raise_for_status()

    # Parse the response (assuming XML response)
    records = []  # Extract records from the response
    next_resumption_token = None  # Extract resumptionToken from the response if present

    # Example parsing logic (you need to implement actual XML parsing)
    # Use an XML parser like xml.etree.ElementTree or lxml to extract data
    # records = parse_records(response.content)
    # next_resumption_token = parse_resumption_token(response.content)

    return records, next_resumption_token