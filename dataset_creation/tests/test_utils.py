import unittest
import xml.etree.ElementTree as ET
from dataset_creation.data_collection.utils import strip_namespace

class TestUtils(unittest.TestCase):
    def test_strip_namespace(self):
        xml_with_ns = """<root xmlns:ns="http://example.com/ns">
                            <ns:child>Value</ns:child>
                         </root>"""
        root = ET.fromstring(xml_with_ns)
        stripped_root = strip_namespace(root)

        self.assertEqual(stripped_root.tag, "root")
        self.assertEqual(stripped_root[0].tag, "child")
        self.assertEqual(stripped_root[0].text, "Value")

if __name__ == "__main__":
    unittest.main()