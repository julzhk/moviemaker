import unittest
from ingest_yaml import Sequence
import io

class TestIngestYaml(unittest.TestCase):

    def test_ingest_hello_world(self):
        # Create a sample YAML content
        yaml_content = """
sequence:
  - type: Title
    message: "Hello, World!"
  - type: Title
    message: "Morning, World!"
"""
        file = io.StringIO(yaml_content)
        s = Sequence()
        s.ingest_yaml(file)
        result = s.render()
        self.assertIn("Hello, World!", result)

if __name__ == '__main__':
    unittest.main()