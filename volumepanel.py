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

from kivy.lang import Builder
from kivy.properties import (ObjectProperty, BooleanProperty,
                             OptionProperty, NumericProperty, AliasProperty,
                             ReferenceListProperty, BoundedNumericProperty)
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout


Builder.load_string('''
<VolumeSlider>:
    canvas:
        Color:
            rgb: 1, 1, 1
        BorderImage:
            border: 0, 0, 0, 0
            pos: int(self.x), int(self.center_y - 1)
            size: 78, 5
            source: 'images/MainVolumeSliderTrack.tiff'
        Rectangle:
            pos: int(self.value_pos[0] - 7), int(self.center_y - 7)
            size: 14, 14
            source: 'images/MainVolumeSliderKnob.tiff' if self.state == 'normal' else 'images/MainVolumeSliderKnobPressed.tiff'

<VolumePanel>:
    size: 102, 51
    slider: slider

    Button:
        pos: 4, 29
        size_hint: None, None
        size: 18, 17
        border: 0, 0, 0, 0
        background_normal: 'images/MainVolumeMute.tiff' if root.muted or slider.value_normalized == 0 else 'images/MainVolume1.tiff' if slider.value_normalized < .33 else 'images/MainVolume2.tiff' if slider.value_normalized < .66 else 'images/MainVolume3.tiff'
        background_down: 'images/MainVolumeMute.tiff' if root.muted or slider.value_normalized == 0 else 'images/MainVolume1.tiff' if slider.value_normalized < .33 else 'images/MainVolume2.tiff' if slider.value_normalized < .66 else 'images/MainVolume3.tiff'
        on_press: root._press_muted()

    VolumeSlider:
        id: slider
        pos: 24, 35
        size_hint: None, None
        size: 78, 5
''')


class VolumeSlider(Widget):
    state   = OptionProperty('normal', options=('normal', 'down'))
    value   = NumericProperty(0.)
    min     = NumericProperty(0.)
    max     = NumericProperty(100.)
    padding = NumericProperty(7)
    range   = ReferenceListProperty(min, max)
    step    = BoundedNumericProperty(0, min=0)

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
        return (x + padding + nval * (self.width - 2 * padding), y)

    def set_value_pos(self, pos):
        padding = self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.width == 0:
            self.value_normalized = 0
        else:
            self.value_normalized = (x - self.x - padding) / float(self.width - 2 * padding)
    value_pos = AliasProperty(get_value_pos, set_value_pos,
                              bind=('x', 'y', 'width', 'height',
                                    'min', 'max', 'value_normalized'))

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


class VolumePanel(RelativeLayout):
    video  = ObjectProperty(None)
    muted  = BooleanProperty(False)
    slider = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(VolumePanel, self).__init__(**kwargs)

    def on_video(self, instance, value):
        self.slider.value_normalized = self.video.volume
        self.slider.bind(value_normalized=self._change_volume)

    def _press_muted(self):
        self.muted = not self.muted
        self._change_volume(self, self.slider.value_normalized)

    def _change_volume(self, instance, value):
        self.video.volume = 0 if self.muted else value
