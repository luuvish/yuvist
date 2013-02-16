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

__all__ = ('VolumeSlider', )

from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, NumericProperty, \
        AliasProperty, OptionProperty, ReferenceListProperty, BoundedNumericProperty


Builder.load_string('''
<VolumeSlider>:
    orientation: 'horizontal'

    canvas:
        Color:
            rgb: 1, 1, 1
        BorderImage:
            border: 0, 0, 0, 0
            pos: int(self.x), int(self.center_y - 1)
            size: 78, 5
            source: self.background
        Rectangle:
            pos: int(self.value_pos[0] - 7), int(self.center_y - 7)
            size: 14, 14
            source: self.cursor
''')


class VolumeSlider(Widget):

    value       = NumericProperty(0.)
    min         = NumericProperty(0.)
    max         = NumericProperty(100.)
    padding     = NumericProperty(7)
    orientation = OptionProperty('horizontal', options=('vertical', 'horizontal'))
    range       = ReferenceListProperty(min, max)
    step        = BoundedNumericProperty(0, min=0)

    state       = OptionProperty('normal', options=('normal', 'down'))
    background  = StringProperty('atlas://data/images/defaulttheme/sliderh_background')
    cursor      = StringProperty('atlas://data/images/defaulttheme/slider_cursor')

    def get_norm_value(self):
        vmin = self.min
        d = self.max - vmin
        if d == 0:
            return 0
        return (self.value - vmin) / float(d)

    def set_norm_value(self, value):
        vmin = self.min
        step = self.step
        val = value * (self.max - vmin) + vmin
        if step == 0:
            self.value = val
        else:
            self.value = min(round((val - vmin) / step) * step + vmin, self.max)
    value_normalized = AliasProperty(get_norm_value, set_norm_value,
                                     bind=('value', 'min', 'max', 'step'))

    def get_value_pos(self):
        padding = self.padding
        x = self.x
        y = self.y
        nval = self.value_normalized
        if self.orientation == 'horizontal':
            return (x + padding + nval * (self.width - 2 * padding), y)
        else:
            return (x, y + padding + nval * (self.height - 2 * padding))

    def set_value_pos(self, pos):
        padding = self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.orientation == 'horizontal':
            if self.width == 0:
                self.value_normalized = 0
            else:
                self.value_normalized = (x - self.x - padding) / float(self.width - 2 * padding)
        else:
            if self.height == 0:
                self.value_normalized = 0
            else:
                self.value_normalized = (y - self.y - padding) / float(self.height - 2 * padding)
    value_pos = AliasProperty(get_value_pos, set_value_pos,
                              bind=('x', 'y', 'width', 'height',
                                    'min', 'max', 'value_normalized', 'orientation'))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self.value_pos = touch.pos
            self.state = 'down'
            return True

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self.value_pos = touch.pos
            return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            self.value_pos = touch.pos
            self.state = 'normal'
            return True
