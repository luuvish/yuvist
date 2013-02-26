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

__all__ = ('OnScreenDisplay', )

from kivy.lang import Builder
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.animation import Animation, AnimationTransition
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

from .onscreen import OnScreen, OnScreenTransition, OnScreenManager

Builder.load_string('''
<MessageBox>:
    padding: 10, 10
    size_hint: (None, None)
    size: max(self.texture_size[0], 1), max(self.texture_size[1], 1)

    canvas:
        Clear
        Color:
            rgba: self.background_color
        Rectangle:
            size: self.size
            pos: self.pos
        Color:
            rgba: self.outline_color
        Rectangle:
            size: self.texture_size
            pos: int(self.center_x - self.texture_size[0] / 2.), int(self.center_y - self.texture_size[1] / 2.)
        Color:
            rgba: self.color
        Rectangle:
            texture: self.texture
            size: self.texture_size
            pos: int(self.center_x - self.texture_size[0] / 2.), int(self.center_y - self.texture_size[1] / 2.)
''')


class MessageBox(OnScreen, Label):

    background_color = ListProperty([.4, .4, .4, 1.])
    outline_color    = ListProperty([.8, .8, .8, 1.])
    color            = ListProperty([.4, 1., 1., 1.])

    def on_pre_enter(self, *args):
        self.manager.size_hint = (None, None)
        self.bind(size=self.manager.setter('size'))

    def on_enter(self, *args):
        pass

    def on_pre_leave(self, *args):
        pass

    def on_leave(self, *args):
        pass


class FadeScreen(OnScreenTransition):

    duration = NumericProperty(10)

    def on_progress(self, progression):
        progression = AnimationTransition.in_out_expo(progression)
        self.screen.color[3] = 1. - progression

    def on_complete(self):
        super(FadeScreen, self).on_complete()


class OnScreenDisplay(OnScreenManager):

    transition = ObjectProperty(FadeScreen())
    screen     = ObjectProperty(MessageBox())

    def show_message(self, text=''):
        self.screen.text = text
        self.start()
