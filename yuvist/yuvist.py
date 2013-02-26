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


__version__ = '0.9.2'


import kivy
kivy.require('1.5.1')

from os.path import basename, join

from kivy.utils import platform
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty, ListProperty, ObjectProperty
from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

from uix.frontpanel import FrontPanel
from uix.osd import OnScreenDisplay
from uix.dialog_open import OpenDialog
from uix.dialog_yuv_cfg import YuvCfgDialog
from uix.dialog_playlist import PlaylistDialog


Builder.load_string('''
<Yuvist>:
    display: video
    osd: osd
    front: front

    FloatLayout:
        id: video
        size_hint: (None, None)
        width: root.width
        height: root.height - self.y
        pos: (0, 0 if root.fullscreen else front.height)

    OnScreenDisplay:
        id: osd
        pos: 10, root.height - self.height - 10

    FrontPanel:
        id: front
''')


class Yuvist(FloatLayout):

    popup            = ObjectProperty(None, allownone=True)
    osd              = ObjectProperty(None)
    front            = ObjectProperty(None)
    display          = ObjectProperty(None)
    fullscreen       = BooleanProperty(False)
    allow_fullscreen = BooleanProperty(True)

    playpath         = StringProperty('.')
    playlist         = ListProperty([])

    def __init__(self, **kwargs):

        super(Yuvist, self).__init__(**kwargs)

        self.front.bind(on_load_video=self._on_load_video,
                        on_prev_video=self._on_prev_video,
                        on_next_video=self._on_next_video,
                        on_prev_frame=self._on_prev_frame,
                        on_next_frame=self._on_next_frame,
                        on_play_pause=self._on_play_pause,
                        on_open_file=self._on_open_file,
                        on_config_yuv_cfg=self._on_config_yuv_cfg,
                        on_config_playlist=self._on_config_playlist)

        from kivy.core.window import Window
        Window.bind(on_dropfile=self._drop_file)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, Window)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

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

            import pygame
            window.size = pygame.display.list_modes()[0]
            self.osd.show_message('fullscreen mode')
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

            window.size = state['size']
            self.osd.show_message('window mode')

        window.fullscreen = value

    def _on_load_video(self, front, value):

        self.display.clear_widgets()
        self.display.add_widget(front._video)

        source, format, colorfmt, yuv_size, yuv_fps = value

        window = self.get_parent_window()
        if window:
            window.title = '%s %s:%s@%2.f' % (
                basename(source),
                '%dx%d' % tuple(yuv_size),
                format.upper(),
                yuv_fps
            )

        playlist = self.playlist[:]
        for playitem in playlist:
            if playitem[0] == source:
                playitem[1:] = value[1:]
                return
        self.playlist.append(value[:])

    def _on_prev_video(self, front, *largs):
        playitem = front.playitem
        playlist = self.playlist[:]
        for i in xrange(len(playlist)):
            if playlist[i][0] == playitem[0] and i > 0:
                front.playitem = playlist[i-1][:]
                front.state = 'play'
                self.osd.show_message('prev video')
                return

    def _on_next_video(self, front, *largs):
        playitem = front.playitem
        playlist = self.playlist[:]
        for i in xrange(len(playlist)):
            if playlist[i][0] == playitem[0] and i < len(playlist)-1:
                front.playitem = playlist[i+1][:]
                front.state = 'play'
                self.osd.show_message('next video')
                return

    def _on_prev_frame(self, front, *largs):
        self.osd.show_message('prev 1 frame')

    def _on_next_frame(self, front, *largs):
        self.osd.show_message('next 1 frame')

    def _on_play_pause(self, front, *largs):
        state = 'pause' if front.state == 'play' else 'play'
        self.osd.show_message(state)

    def _on_open_file(self, front, *largs):
        def confirm(path, filename):
            self.playpath = path
            front.source = join(path, filename)
            front.state = 'play'
            self.osd.show_message('open file')
        window = self.get_parent_window()
        size = (window.size[0] - 160, window.size[1] - 100) if window else (700, 500)
        popup = OpenDialog(path=self.playpath, confirm=confirm, size=size)
        popup.open()

    def _on_config_yuv_cfg(self, front, *largs):
        def confirm(format, yuv_size):
            front.playitem = [front.source, format, front.colorfmt, yuv_size, front.yuv_fps]
            front.state = 'play'
            self.osd.show_message('play video')
        popup = YuvCfgDialog(format=front.format, yuv_size=front.yuv_size, confirm=confirm)
        popup.open()

    def _on_config_playlist(self, front, *largs):
        def confirm(playitem):
            front.playitem = playitem[:]
            front.state = 'play'
            self.osd.show_message('play video')
        window = self.get_parent_window()
        size = (window.size[0] - 160, window.size[1] - 100) if window else (700, 500)
        popup = PlaylistDialog(playlist=self.playlist, confirm=confirm, size=size)
        popup.open()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == '1' and 'meta' in modifiers:
            return self._resize(size_hint=(.5, .5))
        if keycode[1] == '2' and 'meta' in modifiers:
            return self._resize(size_hint=(1., 1.))
        if keycode[1] == '3' and 'meta' in modifiers:
            return self._resize(size_hint=(2., 2.))
        if keycode[1] == '4' and 'meta' in modifiers:
            return self._resize(size_hint=(0., 0.))

        if keycode[1] == 'f' and 'meta' in modifiers:
            if self.allow_fullscreen:
                self.fullscreen = not self.fullscreen
            return True
        if keycode[1] == 'enter':
            if self.allow_fullscreen:
                self.fullscreen = not self.fullscreen
            return True

        if keycode[1] == 'up' and 'meta' in modifiers:
            volume = self.front.volume
            volume += 0.1
            if volume > 1.0:
                volume = 1.0
            self.front.volume = volume
            return True
        if keycode[1] == 'down' and 'meta' in modifiers:
            volume = self.front.volume
            volume -= 0.1
            if volume < 0.0:
                volume = 0.0
            self.front.volume = volume
            return True
        if keycode[1] == 'down' and 'meta' in modifiers and 'alt' in modifiers:
            self.front.volume = 0.0
            return True

        if keycode[1] == 'home':
            self.front.seek(0.)
            return True
        if keycode[1] == 'end':
            self.front.seek(1.)
            return True

        if keycode[1] == 'left' and 'meta' in modifiers:
            self.front.dispatch('on_prev_video')
            return True
        if keycode[1] == 'right' and 'meta' in modifiers:
            self.front.dispatch('on_next_video')
            return True
        if keycode[1] == '[':
            self.front.dispatch('on_prev_frame')
            return True
        if keycode[1] == ']':
            self.front.dispatch('on_next_frame')
            return True
        if keycode[1] == 'spacebar':
            self.front.dispatch('on_play_pause')
            return True

        if keycode[1] == 'o' and 'meta' in modifiers:
            self.front.dispatch('on_open_file')
            return True
        if keycode[1] == 'c' and 'meta' in modifiers and 'alt' in modifiers:
            self.front.dispatch('on_config_yuv_cfg')
            return True
        if keycode[1] == 'l' and 'meta' in modifiers and 'alt' in modifiers:
            self.front.dispatch('on_config_playlist')
            return True

        if keycode[1] == 'q' and 'meta' in modifiers:
            app = App.get_running_app()
            app.stop()
            return True

        return True

    def _resize(self, size_hint=(1., 1.)):
        if self.fullscreen:
            return True

        import pygame
        w, h   = pygame.display.list_modes()[0]
        pad_h  = 0 if self.fullscreen else self.front.height
        size   = self.front.yuv_size
        ratio  = float(size[0]) / float(size[1])
        tw, th = int(size[0] * size_hint[0]), int(size[1] * size_hint[1])

        if not self.fullscreen:
            h -= pad_h + 44

        if size_hint == (0., 0.):
            tw, th = w, h

        iw = min(w, tw)
        ih = iw / ratio
        if ih > h:
            ih = min(h, th)
            iw = ih * ratio

        if not self.fullscreen:
            window = self.get_parent_window()
            window.size = int(iw), int(ih + pad_h)

        if size_hint == (.5, .5):
            self.osd.show_message('half size')
        elif size_hint == (1., 1.):
            self.osd.show_message('normal size')
        elif size_hint == (2., 2.):
            self.osd.show_message('double size')
        elif size_hint == (.0, .0):
            self.osd.show_message('fit to window')
        return True

    def _drop_file(filename):
        print 'dropfile %s' % filename
        self.source = filename
        self.state = 'play'


class YuvistApp(App):

    title = 'Yuvist-' + __version__
    icon  = 'data/images/yuvist.png'

    def __init__(self, **kwargs):

        super(YuvistApp, self).__init__(**kwargs)

        self.filename = kwargs.get('filename', '')
        self.format   = kwargs.get('format', 'yuv420')
        self.yuv_size = kwargs.get('yuv_size', [1920, 1080])
        self.state    = kwargs.get('state', 'pause')

    def build(self):
        return Yuvist(source=self.filename,
                      format=self.format,
                      yuv_size=self.yuv_size,
                      state=self.state)


if __name__ == '__main__':

    print("Kivy YUV Image Viewer")
    print("Copyright (C) 2012 Luuvish <luuvish@gmail.com>")

    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else ''
    app = YuvistApp(filename=filename)
    app.run()
