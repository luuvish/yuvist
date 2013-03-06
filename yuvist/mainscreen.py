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

__all__ = ('MainScreen', )

from os.path import join

import yuvist

from kivy.lang import Builder
from kivy.base import EventLoop, stopTouchApp
from kivy.properties import StringProperty, ListProperty, \
        ObjectProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout

from yuvist.uix.messagebox import MessageBox
from yuvist.uix.frontpanel import FrontPanel
from yuvist.uix.controller import Controller
from yuvist.uix.popup_playitem import PlayitemPopup
from yuvist.uix.popup_playlist import PlaylistPopup
from yuvist.uix.popup_yuvparam import YuvParamPopup


Builder.load_string('''
<MainScreen>:
    msgbox: msgbox
    display: display
    front: front

    FloatLayout:
        id: display
        size_hint: (None, None)
        width: root.width
        height: root.height - self.y
        pos: (0, 0 if root.fullscreen else front.height)

    MessageBox:
        id: msgbox
        pos: 10, root.height - self.height - 10

    FrontPanel:
        id: front
''')


class MainScreen(FloatLayout):

    msgbox     = ObjectProperty(None)
    display    = ObjectProperty(None)
    front      = ObjectProperty(None)
    controller = ObjectProperty(None, allownone=True)
    popup      = ObjectProperty(None, allownone=True)

    playpath   = StringProperty('.')
    playlist   = ListProperty([])

    fullscreen       = BooleanProperty(False)
    allow_fullscreen = BooleanProperty(True)

    def __init__(self, **kwargs):

        super(MainScreen, self).__init__(**kwargs)

        self.controller = Controller(display=self.display,
                                     playlist=self.playlist)
        self.controller.bind(message=self._on_message,
                             on_fullscreen=self._on_fullscreen,
                             on_customsize=self._on_customsize,
                             on_close=self._on_close,
                             on_select_playitem=self._on_select_playitem,
                             on_select_playlist=self._on_select_playlist,
                             on_config_yuvparam=self._on_config_yuvparam)

        self.front.controller = self.controller

        window = EventLoop.window
        self._keyboard = window.request_keyboard(self._on_keyboard_closed, window)
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
            self.front.hide()
            self.msgbox.show('fullscreen mode')
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
            self.front.hide()
            self.front.opacity = 1
            self.msgbox.show('window mode')

        window.fullscreen = value

    def on_touch_down(self, touch):
        if self.fullscreen:
            self.front.show()
        return super(MainScreen, self).on_touch_down(touch)

    def _on_message(self, instance, value):
        self.msgbox.show(value)

    def _on_fullscreen(self, instance, *largs):
        if self.allow_fullscreen:
            self.fullscreen = not self.fullscreen

    def _on_customsize(self, instance, size, size_hint=(1., 1.)):
        if self.fullscreen:
            return True

        import pygame
        w, h   = pygame.display.list_modes()[0]
        pad_h  = 0 if self.fullscreen else self.front.height
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
            window = EventLoop.window
            window.size = int(iw), int(ih + pad_h)

        if size_hint == (.5, .5):
            self.msgbox.show('half size')
        elif size_hint == (1., 1.):
            self.msgbox.show('normal size')
        elif size_hint == (2., 2.):
            self.msgbox.show('double size')
        elif size_hint == (.0, .0):
            self.msgbox.show('fit to window')

    def _on_close(self, instance, *largs):
        stopTouchApp()

    def _on_select_playitem(self, instance, *largs):

        if isinstance(self.popup, PlayitemPopup):
            return
        if self.popup is not None:
            self.popup.dismiss()

        def confirm(path, filename):
            self.playpath = path
            self.controller.dispatch('on_open_playitem', join(path, filename))
            self.msgbox.show('open file')

        def dismiss(*largs):
            self.popup = None

        window = EventLoop.window
        size = (window.size[0] - 160, window.size[1] - 100)
        self.popup = PlayitemPopup(path=self.playpath, confirm=confirm, size=size)
        self.popup.bind(on_dismiss=dismiss)
        self.popup.open()

    def _on_select_playlist(self, instance, *largs):

        if isinstance(self.popup, PlaylistPopup):
            return
        if self.popup is not None:
            self.popup.dismiss()

        def confirm(playitem):
            self.controller.dispatch('on_open_playitem', playitem)
            self.msgbox.show('select video')

        def dismiss(*largs):
            self.popup = None

        window = EventLoop.window
        size = (window.size[0] - 160, window.size[1] - 100)
        self.popup = PlaylistPopup(playlist=self.playlist, confirm=confirm, size=size)
        self.popup.bind(on_dismiss=dismiss)
        self.popup.open()

    def _on_config_yuvparam(self, instance, *largs):

        if isinstance(self.popup, YuvParamPopup):
            return
        if self.popup is not None:
            self.popup.dismiss()

        source, format, colorfmt, yuv_size, yuv_fps = instance.playitem

        def confirm(format, yuv_size):
            playitem = [source, format, colorfmt, yuv_size, yuv_fps]
            self.dispatch('on_open_playitem', playitem)
            self.msgbox.show('play video')

        def dismiss(*largs):
            self.popup = None

        self.popup = YuvParamPopup(format=format, yuv_size=yuv_size, confirm=confirm)
        self.popup.bind(on_dismiss=dismiss)
        self.popup.open()

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        controller = self.controller

        if keycode[1] == '1' and 'meta' in modifiers:
            controller.dispatch('on_customsize', controller.yuv_size, (.5, .5))
            return True
        if keycode[1] == '2' and 'meta' in modifiers:
            controller.dispatch('on_customsize', controller.yuv_size, (1., 1.))
            return True
        if keycode[1] == '3' and 'meta' in modifiers:
            controller.dispatch('on_customsize', controller.yuv_size, (2., 2.))
            return True
        if keycode[1] == '4' and 'meta' in modifiers:
            controller.dispatch('on_customsize', controller.yuv_size, (0., 0.))
            return True

        if keycode[1] == 'f' and 'meta' in modifiers:
            controller.dispatch('on_fullscreen')
            return True
        if keycode[1] == 'enter':
            controller.dispatch('on_fullscreen')
            return True

        if keycode[1] == 'down' and 'meta' in modifiers and 'alt' in modifiers:
            controller.volume = 0.0
            return True
        if keycode[1] == 'up' and 'meta' in modifiers:
            controller.volume = min(controller.volume + .1, 1.)
            return True
        if keycode[1] == 'down' and 'meta' in modifiers:
            controller.volume = max(controller.volume - .1, 0.)
            return True

        if keycode[1] == 'home':
            controller.seek(0.)
            return True
        if keycode[1] == 'end':
            controller.seek(1.)
            return True

        if keycode[1] == 'left' and 'meta' in modifiers:
            controller.dispatch('on_prev_video')
            return True
        if keycode[1] == 'right' and 'meta' in modifiers:
            controller.dispatch('on_next_video')
            return True
        if keycode[1] == '[':
            controller.dispatch('on_prev_frame')
            return True
        if keycode[1] == ']':
            controller.dispatch('on_next_frame')
            return True
        if keycode[1] == 'spacebar':
            controller.dispatch('on_play_pause')
            return True

        if keycode[1] == 'o' and 'meta' in modifiers:
            controller.dispatch('on_select_playitem')
            return True
        if keycode[1] == 'l' and 'meta' in modifiers and 'alt' in modifiers:
            controller.dispatch('on_select_playlist')
            return True
        if keycode[1] == 'c' and 'meta' in modifiers and 'alt' in modifiers:
            controller.dispatch('on_config_yuvparam')
            return True

        if keycode[1] == 'q' and 'meta' in modifiers:
            controller.dispatch('on_close')
            return True

        return True
