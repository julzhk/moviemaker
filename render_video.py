from moviepy.config import change_settings
from moviepy.editor import *

change_settings(
    {"IMAGEMAGICK_BINARY": "/usr/local/Cellar/imagemagick/7.1.1-39/bin/convert"}
)


class TimeLineHandler:
    clips = []

    screensize = (720, 460)

    def add_clip(self, clip):
        self.clips.append(clip)

    def render(self, filename="yeet.mp4"):
        final_clip = concatenate_videoclips(self.clips)
        final_clip.write_videofile(filename, fps=25, codec="mpeg4")
