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

import os

from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, \
        ObjectProperty, ListProperty, DictProperty, OptionProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

from .seekbar import SeekBar
from .volumeslider import VolumeSlider
from .dialog_open import OpenDialog
from .dialog_yuv_cfg import YuvCfgDialog
from .dialog_playlist import PlaylistDialog


class ImageButton(Button):
    pass


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

    lseek      = StringProperty('00:00:00')
    rseek      = StringProperty('00:00:00')
    muted      = BooleanProperty(False)
    slider     = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._image = None
        super(Front, self).__init__(**kwargs)

        self._path = '.'
        Window.bind(on_dropfile=self._drop_file)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, Window)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.bind(source=self._image_init, format=self._image_init, resolution=self._image_init)
        self.bind(position=self._update_seek, duration=self._update_seek)
        self.slider.value_normalized = self.volume
        self.slider.bind(value_normalized=self._change_volume)
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
            self._image = Image(format=self.format,
                                colorfmt='luminance',
                                yuv_size=self.resolution,
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

    def _update_seek(self, *largs):
        def format(position):
            hours   = int(position / 3600)
            minutes = int(position / 60) - (hours * 60)
            seconds = int(position) - (hours * 3600 + minutes * 60)
            return '%02d:%02d:%02d' % (hours, minutes, seconds)
        if self.duration == 0:
            self.lseek = '00:00:00'
            self.rseek = '00:00:00'
        else:
            seek = self.position / float(self.duration)
            self.lseek = format(self.duration * seek)
            self.rseek = format(self.duration * (1. - seek))

    def _press_muted(self):
        self.muted = not self.muted
        self._change_volume(self, self.slider.value_normalized)

    def _change_volume(self, instance, value):
        self.volume = 0 if self.muted else value

    def _play_pause(self):
        if not self.source:
            self._open_file()
            return
        if self.state == 'stop':
            self.state = 'play'
        elif self.state == 'play':
            self.state = 'pause'
        else:
            self.state = 'play'

    def _prev_movie(self):
        if not self.source:
            return
        playlist = self.playlist
        for i in xrange(len(playlist)):
            if playlist[i]['source'] == self.source:
                if i > 0:
                    self.source = playlist[i-1]['source']
                    self.format = playlist[i-1]['format']
                    self.resolution = playlist[i-1]['resolution']
                    self.state = 'play'
                    return

    def _next_movie(self):
        if not self.source:
            return
        playlist = self.playlist
        for i in xrange(len(playlist)):
            if playlist[i]['source'] == self.source:
                if i < len(playlist)-1:
                    self.source = playlist[i+1]['source']
                    self.format = playlist[i+1]['format']
                    self.resolution = playlist[i+1]['resolution']
                    self.state = 'play'
                    return

    def _prev_seek(self):
        if self.duration == 0:
            return
        seek = (self.position - 1) / float(self.duration)
        self.seek(seek)

    def _next_seek(self):
        if self.duration == 0:
            return
        seek = (self.position + 1) / float(self.duration)
        self.seek(seek)

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

        def confirm(path, file):
            self.source = os.path.join(path, file)
            self.state = 'play'
            self._path = path

        popup = OpenDialog(path=self._path, confirm=confirm)
        popup.open()

    def _drop_file(filename):
        print 'dropfile %s' % filename
        self.source = filename
        self.state = 'play'

    def _config_resolution(self):
        def confirm(format, resolution):
            self.format = format
            self.resolution = resolution
            self.state = 'play'
        popup = YuvCfgDialog(format=self.format,
                             yuv_size=self.resolution,
                             confirm=confirm)
        popup.open()

    def _config_playlist(self):
        def confirm(playitem):
            self.source = playitem['source']
            self.format = playitem['format']
            self.resolution = playitem['resolution']
            self.state = 'play'
        popup = PlaylistDialog(playlist=self.playlist,
                               confirm=confirm)
        popup.open()


if __name__ == '__main__':
    import sys
    from kivy.base import runTouchApp
    runTouchApp(Front(source=sys.argv[1]))
