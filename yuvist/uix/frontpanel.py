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

__all__ = ('FrontPanel', )

from os.path import dirname, join

from kivy.lang import Builder
from kivy.resources import resource_find
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, \
        ObjectProperty, ListProperty, DictProperty, OptionProperty, ReferenceListProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.video import Video

from uix.yuvvideo import YuvVideo

from core.video import YUV_CHROMA_FORMAT
from core.video import OUT_COLOR_FORMAT


Builder.load_file(join(dirname(__file__), 'movist.kv'))


class ImageButton(Button):
    pass


class FrontPanel(GridLayout):

    past_seektime = StringProperty('00:00:00')
    next_seektime = StringProperty('00:00:00')
    volume_muted  = BooleanProperty(False)
    volume_slider = ObjectProperty(None)

    source        = StringProperty('')
    duration      = NumericProperty(-1)
    position      = NumericProperty(0)
    volume        = NumericProperty(1.0)
    state         = OptionProperty('stop', options=('play', 'pause', 'stop'))
    play          = BooleanProperty(False)
    options       = DictProperty({})

    format        = OptionProperty(YUV_CHROMA_FORMAT[1], options=YUV_CHROMA_FORMAT)
    colorfmt      = OptionProperty(OUT_COLOR_FORMAT[1], options=OUT_COLOR_FORMAT)
    yuv_size      = ListProperty([1920, 1080])
    yuv_fps       = NumericProperty(30.)
    playitem      = ReferenceListProperty(source, format, colorfmt, yuv_size, yuv_fps)

    def __init__(self, **kwargs):

        self.register_event_type('on_load_video')
        self.register_event_type('on_prev_video')
        self.register_event_type('on_next_video')
        self.register_event_type('on_prev_frame')
        self.register_event_type('on_next_frame')
        self.register_event_type('on_play_pause')

        self.register_event_type('on_fullscreen')
        self.register_event_type('on_exit')

        self.register_event_type('on_open_file')
        self.register_event_type('on_config_yuv_cfg')
        self.register_event_type('on_config_playlist')

        self._video = None

        super(FrontPanel, self).__init__(**kwargs)

        self.bind(position=self._on_seektime, duration=self._on_seektime)

    def seek(self, percent):
        if not self._video:
            return
        self._video.seek(percent)

    def on_load_video(self, *largs):
        pass

    def on_prev_video(self, *largs):
        pass

    def on_next_video(self, *largs):
        pass

    def on_prev_frame(self, *largs):
        if self.duration == 0:
            return
        step = 1 / float(self.yuv_fps) if self.yuv_fps != 0. else 1.
        seek = (self.position - step) / float(self.duration)
        self.seek(seek)

    def on_next_frame(self, *largs):
        if self.duration == 0:
            return
        step = 1 / float(self.yuv_fps) if self.yuv_fps != 0. else 1.
        seek = (self.position + step) / float(self.duration)
        self.seek(seek)

    def on_play_pause(self, *largs):
        if not self.source:
            self.dispatch('on_open_file')
            return

        if self.state == 'play':
            self.state = 'pause'
        else:
            self.state = 'play'

    def on_fullscreen(self, *largs):
        pass

    def on_exit(self, *largs):
        pass

    def on_open_file(self, *largs):
        pass

    def on_config_yuv_cfg(self, *largs):
        pass

    def on_config_playlist(self, *largs):
        pass

    def on_state(self, instance, value):
        if not self._video:
            return
        self._video.state = value

    def on_play(self, instance, value):
        value = 'play' if value else 'stop'
        return self.on_state(instance, value)

    def on_volume(self, instance, value):
        if not self._video:
            return
        self._video.volume = value

    def on_playitem(self, instance, value):

        if self._video is not None:
            self._video.state = 'stop'
            self._video.unbind(on_load=self._on_load_video,
                               state=self.setter('state'),
                               duration=self.setter('duration'),
                               position=self.setter('position'),
                               volume=self.setter('volume'))
            self._video = None

        filename = resource_find(self.source)
        if filename is None:
            return

        cls = YuvVideo if filename.lower().endswith('.yuv') else Video

        self._video = cls(format=self.format, colorfmt=self.colorfmt,
                yuv_size=self.yuv_size, yuv_fps=self.yuv_fps,
                source=filename, state=self.state, volume=self.volume,
                pos_hint={'x':0, 'y':0}, **self.options)

        self._video.bind(on_load=self._on_load_video,
                         state=self.setter('state'),
                         duration=self.setter('duration'),
                         position=self.setter('position'),
                         volume=self.setter('volume'))

    def _on_load_video(self, *largs):
        self.dispatch('on_load_video', self.playitem)

    def _on_seektime(self, *largs):

        if not self._video or self.duration == 0:
            self.past_seektime = '00:00:00'
            self.next_seektime = '00:00:00'
            return

        def seektime(seek):
            hours   = int(seek / 3600)
            minutes = int(seek / 60) - (hours * 60)
            seconds = int(seek) - (hours * 3600 + minutes * 60)
            return '%02d:%02d:%02d' % (hours, minutes, seconds)

        seek = self.position / float(self.duration)
        self.past_seektime = seektime(self.duration * seek)
        self.next_seektime = seektime(self.duration * (1. - seek))
