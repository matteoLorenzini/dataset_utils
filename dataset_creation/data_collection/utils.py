import xml.etree.ElementTree as ET

def strip_namespace(element):
    """
    Remove namespaces from an XML element and its children.
    """
    for elem in element.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
        elem.attrib = {key.split('}', 1)[-1]: value for key, value in elem.attrib.items()}
    return element