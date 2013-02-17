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

__all__ = ('YuvistPanel', )

import os

from kivy.resources import resource_find
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, \
        ObjectProperty, ListProperty, DictProperty, OptionProperty, ReferenceListProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.video import Video

from core.video import YUV_CHROMA_FORMAT
from core.video import OUT_COLOR_FORMAT

from .seekbar import SeekBar
from .volumeslider import VolumeSlider
from .dialog_open import OpenDialog
from .dialog_yuv_cfg import YuvCfgDialog
from .dialog_playlist import PlaylistDialog
from .yuvvideo import YuvVideo


class ImageButton(Button):
    pass


class YuvistPanel(GridLayout):

    source           = StringProperty('')
    duration         = NumericProperty(-1)
    position         = NumericProperty(0)
    volume           = NumericProperty(1.0)
    state            = OptionProperty('stop', options=('play', 'pause', 'stop'))
    play             = BooleanProperty(False)
    fullscreen       = BooleanProperty(False)
    allow_fullscreen = BooleanProperty(True)
    options          = DictProperty({})

    container        = ObjectProperty(None)

    time_past        = StringProperty('00:00:00')
    time_next        = StringProperty('00:00:00')
    volume_muted     = BooleanProperty(False)
    volume_slider    = ObjectProperty(None)

    format           = OptionProperty(YUV_CHROMA_FORMAT[1], options=YUV_CHROMA_FORMAT)
    colorfmt         = OptionProperty(OUT_COLOR_FORMAT[1], options=OUT_COLOR_FORMAT)
    yuv_size         = ListProperty([1920, 1080])
    yuv_fps          = NumericProperty(30.)

    playpath         = StringProperty('.')
    playlist         = ListProperty([])
    playitem         = ReferenceListProperty(source, format, colorfmt, yuv_size, yuv_fps)

    def __init__(self, **kwargs):
        self._video = None
        super(YuvistPanel, self).__init__(**kwargs)

        self.bind(position=self._update_seek_time, duration=self._update_seek_time)
        self.volume_slider.value_normalized = self.volume

        Window.bind(on_dropfile=self._drop_file)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, Window)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

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

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if touch.is_double_tap and self.allow_fullscreen:
            self.fullscreen = not self.fullscreen
            return True
        return super(YuvistPanel, self).on_touch_down(touch)

    def on_fullscreen(self, instance, value):
        window = self.get_parent_window()
        if not window:
            Logger.warning('VideoPlayer: Cannot switch to fullscreen, window not found.')
            if value:
                self.fullscreen = False
            return
        if not self.parent:
            Logger.warning('VideoPlayer: Cannot switch to fullscreen, no parent.')
            if value:
                self.fullscreen = False
            return

        if value:
            self._fullscreen_state = state = {
                'parent':          self.parent,
                'pos':             self.pos,
                'size':            self.size,
                'pos_hint':        self.pos_hint,
                'size_hint':       self.size_hint,
                'window_children': window.children[:]
            }

            # remove all window children
            for child in window.children[:]:
                window.remove_widget(child)

            # put the video in fullscreen
            if state['parent'] is not window:
                state['parent'].remove_widget(self)
            window.add_widget(self)

            # ensure the video widget is in 0, 0, and the size will be reajusted
            self.pos = (0, 0)
            self.size = (100, 100)
            self.pos_hint = {}
            self.size_hint = (1, 1)
        else:
            state = self._fullscreen_state
            window.remove_widget(self)
            for child in state['window_children']:
                window.add_widget(child)
            self.pos_hint = state['pos_hint']
            self.size_hint = state['size_hint']
            self.pos = state['pos']
            self.size = state['size']
            if state['parent'] is not window:
                state['parent'].add_widget(self)

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
        self._update_playlist()

        Window.title = '%s %s:%s@%2.f' % (
            os.path.basename(self.source),
            '%dx%d' % tuple(self.yuv_size),
            self.format.upper(),
            self.yuv_fps
        )

    def _play_started(self, instance, value):
        self.container.clear_widgets()
        self.container.add_widget(self._video)

    def _update_playlist(self, *largs):
        playlist = self.playlist[:]
        for playitem in playlist:
            if playitem[0] == self.source:
                playitem[1:] = self.playitem[1:]
                return
        self.playlist.append(self.playitem[:])

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
            self._open_file()
            return
        if self.state == 'play':
            self.state = 'pause'
        else:
            self.state = 'play'

    def _prev_movie(self):
        playlist = self.playlist[:]
        for i in xrange(len(playlist)):
            if playlist[i][0] == self.source and i > 0:
                self.playitem = playlist[i-1][:]
                self.state = 'play'
                return

    def _next_movie(self):
        playlist = self.playlist[:]
        for i in xrange(len(playlist)):
            if playlist[i][0] == self.source and i < len(playlist)-1:
                self.playitem = playlist[i+1][:]
                self.state = 'play'
                return

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

    def _open_file(self):
        def confirm(path, file):
            self.playpath = path
            self.source = os.path.join(path, file)
            self.state = 'play'
        popup = OpenDialog(path=self.playpath, confirm=confirm)
        popup.open()

    def _config_yuv_cfg(self):
        def confirm(format, yuv_size):
            self.playitem = [self.source, format, self.colorfmt, yuv_size, self.yuv_fps]
            self.state = 'play'
        popup = YuvCfgDialog(format=self.format, yuv_size=self.yuv_size, confirm=confirm)
        popup.open()

    def _config_playlist(self):
        def confirm(playitem):
            self.playitem = playitem[:]
            self.state = 'play'
        popup = PlaylistDialog(playlist=self.playlist, confirm=confirm)
        popup.open()

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

    def _drop_file(filename):
        print 'dropfile %s' % filename
        self.source = filename
        self.state = 'play'


if __name__ == '__main__':
    import sys
    from kivy.base import runTouchApp
    runTouchApp(Front(source=sys.argv[1]))
