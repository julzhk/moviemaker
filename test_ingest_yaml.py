import unittest
from ingest_yaml import Sequence
import io

class TestIngestYaml(unittest.TestCase):

    def test_ingest_hello_world(self):
        # Create a sample YAML content
        yaml_content = """
details:
    filename: yeet3.mp4
sequence:
  - type: Title
    message: "Hello, World!"
  - type: Title
    message: "Morn', World!"
"""
        file = io.StringIO(yaml_content)
        s = Sequence()
        s.ingest_yaml(file)
        s.render()

if __name__ == '__main__':
    unittest.main()