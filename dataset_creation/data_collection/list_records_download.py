import argparse
import os
from fetch_records import fetch_records
from save_records import save_to_csv, save_to_xml

ENDPOINTS = {
    "a": "https://www.culturaitalia.it/oaiProviderCI/OAIHandler",
    "b": "https://example1.com/oai",
    "c": "https://example2.com/oai"
}

VERBS = {
    "1": "Identify",
    "2": "ListIdentifiers",
    "3": "ListMetadataFormats",
    "4": "ListSets",
    "5": "ListRecords"
}

def main():
    parser = argparse.ArgumentParser(description="Fetch and save records or perform other OAI-PMH operations.")
    parser.add_argument("dataset_name", nargs="?", help="The name of the dataset to fetch.")
    parser.add_argument("output_file", help="The file to save the fetched data.")
    parser.add_argument("-e", "--endpoint", choices=ENDPOINTS.keys(), required=True, help="The endpoint to fetch data from.")
    parser.add_argument("-v", "--verb", choices=VERBS.keys(), required=True, help="The OAI-PMH verb to use.")
    parser.add_argument("--test", action="store_true", help="Limit the fetch to 20 records for testing purposes.")
    parser.add_argument("--save-xml", action="store_true", help="Save the ListRecords output as an XML file.")
    args = parser.parse_args()

    endpoint = ENDPOINTS[args.endpoint]
    verb = VERBS[args.verb]
    dataset_name = args.dataset_name
    output_file = args.output_file
    test_limit = 20 if args.test else None

    if verb in ["ListRecords", "ListIdentifiers"] and not dataset_name:
        print(f"Error: The dataset_name argument is required for the '{verb}' verb.")
        sys.exit(1)

    result = fetch_records(endpoint, verb, set_name=dataset_name, test_limit=test_limit)

    if verb == "ListRecords":
        save_to_csv(result, output_file)
        if args.save_xml:
            xml_output_file = output_file.replace(".csv", ".xml")
            xslt_path = os.path.join("xslt", "oai2.xsl")
            save_to_xml(result, xml_output_file, stylesheet=xslt_path)
    else:
        print("Non-ListRecords verbs are not yet supported.")

if __name__ == "__main__":
    main()
