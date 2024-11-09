from dataclasses import dataclass

from dataclasses_json import dataclass_json, Undefined
from moviepy.video.io.VideoFileClip import VideoFileClip
from abc import ABC

from shotstackwrapper import ShotStack


class SequenceElement(ABC):
    def render(self):
        pass


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Title(SequenceElement):
    message: str

    def render(self):
        print("+" + "-" * (len(self.message) + 2) + "+")
        print("| " + self.message + " |")
        print("+" + "-" * (len(self.message) + 2) + "+")
        shot = ShotStack()
        shot.prepare("Title", {"TITLE_TEXT": self.message})
        fn = shot.poll()
        return VideoFileClip(fn)
