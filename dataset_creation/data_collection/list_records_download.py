import os
import sys
import questionary
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

def interactive_main():
    # Define the interactive prompts using questionary
    endpoint = questionary.select(
        "Choose the endpoint to fetch data from:",
        choices=[f"{key}: {value}" for key, value in ENDPOINTS.items()]
    ).ask()

    verb = questionary.select(
        "Choose the OAI-PMH verb to use:",
        choices=[f"{key}: {value}" for key, value in VERBS.items()]
    ).ask()

    dataset_name = questionary.text(
        "Enter the dataset name (leave blank if not required):",
        default=""
    ).ask()

    output_file = questionary.text(
        "Enter the output file name (e.g., output.csv):",
        default="output.csv"
    ).ask()

    test = questionary.confirm(
        "Do you want to limit the fetch to 20 records for testing?",
        default=False
    ).ask()

    save_xml = questionary.confirm(
        "Do you want to save the output as an XML file?",
        default=False
    ).ask()

    # Parse the selected options
    endpoint_key = endpoint.split(':')[0]
    verb_key = verb.split(':')[0]
    endpoint = ENDPOINTS[endpoint_key]
    verb = VERBS[verb_key]
    test_limit = 20 if test else None

    # Print selected options
    print(f"Endpoint: {endpoint}")
    print(f"Verb: {verb}")
    print(f"Dataset Name: {dataset_name}")
    print(f"Output File: {output_file}")
    print(f"Test Limit: {test_limit}")

    # Validate dataset_name if required
    if verb in ["ListRecords", "ListIdentifiers"] and not dataset_name:
        print(f"Error: The dataset_name argument is required for the '{verb}' verb.")
        sys.exit(1)

    # Fetch records with resumption token handling
    all_records = []
    resumption_token = None

    while True:
        result, resumption_token = fetch_records(endpoint, verb, set_name=dataset_name, test_limit=test_limit, resumption_token=resumption_token)
        all_records.extend(result)

        if not resumption_token:
            break

    # Save records
    if verb == "ListRecords":
        save_to_csv(all_records, output_file)
        if save_xml:
            xml_output_file = output_file.replace(".csv", ".xml")
            xslt_path = os.path.join("xslt", "oai2.xsl")
            save_to_xml(all_records, xml_output_file, stylesheet=xslt_path)
    else:
        print("Non-ListRecords verbs are not yet supported.")

def main():
    if len(sys.argv) == 1:
        interactive_main()
    elif len(sys.argv) == 3:
        dataset_name = sys.argv[1]
        output_file = sys.argv[2]
        endpoint = "https://www.culturaitalia.it/oaiProviderCI/OAIHandler"
        
        print(f"Fetching records for dataset: {dataset_name}")
        records = fetch_records(endpoint, dataset_name)
        print(f"Fetched {len(records)} records.")
        
        print(f"Saving records to {output_file}")
        save_to_csv(records, output_file)
        print("Done.")
    else:
        print("Usage: python script.py or python script.py <dataset_name> <output_file>")
        sys.exit(1)

if __name__ == "__main__":
    main()
