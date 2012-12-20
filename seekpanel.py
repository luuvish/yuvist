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
from kivy.properties import (ObjectProperty, NumericProperty, StringProperty)
from kivy.animation import Animation
from kivy.factory import Factory
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout


Builder.load_string('''
<SeekPanel>:
    orientation: 'horizontal'
    height: 13

    Label:
        size_hint_x: None
        width: 50
        text: '[size=10][color=444]%s[/color][/size]' % root.lseek
        markup: True
    SeekBar:
        video: root.video
        max: max(root.duration, root.position, 1)
        value: root.position
    Label:
        size_hint_x: None
        width: 50
        text: '[size=10][color=444]-%s[/color][/size]' % root.rseek
        markup: True
''')


class SeekBar(ProgressBar):
    video = ObjectProperty(None)
    seek  = NumericProperty(None, allownone=True)
    alpha = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(SeekBar, self).__init__(**kwargs)
        self.bubble = Factory.Bubble(size=(72,44))
        self.label = Factory.Label(text='0:00')
        self.bubble.add_widget(self.label)
        self.add_widget(self.bubble)
        self.bind(pos=self._update_bubble,
                  size=self._update_bubble,
                  seek=self._update_bubble)

    def on_video(self, instance, value):
        self.video.bind(position=self._update_bubble, state=self._showhide_bubble)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        self._show_bubble()
        touch.grab(self)
        self._update_seek(touch.x)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        self._update_seek(touch.x)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        if self.seek:
            self.video.seek(self.seek)
        self.seek = None
        self._hide_bubble()
        return True

    def _update_seek(self, x):
        if self.width == 0:
            return
        x = max(self.x, min(self.right, x)) - self.x
        self.seek = x / float(self.width)

    def _show_bubble(self):
        self.alpha = 1.
        Animation.stop_all(self, 'alpha')

    def _hide_bubble(self):
        self.alpha = 1.
        Animation(alpha=0, d=4, t='in_out_expo').start(self)

    def on_alpha(self, instance, value):
        self.bubble.background_color = (1, 1, 1, value)
        self.label.color = (1, 1, 1, value)

    def _update_bubble(self, *l):
        seek = self.seek
        if self.seek is None:
            if self.video.duration == 0:
                seek = 0
            else:
                seek = self.video.position / self.video.duration
        d = self.video.duration * seek
        hours   = int(d / 3600)
        minutes = int(d / 60) - (hours * 60)
        seconds = int(d) - (hours * 3600 + minutes * 60)
        self.label.text = '%02d:%02d:%02d' % (hours, minutes, seconds)
        self.bubble.center_x = self.x + seek * self.width
        self.bubble.y = self.top

    def _showhide_bubble(self, instance, value):
        if value == 'play':
            self._hide_bubble()
        else:
            self._show_bubble()


class SeekPanel(BoxLayout):
    video    = ObjectProperty(None)
    duration = NumericProperty(-1)
    position = NumericProperty(0)
    lseek    = StringProperty('00:00:00')
    rseek    = StringProperty('00:00:00')

    def __init__(self, **kwargs):
        super(SeekPanel, self).__init__(**kwargs)

    def on_video(self, instance, value):
        self.video.bind(position=self._update_seek, duration=self._update_seek)

    def _update_seek(self, *largs):
        def format(position):
            hours   = int(position / 3600)
            minutes = int(position / 60) - (hours * 60)
            seconds = int(position) - (hours * 3600 + minutes * 60)
            return '%02d:%02d:%02d' % (hours, minutes, seconds)
        self.duration = self.video.duration
        self.position = self.video.position
        if self.duration == 0:
            self.lseek = '00:00:00'
            self.rseek = '00:00:00'
        else:
            seek = self.position / float(self.duration)
            self.lseek = format(self.duration * seek)
            self.rseek = format(self.duration * (1. - seek))
