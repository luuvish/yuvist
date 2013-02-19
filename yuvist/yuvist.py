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

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty, ListProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout

from os.path import dirname, basename, join

from uix.dialog_open import OpenDialog
from uix.dialog_yuv_cfg import YuvCfgDialog
from uix.dialog_playlist import PlaylistDialog


class Yuvist(GridLayout):

    front            = ObjectProperty(None)
    display          = ObjectProperty(None)
    fullscreen       = BooleanProperty(False)
    allow_fullscreen = BooleanProperty(True)
    desktop_size     = ListProperty([0, 0])

    playpath         = StringProperty('.')
    playlist         = ListProperty([])

    def __init__(self, **kwargs):

        super(Yuvist, self).__init__(**kwargs)

        from kivy.core.window import Window
        self.desktop_size = kwargs.get('desktop_size', Window.size)

        Window.bind(on_dropfile=self._drop_file)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, Window)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def prev_movie(self, playitem):
        playlist = self.playlist[:]
        for i in xrange(len(playlist)):
            if playlist[i][0] == playitem[0] and i > 0:
                self.front.playitem = playlist[i-1]
                self.front.state = 'play'
                return

    def next_movie(self, playitem):
        playlist = self.playlist[:]
        for i in xrange(len(playlist)):
            if playlist[i][0] == playitem[0] and i < len(playlist)-1:
                self.front.playitem = playlist[i+1]
                self.front.state = 'play'
                return

    def update_playlist(self, newitem):
        playlist = self.playlist[:]
        for playitem in playlist:
            if playitem[0] == newitem[0]:
                playitem[1:] = newitem[1:]
                return
        self.playlist.append(newitem[:])

    def open_file(self):
        front = self.front
        def confirm(path, filename):
            self.playpath = path
            front.source = join(path, filename)
            front.state = 'play'
        window = self.get_parent_window()
        size = (window.size[0] - 160, window.size[1] - 100) if window else (700, 500)
        popup = OpenDialog(path=self.playpath, confirm=confirm, size=size)
        popup.open()

    def config_yuv_cfg(self):
        front = self.front
        def confirm(format, yuv_size):
            front.playitem = [front.source, format, front.colorfmt, yuv_size, front.yuv_fps]
            front.state = 'play'
        popup = YuvCfgDialog(format=front.format, yuv_size=front.yuv_size, confirm=confirm)
        popup.open()

    def config_playlist(self):
        front = self.front
        def confirm(playitem):
            front.playitem = playitem[:]
            front.state = 'play'
        window = self.get_parent_window()
        size = (window.size[0] - 160, window.size[1] - 100) if window else (700, 500)
        popup = PlaylistDialog(playlist=self.playlist, confirm=confirm, size=size)
        popup.open()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if touch.is_double_tap and self.allow_fullscreen:
            self.fullscreen = not self.fullscreen
            return True
        return super(Yuvist, self).on_touch_down(touch)

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

            self.prev_size = window.size
            window.size = self.desktop_size
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

            window.size = self.prev_size

        window.fullscreen = value

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        from kivy.utils import platform
        if keycode == (111, 'o') and (
            platform() == 'win'    and 'ctrl' in modifiers or
            platform() == 'linux'  and 'ctrl' in modifiers or
            platform() == 'macosx' and 'meta' in modifiers):
            self.open_file()
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


class YuvistApp(App):

    title = 'Yuvist-' + __version__
    icon  = 'data/images/yuvist.png'

    def __init__(self, **kwargs):

        super(YuvistApp, self).__init__(**kwargs)

        import pygame
        pygame.display.init()
        info = pygame.display.Info()
        self.desktop_size = [info.current_w, info.current_h]

        self.filename = kwargs.get('filename', '')
        self.format   = kwargs.get('format', 'yuv420')
        self.yuv_size = kwargs.get('yuv_size', [1920, 1080])
        self.state    = kwargs.get('state', 'pause')

    def build(self):
        return Yuvist(source=self.filename,
                      format=self.format,
                      yuv_size=self.yuv_size,
                      state=self.state,
                      desktop_size=self.desktop_size)


if __name__ == '__main__':

    print("Kivy YUV Image Viewer")
    print("Copyright (C) 2012 Luuvish <luuvish@gmail.com>")

    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else ''
    app = YuvistApp(filename=filename)
    app.run()
