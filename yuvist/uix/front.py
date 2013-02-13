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

__all__ = ('Front', )

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import (ObjectProperty, StringProperty,
                             BooleanProperty, NumericProperty, ListProperty,
                             DictProperty, OptionProperty)
from kivy.uix.gridlayout import GridLayout

from .seek   import Seek
from .volume import Volume
from .play   import Play
from .config import Config


Builder.load_string('''
<Front>:
    container: container
    cols: 1

    FloatLayout:
        cols: 1
        id: container

    GridLayout:
        cols: 1
        size_hint_y: None
        height: 62

        canvas:
            Color:
                hsv: 0, 0, .8
            Rectangle:
                size: self.size
                pos: self.pos

        Seek:
            size_hint_y: None
            height: 11
            video: root

        FloatLayout:
            size_hint_y: None
            height: 51

            Volume:
                x: root.x
                size_hint: None, None
                video: root

            Play:
                center_x: int(root.center_x)
                size_hint: None, None
                video: root

            Config:
                right: root.right
                size_hint: None, None
                video: root
''')


class Front(GridLayout):
    source     = StringProperty('')
    format     = OptionProperty('yuv420', options=('yuv400', 'yuv420',
                                                   'yuv422', 'yuv422v', 'yuv444'))
    resolution = ListProperty([1920, 1080])

    duration   = NumericProperty(-1)
    position   = NumericProperty(0)
    volume     = NumericProperty(1.0)
    state      = OptionProperty('stop', options=('play', 'pause', 'stop'))
    play       = BooleanProperty(False)

    options    = DictProperty({})
    container  = ObjectProperty(None)

    playlist   = ListProperty([])

    def __init__(self, **kwargs):
        self._image = None
        super(Front, self).__init__(**kwargs)

        self.bind(source=self._image_init, format=self._image_init, resolution=self._image_init)
        if self.source:
            self._trigger_image_load()

    def seek(self, percent):
        if not self._image:
            return
        self._image.seek(percent)

    def on_state(self, instance, value):
        if self._image is None:
            self._trigger_image_load()
        else:
            self._image.state = value

    def on_play(self, instance, value):
        value = 'play' if value else 'stop'
        return self.on_state(instance, value)

    def on_volume(self, instance, value):
        if not self._image:
            return
        self._image.volume = value

    def _image_init(self, *largs):
        if not self.container:
            return
        self.container.clear_widgets()
        self._trigger_image_load()

    def _trigger_image_load(self, *largs):
        Clock.unschedule(self._image_load)
        Clock.schedule_once(self._image_load, -1)

    def _image_load(self, *largs):
        if self._image is not None:
            self._image.state = 'stop'
            self._image.unbind(texture=self._play_started,
                               state=self.setter('state'),
                               duration=self.setter('duration'),
                               position=self.setter('position'),
                               volume=self.setter('volume'))
            self._image = None
        if self.source:
            from kivy.resources import resource_find
            filename = resource_find(self.source)
            if filename is None:
                return
            if filename.lower().endswith('.yuv'):
                from .yuvvideo import YuvVideo as Image
            else:
                from kivy.uix.video import Video as Image
            self._image = Image(yuv_size=self.resolution,
                                yuv_format=self.format,
                                out_format='yuv',
                                source=filename,
                                state=self.state,
                                volume=self.volume,
                                pos_hint={'x':0, 'y':0},
                                **self.options)
            self._image.bind(texture=self._play_started,
                             state=self.setter('state'),
                             duration=self.setter('duration'),
                             position=self.setter('position'),
                             volume=self.setter('volume'))
            self._image.state = self.state
            self._update_playlist()

    def _play_started(self, instance, value):
        self.container.clear_widgets()
        self.container.add_widget(self._image)

    def _update_playlist(self):
        from kivy.core.window import Window
        import os
        info = '%dx%d' % tuple(self.resolution) + '@' + self.format
        Window.title = '%s %s' % (os.path.basename(self.source), info)

        playlist = self.playlist[:]
        for play in playlist:
            if play['source'] == self.source:
                play['format'] = self.format
                play['resolution'] = self.resolution
                return
        playlist.append({'source': self.source,
                         'format': self.format,
                         'resolution': self.resolution})
        self.playlist = playlist


if __name__ == '__main__':
    import sys
    from kivy.base import runTouchApp
    runTouchApp(Front(source=sys.argv[1]))
