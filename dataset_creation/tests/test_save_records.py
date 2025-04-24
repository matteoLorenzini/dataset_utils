import unittest
import os
from dataset_creation.data_collection.save_records import save_to_csv, save_to_xml

class TestSaveRecords(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"identifier": "1", "title": "Title 1", "description": "Description 1", "type": "Type1; Type2", "subject": "Subject1; Subject2"},
            {"identifier": "2", "title": "Title 2", "description": "Description 2", "type": "Type3", "subject": "Subject3"}
        ]
        self.csv_file = "test_output.csv"
        self.xml_file = "test_output.xml"

    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        if os.path.exists(self.xml_file):
            os.remove(self.xml_file)

    def test_save_to_csv(self):
        save_to_csv(self.records, self.csv_file)
        self.assertTrue(os.path.exists(self.csv_file))

    def test_save_to_xml(self):
        save_to_xml(self.records, self.xml_file)
        self.assertTrue(os.path.exists(self.xml_file))

if __name__ == "__main__":
    unittest.main()