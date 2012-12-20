#!/usr/bin/env python
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

from kivy.lang import Builder
from kivy.properties import (ObjectProperty, OptionProperty)
from kivy.uix.boxlayout import BoxLayout


Builder.load_string('''
<PlayPanel>:
    orientation: 'horizontal'
    spacing: 8
    size: (45 + (20+18)*2 + root.spacing*4, 45)

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainPrevMovie.tiff'
        background_down: 'images/MainPrevMovieHover.tiff'
        on_press: root._prev_movie()

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (18, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainPrevSeek.tiff'
        background_down: 'images/MainPrevSeekHover.tiff'
        on_press: root._prev_seek()

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (45, 45)
        background_normal: 'images/MainPause.tiff' if root.state == 'play' else 'images/MainPlay.tiff'
        background_down: 'images/MainPausePressed.tiff' if root.state == 'play' else 'images/MainPlayPressed.tiff'
        on_press: root._play_pause()

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (18, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainNextSeek.tiff'
        background_down: 'images/MainNextSeekHover.tiff'
        on_press: root._next_seek()

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainNextMovie.tiff'
        background_down: 'images/MainNextMovieHover.tiff'
        on_press: root._next_movie()
''')


class PlayPanel(BoxLayout):
    video = ObjectProperty(None)
    state = OptionProperty('stop', options=('play', 'pause', 'stop'))

    def __init__(self, **kwargs):
        super(PlayPanel, self).__init__(**kwargs)

    def on_video(self, instance, value):
        self.video.bind(state=self.setter('state'))

    def _play_pause(self):
        if   self.video.state == 'stop':
            self.video.state = 'play'
            print '_play_pause'
        elif self.video.state == 'play':
            self.video.state = 'pause'
        else:
            self.video.state = 'play'

    def _prev_movie(self):
        print 'on_prev_movie'
    def _next_movie(self):
        print 'on_next_movie'

    def _prev_seek(self):
        if self.video.duration == 0:
            return
        seek = (self.video.position - 1) / float(self.video.duration)
        self.video.seek(seek)

    def _next_seek(self):
        if self.video.duration == 0:
            return
        seek = (self.video.position + 1) / float(self.video.duration)
        self.video.seek(seek)
