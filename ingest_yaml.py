from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import yaml
from dataclasses_json import dataclass_json, Undefined
from moviepy.video.fx.resize import resize

from moviepy.config import change_settings
from moviepy.editor import *

from utils import ShotStack, SynthesiaHandler

change_settings(
    {"IMAGEMAGICK_BINARY": "/usr/local/Cellar/imagemagick/7.1.1-39/bin/convert"}
)
from playwright.sync_api import sync_playwright

def run_htmlcapture(playwright, url='https://example.com', output_path='example.png'):
    # launch the browser
    browser = playwright.chromium.launch()
    # opens a new browser page
    page = browser.new_page()
    # navigate to the website
    page.goto(url)
    # take a full-page screenshot
    page.screenshot(path=output_path, full_page=True)
    # always close the browser
    browser.close()


class VideoClipHandler:
    clips = []
    screensize = (720, 460)
    fps = 25
    final_clip = VideoClip()

    def add_clip(self, clip:VideoClip):
        # conform the clip to the output requirements
        clip = clip.resize(self.screensize).fadeout(0.1)
        self.clips.append(clip)

    def concat(self):
        self.final_clip= concatenate_videoclips(self.clips)

    def write_out(self, filename):
        self.final_clip.write_videofile(filename, fps=self.fps, codec="mpeg4",)

    def add_watermark(self, watermark):
        SCALE_FACTOR = 8
        watermark = resize(watermark, width=self.final_clip.w / SCALE_FACTOR, height=self.final_clip.h / SCALE_FACTOR)
        watermark = watermark.set_duration(self.final_clip.duration).set_pos(("left", "top"))
        self.final_clip = CompositeVideoClip([self.final_clip, watermark])


class Card(metaclass=ABCMeta):
    start: int = 0
    end: int = None

    def first(self, moviemaker_parent:'MovieMaker'):
        pass
    def second(self, moviemaker_parent:'MovieMaker'):
        pass
    def third(self, moviemaker_parent:'MovieMaker'):
        pass


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class SimpleVideo(Card):
    src: str
    start: int = 0
    end: int = None

    def first(self) ->VideoFileClip:
        return VideoFileClip(self.src).subclip(self.start, self.end)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TalkingHeadCard(Card):
    script: str
    start: int = 0
    end: int = None
    src = ''

    def first(self) ->VideoFileClip:
        synthesia = SynthesiaHandler()
        synthesia.script = self.script
        synthesia.prepare()
        self.src = synthesia.poll()
        return VideoFileClip(self.src).subclip(self.start, self.end)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class HTMLCard(Card):
    src: str
    duration: int = 5
    filename="example.png"
    end: int = None
    moviemaker_parent: 'MovieMaker' = None

    def first(self) ->VideoFileClip:
        with sync_playwright() as playwright:
            run_htmlcapture(playwright, url=self.src, output_path=self.filename)
        clip= ImageClip(self.filename)
        clip = clip.set_duration(self.duration)
        # clip = resize(clip, width=self.moviemaker_parent.video_clip.w / SCALE_FACTOR, height=self.final_clip.h / SCALE_FACTOR)
        return clip

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class TitleCard(Card):
    message: str
    start: int = 0
    end: int = None

    def first(self):
        shot = ShotStack(template_name="TitleCard")
        shot.prepare("Title", {"TITLE_TEXT": self.message})
        fn = shot.poll()
        return VideoFileClip(fn).subclip(self.start).subclip(0, self.end)

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
            card = globals()[element.get("type")](**element,moviemaker_parent=moviemaker_parent)
            moviemaker_parent.video_clip.add_clip(card.first())

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
        for section in self.data:
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
