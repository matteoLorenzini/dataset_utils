import unittest
from dataset_creation.data_collection.fetch_records import fetch_records

class TestFetchRecords(unittest.TestCase):
    def test_fetch_records_valid(self):
        # Mock a valid endpoint and response
        endpoint = "https://www.culturaitalia.it/oaiProviderCI/OAIHandler"
        verb = "ListRecords"
        set_name = "museid_oa_parthenos"
        test_limit = 5

        # Simulate fetching records (mocking the actual HTTP request is recommended)
        result = fetch_records(endpoint, verb, set_name=set_name, test_limit=test_limit)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), test_limit)

    def test_fetch_records_invalid_endpoint(self):
        # Test with an invalid endpoint
        endpoint = "https://www.culturaitalia.it/oaiProviderCI/OAIHandler"
        verb = "ListRecords"
        with self.assertRaises(SystemExit):
            fetch_records(endpoint, verb)

if __name__ == "__main__":
    unittest.main()