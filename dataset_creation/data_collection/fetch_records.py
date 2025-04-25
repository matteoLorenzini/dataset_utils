import requests
import xml.etree.ElementTree as ET
import sys
from tqdm import tqdm

def fetch_records(endpoint, set_name, verb="ListRecords", metadata_prefix="oai_dc", test_limit=None):
    records = []
    params = {
        "verb": verb,
        "metadataPrefix": metadata_prefix,
        "set": set_name
    }
    
    try:
        with tqdm(desc="Fetching records", unit="record", bar_format="{l_bar}{bar}| {n_fmt} records [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
            while True:
                response = requests.get(endpoint, params=params)
                if response.status_code != 200:
                    print(f"Error: Unable to fetch records. HTTP Status Code: {response.status_code}")
                    sys.exit(1)
                
                root = ET.fromstring(response.content)
                ns = {
                    'oai': 'http://www.openarchives.org/OAI/2.0/',
                    'dc': 'http://purl.org/dc/elements/1.1/'
                }
                
                found_records = False
                for record in root.findall('.//oai:record', ns):
                    metadata = record.find('oai:metadata', ns)
                    if metadata is not None:
                        dc = metadata.find('dc:dc', ns)
                        if dc is not None:
                            title = dc.find('dc:title', ns)
                            description = dc.find('dc:description', ns)
                            subjects = dc.findall('dc:subject', ns)
                            subject_values = "; ".join(subject.text for subject in subjects if subject is not None)
                            types = dc.findall('dc:type', ns)
                            type_values = "; ".join(type_.text for type_ in types if type_ is not None)
                            
                            records.append({
                                "title": title.text if title is not None else "",
                                "description": description.text if description is not None else "",
                                "type": type_values,
                                "subject": subject_values
                            })
                            pbar.update(1)
                            found_records = True

                            # Stop if test limit is reached
                            if test_limit and len(records) >= test_limit:
                                return records
                
                if not found_records:
                    break
                
                resumption_token = root.find('.//oai:resumptionToken', ns)
                if resumption_token is None or resumption_token.text is None:
                    break
                params = {
                    "verb": "ListRecords",
                    "resumptionToken": resumption_token.text
                }
    except Exception as e:
        print(f"Error during fetching records: {e}")
        sys.exit(1)
    
    return records