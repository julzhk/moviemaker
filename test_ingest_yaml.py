import unittest
from ingest_yaml import MovieMaker
import io


class TestIngestYaml(unittest.TestCase):
    def test_ingest_hello_world(self):
        # Create a sample YAML content
        yaml_content = """
details:
    filename: yeet7.mp4
sequence:
    elements:
      - type: Title
        message: "!Hello World!"
      - type: Title
        message: "AWESOME!"
"""
        file = io.StringIO(yaml_content)
        s = MovieMaker()
        s.ingest_yaml(file)
        s.render()


if __name__ == "__main__":
    unittest.main()
