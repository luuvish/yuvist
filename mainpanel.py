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
from kivy.properties import (ObjectProperty, StringProperty,
                             BooleanProperty, NumericProperty,
                             DictProperty, OptionProperty)
from kivy.uix.gridlayout import GridLayout

from seekpanel   import SeekPanel
from volumepanel import VolumePanel
from playpanel   import PlayPanel
from configpanel import ConfigPanel


Builder.load_string('''
<MainPanel>:
    container: container
    cols: 1

    FloatLayout:
        cols: 1
        id: container

    GridLayout:
        cols: 1
        size_hint_y: None
        height: 58

        canvas:
            Color:
                rgb: .8, .8, .8
            Rectangle:
                size: self.size
                pos: self.pos

        SeekPanel:
            size_hint_y: None
            height: 13
            video: root

        FloatLayout:
            size_hint_y: None
            height: 45

            VolumePanel:
                x: root.x + 8
                size_hint: None, None
                video: root

            PlayPanel:
                pos_hint: {'center_x':.5}
                size_hint: None, None
                video: root

            ConfigPanel:
                right: root.right - 8
                size_hint: None, None
                video: root
''')


class MainPanel(GridLayout):
    source    = StringProperty('')
    duration  = NumericProperty(-1)
    position  = NumericProperty(0)
    volume    = NumericProperty(1.0)
    state     = OptionProperty('stop', options=('play', 'pause', 'stop'))
    play      = BooleanProperty(False)

    options   = DictProperty({})
    container = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._video = None
        super(MainPanel, self).__init__(cols=1, **kwargs)

    def on_source(self, instance, value):
        if not self.container:
            return
        self.container.clear_widgets()

    def on_state(self, instance, value):
        if self._video is None:
            if self.source.lower().endswith('.yuv'):
                from yuvimage import YuvImage as CoreImage
            else:
                from kivy.uix.video import Video as CoreImage
            self._video = CoreImage(source=self.source,
                                    state='stop',
                                    volume=self.volume,
                                    pos_hint={'x':0, 'y':0},
                                    **self.options)
            self._video.bind(texture=self._play_started,
                             state=self.setter('state'),
                             duration=self.setter('duration'),
                             position=self.setter('position'),
                             volume=self.setter('volume'))
        self._video.state = value

    def on_play(self, instance, value):
        value = 'play' if value else 'stop'
        return self.on_state(instance, value)

    def on_volume(self, instance, value):
        if not self._video:
            return
        self._video.volume = value

    def seek(self, percent):
        if not self._video:
            return
        self._video.seek(percent)

    def _play_started(self, instance, value):
        self.container.clear_widgets()
        self.container.add_widget(self._video)


if __name__ == '__main__':
    import sys
    from kivy.base import runTouchApp
    runTouchApp(MainPanel(source=sys.argv[1]))
