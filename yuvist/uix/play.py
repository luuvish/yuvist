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

__all__ = ('Play', )

from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, OptionProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window


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

<Play>:
    size: 153+1, 51

    Button:
        pos: 0, 18
        size_hint: None, None
        size: 20, 18
        border: 0, 0, 0, 0
        background_normal: 'data/images/MainPrevMovie.tiff'
        background_down: 'data/images/MainPrevMovieHover.tiff'
        on_press: root._prev_movie()

    Button:
        pos: 28, 19
        size_hint: None, None
        size: 18, 18
        border: 0, 0, 0, 0
        background_normal: 'data/images/MainPrevSeek.tiff'
        background_down: 'data/images/MainPrevSeekHover.tiff'
        on_press: root._prev_seek()

    Button:
        pos: 54, 6
        size_hint: None, None
        size: 45, 45
        background_normal: 'data/images/MainPause.tiff' if root.state == 'play' else 'data/images/MainPlay.tiff'
        background_down: 'data/images/MainPausePressed.tiff' if root.state == 'play' else 'data/images/MainPlayPressed.tiff'
        on_press: root._play_pause()

    Button:
        pos: 107, 19
        size_hint: None, None
        size: 18, 18
        border: 0, 0, 0, 0
        background_normal: 'data/images/MainNextSeek.tiff'
        background_down: 'data/images/MainNextSeekHover.tiff'
        on_press: root._next_seek()

    Button:
        pos: 133, 19
        size_hint: None, None
        size: 20, 18
        border: 0, 0, 0, 0
        background_normal: 'data/images/MainNextMovie.tiff'
        background_down: 'data/images/MainNextMovieHover.tiff'
        on_press: root._next_movie()
''')


class OpenDialog(FloatLayout):
    path   = StringProperty('.')
    open   = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Play(RelativeLayout):
    video = ObjectProperty(None)
    state = OptionProperty('stop', options=('play', 'pause', 'stop'))

    def __init__(self, **kwargs):
        self._path = '.'

        super(Play, self).__init__(**kwargs)

        Window.bind(on_dropfile=self._drop_file)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, Window)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def on_video(self, instance, value):
        self.video.bind(state=self.setter('state'))

    def _play_pause(self):
        if not self.video.source:
            self._open_file()
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
        playlist = self.video.playlist
        for i in xrange(len(playlist)):
            if playlist[i]['source'] == self.video.source:
                if i > 0:
                    self.video.source = playlist[i-1]['source']
                    self.video.format = playlist[i-1]['format']
                    self.video.resolution = playlist[i-1]['resolution']
                    self.video.state = 'play'
                    return

    def _next_movie(self):
        if not self.video.source:
            return
        playlist = self.video.playlist
        for i in xrange(len(playlist)):
            if playlist[i]['source'] == self.video.source:
                if i < len(playlist)-1:
                    self.video.source = playlist[i+1]['source']
                    self.video.format = playlist[i+1]['format']
                    self.video.resolution = playlist[i+1]['resolution']
                    self.video.state = 'play'
                    return

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

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        from kivy.utils import platform
        if keycode == (111, 'o') and (
            platform() == 'win'    and 'ctrl' in modifiers or
            platform() == 'linux'  and 'ctrl' in modifiers or
            platform() == 'macosx' and 'meta' in modifiers):
            self._open_file()
            return True
        if keycode == (49, '1') and (
            platform() == 'win'    and 'alt'  in modifiers or
            platform() == 'linux'  and 'alt'  in modifiers or
            platform() == 'macosx' and 'meta' in modifiers):
            return self._resize(size_hint=(0.5, 0.5))
        if keycode == (50, '2') and (
            platform() == 'win'    and 'alt'  in modifiers or
            platform() == 'linux'  and 'alt'  in modifiers or
            platform() == 'macosx' and 'meta' in modifiers):
            return self._resize(size_hint=(1.0, 1.0))
        if keycode == (51, '3') and (
            platform() == 'win'    and 'alt'  in modifiers or
            platform() == 'linux'  and 'alt'  in modifiers or
            platform() == 'macosx' and 'meta' in modifiers):
            return self._resize(size_hint=(1.5, 1.5))
        if keycode == (52, '4') and (
            platform() == 'win'    and 'alt'  in modifiers or
            platform() == 'linux'  and 'alt'  in modifiers or
            platform() == 'macosx' and 'meta' in modifiers):
            return self._resize(size_hint=(2.0, 2.0))
        return True

    def _resize(self, size_hint=(1., 1.)):
        window = self.get_root_window()
        size   = self.video.resolution
        ratio  = size[0] / float(size[1])
        w, h   = 1920, 1080 #window._size
        tw, th = int(size[0] * size_hint[0]), int(size[1] * size_hint[1]) + 62
        iw = min(w, tw)
        ih = iw / ratio
        if ih > h:
            ih = min(h, th)
            iw = ih * ratio
        window.size = int(iw), int(ih)
        return True

    def _open_file(self):
        popup = None

        def open(path, selected):
            if len(selected) > 0:
                import os
                self.video.source = os.path.join(path, selected[0])
                self.video.state = 'play'
                self._path = path
            popup.dismiss()

        def submit():
            popup.dismiss()

        from kivy.uix.popup import Popup
        from kivy.core.window import Window
        size = Window.size[0] - 160, Window.size[1] - 100
        popup = Popup(title='Open Image File',
                      content=OpenDialog(path=self._path, open=open, cancel=submit),
                      size_hint=(None, None), size=size)
        popup.open()

    def _drop_file(filename):
        print 'dropfile %s' % filename
        self.video.source = filename
        self.video.state = 'play'
