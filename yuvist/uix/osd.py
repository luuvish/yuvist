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
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.button import Button


Builder.load_string('''
<OnScreenDisplay>:
    padding: 10, 10
    size_hint: (None, None)
    width: max(self.texture_size[0] + 2 * self.outer_size[0], 1)
    height: max(self.texture_size[0] + 2 * self.outer_size[1], 1)

    canvas:
        Clear
        Color:
            rgba: self.color
        Rectangle:
            texture: self.texture
            size: self.texture_size
            pos: int(self.center_x - self.texture_size[0] / 2.), int(self.center_y - self.texture_size[1] / 2.)
''')


class OnScreenDisplay(Label):

    outer_size  = ListProperty([2, 2])
    outer_color = ListProperty([1., 1., 1., 1.])
    inner_color = ListProperty([.4, .4, .4, .4])
    color       = ListProperty([.8, .8, .8, 1.])

    anim  = ObjectProperty(None, allownone=True)
    alpha = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(OnScreenDisplay, self).__init__(**kwargs)
        self.alpha = 0.

    def message(self, text='', timeout=10):
        if self.anim is not None:
            self.alpha = 0.
            self.anim.stop(self)
            self.anim = None

        self.alpha = 1.
        self.text  = text
        self.anim  = Animation(alpha=1, d=timeout-4, t='in_out_expo')
        self.anim += Animation(alpha=0, d=4, t='in_out_expo')
        self.anim.start(self)

    def on_alpha(self, instance, value):
        self.outer_color[3] = 1. * value
        self.inner_color[3] = .4 * value
        self.color[3]       = 1. * value
