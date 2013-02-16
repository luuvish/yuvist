# -*- coding: utf-8 -*-

"""\
Kivy YUV Image Viewer
Copyright (C) 2012 Luuvish <luuvish@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__all__ = ('SeekBar', )

from kivy.uix.videoplayer import VideoPlayerProgressBar


class SeekBar(VideoPlayerProgressBar):

    def __init__(self, **kwargs):

        super(SeekBar, self).__init__(**kwargs)

        self.bubble.size = (72,44)

    def _update_bubble(self, *l):
        seek = self.seek
        if self.seek is None:
            if self.video.duration == 0:
                seek = 0
            else:
                seek = self.video.position / self.video.duration
        d = self.video.duration * seek
        hours   = int(d / 3600)
        minutes = int(d / 60) - (hours * 60)
        seconds = int(d) - (hours * 3600 + minutes * 60)
        self.bubble_label.text = '%02d:%02d:%02d' % (hours, minutes, seconds)
        self.bubble.center_x = self.x + seek * self.width
        self.bubble.y = self.top
