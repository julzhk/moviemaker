from dataclasses import dataclass, field
from typing import Any
import yaml
from dataclasses_json import dataclass_json, Undefined
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import VideoClip

from moviepy.config import change_settings
from moviepy.editor import *

from utils import ShotStack

change_settings(
    {"IMAGEMAGICK_BINARY": "/usr/local/Cellar/imagemagick/7.1.1-39/bin/convert"}
)


class VideoClipHandler:
    clips = []
    screensize = (720, 460)
    fps = 25
    final_clip = VideoClip()

    def add_clip(self, clip):
        self.clips.append(clip)

    def concat(self):
        self.final_clip= concatenate_videoclips(self.clips)

    def write_out(self, filename):
        self.final_clip.write_videofile(filename, fps=self.fps, codec="mpeg4",)

    def add_watermark(self, watermark):
        watermark = ImageClip(watermark.get("src"))
        SCALE_FACTOR = 8
        watermark = resize(watermark, width=self.final_clip.w / SCALE_FACTOR, height=self.final_clip.h / SCALE_FACTOR)
        watermark = watermark.set_duration(self.final_clip.duration).set_pos(("left", "top"))
        self.final_clip = CompositeVideoClip([self.final_clip, watermark])


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class SimpleVideo:
    src: str

    def render(self):
        return VideoFileClip(self.src)

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TitleCard:
    message: str

    def render(self):
        shot = ShotStack(template_name="TitleCard")
        shot.prepare("Title", {"TITLE_TEXT": self.message})
        fn = shot.poll()
        return VideoFileClip(fn)

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class details:
    # handles the YAML metadata section
    filename: str = "noname.mp4"
    watermark: dict[str:Any] = field(default_factory=dict)

    def first(self, moviemaker_parent:'MovieMaker'):
        moviemaker_parent.filename = self.filename

    def second(self, moviemaker_parent:'MovieMaker'):
        moviemaker_parent.result_video=moviemaker_parent.video_clip.concat()

    def third(self, moviemaker_parent:'MovieMaker'):
        moviemaker_parent.video_clip.add_watermark(self.watermark)
        moviemaker_parent.video_clip.write_out(self.filename)

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class sequence:
    elements: list = field(default_factory=list)
    cards:list = field(default_factory=list)
    def first(self, moviemaker_parent:'MovieMaker'):
        for element in self.elements:
            card = globals()[element.get("type")](**element)
            moviemaker_parent.video_clip.add_clip(card.render())

    def second(self, moviemaker_parent:'MovieMaker'):
        pass

    def third(self, moviemaker_parent:'MovieMaker'):
        pass


@dataclass()
class MovieMaker:
    data:dict = field(default_factory=dict)
    video_clip: VideoClipHandler = VideoClipHandler()
    raw_yaml_data:dict=field(default_factory=dict)

    def prepare(self, file):
        self.raw_yaml_data = yaml.safe_load(file)
        for section in self.raw_yaml_data:
            init_vars = self.raw_yaml_data.get(section, {})
            try:
                klass=globals()[section]
                self.data[section] = klass(**init_vars)
            except (KeyError, TypeError) as e:
                print(f"Error No such element?: {e}")

    def parse(self,method_name:str):
        for section in self.raw_yaml_data:
            obj = self.data[section]
            getattr(obj, method_name)(moviemaker_parent=self)

    def first(self):
        self.parse("first")

    def second(self):
        self.parse("second")

    def third(self):
        self.parse("third")

    def execute(self):
        self.first()
        self.second()
        self.third()
