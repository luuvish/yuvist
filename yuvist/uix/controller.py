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

__all__ = ('Controller', )

from os.path import basename

from kivy.resources import resource_find
from kivy.base import EventLoop
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, ListProperty, \
        ObjectProperty, BooleanProperty, \
        OptionProperty, ReferenceListProperty, DictProperty
from kivy.uix.video import Video

from yuvist.core.video import YUV_CHROMA_FORMAT, OUT_COLOR_FORMAT
from yuvist.uix.yuvvideo import YuvVideo


class Controller(EventDispatcher):

    source   = StringProperty('')
    duration = NumericProperty(-1)
    position = NumericProperty(0)
    volume   = NumericProperty(1.0)
    state    = OptionProperty('stop', options=('play', 'pause', 'stop'))
    play     = BooleanProperty(False)
    options  = DictProperty({})

    format   = OptionProperty(YUV_CHROMA_FORMAT[1], options=YUV_CHROMA_FORMAT)
    colorfmt = OptionProperty(OUT_COLOR_FORMAT[1], options=OUT_COLOR_FORMAT)
    yuv_size = ListProperty([1920, 1080])
    yuv_fps  = NumericProperty(30.)
    playitem = ReferenceListProperty(source, format, colorfmt, yuv_size, yuv_fps)

    message  = StringProperty('')
    display  = ObjectProperty(None)
    playlist = ObjectProperty(None)

    def __init__(self, **kwargs):

        self.register_event_type('on_open_playitem')
        self.register_event_type('on_open_playlist')
        self.register_event_type('on_fullscreen')
        self.register_event_type('on_customsize')
        self.register_event_type('on_close')

        self.register_event_type('on_prev_video')
        self.register_event_type('on_next_video')
        self.register_event_type('on_prev_frame')
        self.register_event_type('on_next_frame')
        self.register_event_type('on_play_pause')

        self.register_event_type('on_select_playitem')
        self.register_event_type('on_select_playlist')
        self.register_event_type('on_config_yuvparam')

        self._video = None

        super(Controller, self).__init__(**kwargs)

    def seek(self, percent):
        if self._video is None:
            return
        self._video.seek(percent)

    def on_open_playitem(self, playitem):
        if type(playitem) is tuple or type(playitem) is list:
            if len(playitem) != 5:
                raise ValueError('playitem must have 5 components'
                                 ' - source, format, colorfmt, size, fps'
                                 ' (got %r)' % playitem)
            self.playitem = playitem[:]
            self.state = 'play'
            return
        if type(playitem) is str or type(playitem) is unicode:
            self.source = playitem
            self.state = 'play'
            return
        raise ValueError('playitem have an invalid format (got %r)' % type(playitem))

    def on_open_playlist(self, playlist):
        pass

    def on_fullscreen(self):
        pass

    def on_customsize(self, size, size_hint=(1., 1.)):
        pass

    def on_close(self, *largs):
        pass

    def on_prev_video(self, *largs):
        playitem = self.playitem
        playlist = self.playlist[:]
        for i in xrange(len(playlist)):
            if playlist[i][0] == playitem[0] and i > 0:
                self.dispatch('on_open_playitem', playlist[i-1])
                self.message = 'prev video'
                return

    def on_next_video(self, *largs):
        playitem = self.playitem
        playlist = self.playlist[:]
        for i in xrange(len(playlist)):
            if playlist[i][0] == playitem[0] and i < len(playlist)-1:
                self.dispatch('on_open_playitem', playlist[i+1])
                self.message = 'next video'
                return

    def on_prev_frame(self, *largs):
        if self.duration == 0:
            return
        step = 1 / float(self.yuv_fps) if self.yuv_fps != 0. else 1.
        seek = (self.position - step) / float(self.duration)
        self.seek(seek)
        self.message = 'prev 1 frame'

    def on_next_frame(self, *largs):
        if self.duration == 0:
            return
        step = 1 / float(self.yuv_fps) if self.yuv_fps != 0. else 1.
        seek = (self.position + step) / float(self.duration)
        self.seek(seek)
        self.message = 'next 1 frame'

    def on_play_pause(self, *largs):
        if not self.source:
            self.dispatch('on_select_playitem')
            return
        if self.state == 'play':
            self.state = 'pause'
        else:
            self.state = 'play'
        self.message = self.state

    def on_select_playitem(self, *largs):
        pass

    def on_select_playlist(self, *largs):
        pass

    def on_config_yuvparam(self, *largs):
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
                               texture=self._on_load_video,
                               state=self.setter('state'),
                               duration=self.setter('duration'),
                               position=self.setter('position'),
                               volume=self.setter('volume'))
            self._video = None

        filename = resource_find(self.source)
        if filename is None:
            return

        cls = YuvVideo if filename.lower().endswith('.yuv') else Video
        self._video = cls(format=self.format,
                          colorfmt=self.colorfmt,
                          yuv_size=self.yuv_size,
                          yuv_fps=self.yuv_fps,
                          source=filename,
                          state=self.state,
                          volume=self.volume,
                          pos_hint={'x':0, 'y':0},
                          **self.options)
        self._video.bind(on_load=self._on_load_video,
                         texture=self._on_load_video,
                         state=self.setter('state'),
                         duration=self.setter('duration'),
                         position=self.setter('position'),
                         volume=self.setter('volume'))

    def _on_load_video(self, *largs):
        if self._video is not None:
            self._video.unbind(texture=self._on_load_video)

        self.display.clear_widgets()
        self.display.add_widget(self._video)

        source, format, colorfmt, yuv_size, yuv_fps = self.playitem

        title = '%s' % basename(source)
        if source.lower().endswith('.yuv'):
            title += ' %s:%s@%2.f' % (
                '%dx%d' % tuple(yuv_size),
                format.upper(),
                yuv_fps
            )
        window = EventLoop.window
        window.title = title

        playlist = self.playlist[:]
        for playitem in playlist:
            if playitem[0] == source:
                playitem[1:] = self.playitem[1:]
                return
        self.playlist.append(self.playitem[:])
