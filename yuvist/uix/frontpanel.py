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

from os.path import dirname, basename, join

from kivy.lang import Builder
from kivy.resources import resource_find
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, \
        ObjectProperty, ListProperty, DictProperty, OptionProperty, ReferenceListProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.video import Video

from core.video import YUV_CHROMA_FORMAT
from core.video import OUT_COLOR_FORMAT

from uix.seekbar import SeekBar
from uix.volumeslider import VolumeSlider
from uix.yuvvideo import YuvVideo


Builder.load_file(join(dirname(__file__), 'frontpanel.kv'))


class ImageButton(Button):
    pass


class FrontPanel(GridLayout):

    control       = ObjectProperty(None)
    display       = ObjectProperty(None)

    time_past     = StringProperty('00:00:00')
    time_next     = StringProperty('00:00:00')
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
        self._video = None
        super(FrontPanel, self).__init__(**kwargs)

        self.bind(position=self._update_seek_time, duration=self._update_seek_time)

    def seek(self, percent):
        if not self._video:
            return
        self._video.seek(percent)

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
        self.volume_slider.value_normalized = self.volume

    def on_playitem(self, instance, value):
        if self._video is not None:
            self._video.state = 'stop'
            self._video.unbind(texture=self._play_started,
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
        self._video.bind(texture=self._play_started,
                         state=self.setter('state'),
                         duration=self.setter('duration'),
                         position=self.setter('position'),
                         volume=self.setter('volume'))

        if self.control is not None:
            self.control.update_playlist(value)

        window = self.get_parent_window()
        if window:
            window.title = '%s %s:%s@%2.f' % (
                basename(self.source),
                '%dx%d' % tuple(self.yuv_size),
                self.format.upper(),
                self.yuv_fps
            )

    def _play_started(self, instance, value):
        self.display.clear_widgets()
        self.display.add_widget(self._video)

    def _update_seek_time(self, *largs):
        if not self._video or self.duration == 0:
            self.time_past = '00:00:00'
            self.time_next = '00:00:00'
            return
        def time_format(sec):
            hours   = int(sec / 3600)
            minutes = int(sec / 60) - (hours * 60)
            seconds = int(sec) - (hours * 3600 + minutes * 60)
            return '%02d:%02d:%02d' % (hours, minutes, seconds)
        percent = self.position / float(self.duration)
        self.time_past = time_format(self.duration * percent)
        self.time_next = time_format(self.duration * (1. - percent))

    def _play_pause(self):
        if not self.source:
            self.control.open_file()
            return
        if self.state == 'play':
            self.state = 'pause'
        else:
            self.state = 'play'

    def _prev_movie(self):
        self.control.prev_movie(self.playitem)

    def _next_movie(self):
        self.control.next_movie(self.playitem)

    def _prev_seek(self):
        if self.duration == 0:
            return
        step = 1 / float(self.yuv_fps) if self.yuv_fps != 0. else 1.
        seek = (self.position - step) / float(self.duration)
        self.seek(seek)

    def _next_seek(self):
        if self.duration == 0:
            return
        step = 1 / float(self.yuv_fps) if self.yuv_fps != 0. else 1.
        seek = (self.position + step) / float(self.duration)
        self.seek(seek)

    def _config_yuv_cfg(self):
        self.control.config_yuv_cfg()

    def _config_playlist(self):
        self.control.config_playlist()
