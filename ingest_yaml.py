from dataclasses import dataclass, field
from typing import List

import yaml
from dataclasses_json import dataclass_json, Undefined

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Title:
    message:str

    def render(self):
        print('+' + '-' * (len(self.message) + 2) + '+')
        print('| ' + self.message + ' |')
        print('+' + '-' * (len(self.message) + 2) + '+')
        return f'** {self.message} ** '

@dataclass()
class Sequence:
    sequence: List = field(default_factory=list)

    def render(self):
        r = ''
        for e in self.sequence:
            r += e.render()
        return r



    def ingest_yaml(self, file):
        content = yaml.safe_load(file)
        typeLookup = {
            'Title':Title
        }
        for frame in content.get('sequence'):
            frame_entity = typeLookup.get(frame.get('type'))(**frame)
            self.sequence.append(frame_entity)



