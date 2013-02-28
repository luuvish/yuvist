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

__all__ = ('MessageBox', )

from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout


Builder.load_string('''
<MessageBox>:
    size_hint: (None, None)
    width: max(message.texture_size[0] + root.padding[0], 1)
    height: max(message.texture_size[1] + root.padding[1], 1)

    Button:
        id: message
        background_normal: 'atlas://data/images/defaulttheme/bubble'
        background_down: self.background_normal
        color: root.color
        text: root.text
''')


class MessageBox(RelativeLayout):

    padding = ListProperty([12, 12])
    color   = ListProperty([1, 1, 1, 1])
    text    = StringProperty('')

    def __init__(self, **kwargs):
        self._anim = None
        super(MessageBox, self).__init__(**kwargs)

    def show(self, text='', duration=10):
        self.hide()
        self.text = text
        self._anim  = Animation(opacity=1, d=1, t='in_out_expo')
        self._anim += Animation(opacity=0, d=duration-1, t='in_out_expo')
        self._anim.start(self)

    def hide(self):
        if self._anim is not None:
            self._anim.cancel(self)
            self._anim = None
        self.opacity = 0
