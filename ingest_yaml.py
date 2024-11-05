from dataclasses import dataclass, field
from typing import List

import yaml
from dataclasses_json import dataclass_json, Undefined

from render_video import MovieHandler


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Title:
    message:str

    def render(self):
        print('+' + '-' * (len(self.message) + 2) + '+')
        print('| ' + self.message + ' |')
        print('+' + '-' * (len(self.message) + 2) + '+')
        return MovieHandler.create_title_text_clip(self.message)

@dataclass()
class Sequence:
    sequence: List = field(default_factory=list)
    video_clip:MovieHandler = MovieHandler()
    filename:str = 'noname.mp4'

    def render(self):
        for frame in self.sequence:
            self.video_clip.add_clip(frame.render())
        self.video_clip.render(self.filename)




    def ingest_yaml(self, file):
        content = yaml.safe_load(file)
        self.extract_details(content)
        self.extract_sequence(content)

    def extract_sequence(self, content):
        typeLookup = {
            'Title': Title
        }
        for frame in content.get('sequence'):
            frame_entity = typeLookup.get(frame.get('type'))(**frame)
            self.sequence.append(frame_entity)

    def extract_details(self, content):
        self.filename = content.get('details').get('filename','anon.mp4')



