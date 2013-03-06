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

__all__ = ('FrontPanel', )

from os.path import dirname, join

from kivy.lang import Builder
from kivy.resources import resource_find
from kivy.properties import NumericProperty, StringProperty, \
        ObjectProperty, BooleanProperty, OptionProperty, AliasProperty
from kivy.animation import Animation
from kivy.uix.videoplayer import VideoPlayerProgressBar
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout


Builder.load_string('''
<VolumeSlider>:
    padding: 7
    orientation: 'horizontal'

    canvas:
        Clear
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

Builder.load_file(resource_find('data/skins/movist.kv'))


class SeekBar(VideoPlayerProgressBar):

    show_bubble = BooleanProperty(False)

    def __init__(self, **kwargs):

        super(SeekBar, self).__init__(**kwargs)

        self.bubble.size = (72,44)
        if not self.show_bubble:
            self.alpha = 0

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
        self.bubble_label.text = '%02d:%02d:%02d' % (hours, minutes, seconds)
        self.bubble.center_x = self.x + seek * self.width
        self.bubble.y = self.top

    def _showhide_bubble(self, instance, value):
        if not self.show_bubble:
            return
        super(SeekBar, self)._showhide_bubble(instance, value)


class VolumeSlider(Slider):

    state      = OptionProperty('normal', options=('normal', 'down'))
    background = StringProperty('atlas://data/images/defaulttheme/sliderh_background')
    cursor     = StringProperty('atlas://data/images/defaulttheme/slider_cursor')

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


class ImageButton(Button):
    pass


class ImageToggle(ToggleButton):
    pass


class FrontPanel(GridLayout):

    pasttime   = StringProperty('00:00:00')
    nexttime   = StringProperty('00:00:00')

    duration   = NumericProperty(-1)
    position   = NumericProperty(0)
    volume     = NumericProperty(1.0)
    state      = OptionProperty('stop', options=('play', 'pause', 'stop'))

    controller = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self._anim = None
        super(FrontPanel, self).__init__(**kwargs)
        self.bind(position=self._on_seektime, duration=self._on_seektime)

    def show(self, duration=20):
        if self._anim is not None:
            self._anim.cancel(self)
            self._anim = None
        self._anim  = Animation(opacity=1, d=1, t='in_out_expo')
        self._anim += Animation(opacity=1, d=max(1, duration-4), t='linear')
        self._anim += Animation(opacity=0, d=max(1, duration-7), t='in_out_expo')
        self._anim.start(self)

    def hide(self):
        if self._anim is not None:
            self._anim.cancel(self)
            self._anim = None
        self.opacity = 0

    def seek(self, percent):
        if self.controller is None:
            return
        self.controller.seek(percent)

    def dispatch(self, event_type, *largs):

        if self.is_event_type(event_type):
            return super(FrontPanel, self).dispatch(event_type, *largs)

        controller = self.controller
        if controller is not None and controller.is_event_type(event_type):
            return controller.dispatch(event_type, *largs)

    def on_touch_down(self, touch):
        if self.opacity < .8:
            return True
        return super(FrontPanel, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.opacity < .8:
            return True
        return super(FrontPanel, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.opacity < .8:
            return True
        return super(FrontPanel, self).on_touch_up(touch)

    def on_controller(self, instance, value):

        controller = value
        if controller is None:
            return

        controller.bind(state=self.setter('state'),
                        duration=self.setter('duration'),
                        position=self.setter('position'),
                        volume=self.setter('volume'))

        self.bind(state=controller.setter('state'),
                  volume=controller.setter('volume'))

    def _on_seektime(self, *largs):

        if self.controller is None or self.duration == 0:
            self.pasttime = '00:00:00'
            self.nexttime = '00:00:00'
            return

        def seektime(seek):
            hours   = int(seek / 3600)
            minutes = int(seek / 60) - (hours * 60)
            seconds = int(seek) - (hours * 3600 + minutes * 60)
            return '%02d:%02d:%02d' % (hours, minutes, seconds)

        seek = self.position / float(self.duration)
        self.pasttime = seektime(self.duration * seek)
        self.nexttime = seektime(self.duration * (1. - seek))
