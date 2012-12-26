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
from kivy.properties import StringProperty, ObjectProperty, OptionProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout


Builder.load_string('''
<OpenDialog>:
    BoxLayout:
        orientation: 'vertical'
        pos: root.pos
        size: root.size

        FileChooserListView:
            id: filechooser
            multiselect: False
            path: root.path

        BoxLayout:
            size_hint_y: None
            height: 30

            Button:
                text: 'Cancel'
                on_release: root.cancel()

            Button:
                text: 'Open'
                on_release: root.open(filechooser.path, filechooser.selection)

<PlayPanel>:
    size: 153+1, 51

    Button:
        pos: 0, 18
        size_hint: None, None
        size: 20, 18
        border: 0, 0, 0, 0
        background_normal: 'images/MainPrevMovie.tiff'
        background_down: 'images/MainPrevMovieHover.tiff'
        on_press: root._prev_movie()

    Button:
        pos: 28, 19
        size_hint: None, None
        size: 18, 18
        border: 0, 0, 0, 0
        background_normal: 'images/MainPrevSeek.tiff'
        background_down: 'images/MainPrevSeekHover.tiff'
        on_press: root._prev_seek()

    Button:
        pos: 54, 6
        size_hint: None, None
        size: 45, 45
        background_normal: 'images/MainPause.tiff' if root.state == 'play' else 'images/MainPlay.tiff'
        background_down: 'images/MainPausePressed.tiff' if root.state == 'play' else 'images/MainPlayPressed.tiff'
        on_press: root._play_pause()

    Button:
        pos: 107, 19
        size_hint: None, None
        size: 18, 18
        border: 0, 0, 0, 0
        background_normal: 'images/MainNextSeek.tiff'
        background_down: 'images/MainNextSeekHover.tiff'
        on_press: root._next_seek()

    Button:
        pos: 133, 19
        size_hint: None, None
        size: 20, 18
        border: 0, 0, 0, 0
        background_normal: 'images/MainNextMovie.tiff'
        background_down: 'images/MainNextMovieHover.tiff'
        on_press: root._next_movie()
''')


class OpenDialog(FloatLayout):
    path   = StringProperty('.')
    open   = ObjectProperty(None)
    cancel = ObjectProperty(None)


class PlayPanel(RelativeLayout):
    video = ObjectProperty(None)
    state = OptionProperty('stop', options=('play', 'pause', 'stop'))

    def __init__(self, **kwargs):
        super(PlayPanel, self).__init__(**kwargs)

    def on_video(self, instance, value):
        self.video.bind(state=self.setter('state'))

    def _play_pause(self):
        if not self.video.source:
            popup = None
            def open(path, selected):
                if len(selected) > 0:
                    import os
                    self.video.source = os.path.join(path, selected[0])
                    self.video.state = 'play'
                popup.dismiss()
            def submit():
                popup.dismiss()
            from kivy.uix.popup import Popup
            from kivy.core.window import Window
            size = Window.size[0] - 160, Window.size[1] - 100
            popup = Popup(title='Open Image File',
                          content=OpenDialog(open=open, cancel=submit),
                          size_hint=(None, None), size=size)
            popup.open()
            return
        if self.video.state == 'stop':
            self.video.state = 'play'
        elif self.video.state == 'play':
            self.video.state = 'pause'
        else:
            self.video.state = 'play'

    def _prev_movie(self):
        if not self.video.source:
            return
        try:
            playlist = self.video.playlist
            i = playlist.index(self.video.source)
            if i > 0:
                self.video.source = playlist[i-1]
                self.video.state = 'play'
        except ValueError:
            pass

    def _next_movie(self):
        if not self.video.source:
            return
        try:
            playlist = self.video.playlist
            i = playlist.index(self.video.source)
            if i < len(playlist):
                self.video.source = playlist[i+1]
                self.video.state = 'play'
        except ValueError:
            pass

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
