from dataclasses import dataclass, field
from typing import List
from abc import ABC
import yaml
from dataclasses_json import dataclass_json, Undefined

from render_video import TimeLineHandler
from video_components import Title


class YamlSection(ABC):
    def parse(self, *args, **kwargs):
        pass


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Details(YamlSection):
    # handles the YAML details section
    filename: str = "noname.mp4"

    def parse(self, moviemaker_parent):
        moviemaker_parent.filename = self.filename


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Sequence(YamlSection):
    elements: List = field(default_factory=list)
    component_lookup = {"Title": Title}

    def parse(self, moviemaker_parent):
        for frame in self.elements:
            frame_entity = self.component_lookup.get(frame.get("type"))(**frame)
            moviemaker_parent.sequence.append(frame_entity)


@dataclass()
class MovieMaker:
    sequence: List = field(default_factory=list)
    video_clip: TimeLineHandler = TimeLineHandler()
    filename: str = "noname.mp4"

    def ingest_yaml(self, file):
        content = yaml.safe_load(file)
        section_ookup = {"details": Details, "sequence": Sequence}
        for section in content:
            klass = section_ookup.get(section)
            # we don't allow top level lists or anything special
            init_vars = content.get(section, {})
            r = klass(**init_vars)
            r.parse(self)

    def render(self):
        for frame in self.sequence:
            self.video_clip.add_clip(frame.render())
        self.video_clip.render(self.filename)
