import unittest

import requests_mock

from ingest_yaml import MovieMaker
import io


class TestIngestYaml(unittest.TestCase):



    def create_movie(self, yaml_content):
        file = io.StringIO(yaml_content)
        my_movie = MovieMaker()
        my_movie.prepare(file)
        return my_movie


    def test_ingest_yaml(self):
        yaml_content = """
        details:
            filename: yeet_c.mp4
            watermark:
              src: logo2.png
              position: [top,left]
        sequence:
            elements:
            - type: TitleCard
              message: "Hello, World!"
              start: 0
              end: 2                          
            - type: HTMLCard
              src: http://consent-portal.com/
              duration: 3
            - type: SimpleVideo
              src: http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4
              start: 0
              end: 5
            - type: TalkingHeadCard
              script: "good!"
            - type: SimpleVideo
              src: http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4
              start: 0
              end: 2                           
            - type: SimpleVideo
              src: http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4
              start: 0
              end: 5             
        """
        with requests_mock.Mocker(real_http=True) as m:
            m.post("https://api.shotstack.io/edit/v1/templates/render",
                   json={"response": {"id": "mock_queue_id"}},)
            m.get("https://api.shotstack.io/edit/v1/render/mock_queue_id",
                  json={"response": {"status": "done", "url": "http://localhost:8000/welcome.mp4"}},)
            m.get("https://api.shotstack.io/edit/v1/templates",
                  json={"response": {"templates": [{'id':'mytemplate_id','name':'Title'}]}},)
            m.post("https://api.synthesia.io/v2/videos",
                  json= {'id':'synthesia_id','name':'Title'})
            m.get("https://api.synthesia.io/v2/videos/synthesia_id",
                  json= {'id':'synthesia_id','status':'complete','download':'http://localhost:8000/green_screen_awesome_rendered_video.mp4'})
            r = self.create_movie(yaml_content)
            r.execute()

if __name__ == "__main__":
    unittest.main()
