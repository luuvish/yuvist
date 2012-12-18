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
from kivy.properties import (ObjectProperty, StringProperty,
                             BooleanProperty, NumericProperty,
                             DictProperty, OptionProperty,
                             ReferenceListProperty, BoundedNumericProperty, AliasProperty)
from kivy.animation import Animation
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.video import Image, Video

from yuvimage import YuvImage


Builder.load_string('''
<VolumeSlider>:
    canvas:
        Color:
            rgb: 1, 1, 1
        BorderImage:
            border: (0, 0, 0, 0)
            pos: (self.x, self.center_y - 1)
            size: (78, 5)
            source: 'images/MainVolumeSliderTrack.tiff'
        Rectangle:
            pos: (self.value_pos[0] - 7, self.center_y - 7)
            size: (14, 14)
            source: 'images/MainVolumeSliderKnob.tiff' if self.state == 'normal' else 'images/MainVolumeSliderKnobPressed.tiff'

<VolumePanel>:
    orientation: 'horizontal'
    spacing: 2
    size: (18 + 78 + root.spacing, 45)
    slider: slider

    Button:
        pos_hint: {'center_y':.7}
        size_hint: (None, None)
        size: (18, 17)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainVolumeMute.tiff' if root.muted or slider.value_normalized == 0 else 'images/MainVolume1.tiff' if slider.value_normalized < .33 else 'images/MainVolume2.tiff' if slider.value_normalized < .66 else 'images/MainVolume3.tiff'
        background_down: 'images/MainVolumeMute.tiff' if root.muted or slider.value_normalized == 0 else 'images/MainVolume1.tiff' if slider.value_normalized < .33 else 'images/MainVolume2.tiff' if slider.value_normalized < .66 else 'images/MainVolume3.tiff'
        on_press: root._press_muted()

    VolumeSlider:
        id: slider
        pos_hint: {'center_y':.7}
        size_hint: (None, None)
        size: (78, 5)

<PlayPanel>:
    orientation: 'horizontal'
    spacing: 8
    size: (45 + (20+18)*2 + root.spacing*4, 45)

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainPrevMovie.tiff'
        background_down: 'images/MainPrevMovieHover.tiff'
        on_press: root._prev_movie()

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (18, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainPrevSeek.tiff'
        background_down: 'images/MainPrevSeekHover.tiff'
        on_press: root._prev_seek()

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (45, 45)
        background_normal: 'images/MainPause.tiff' if root.state == 'play' else 'images/MainPlay.tiff'
        background_down: 'images/MainPausePressed.tiff' if root.state == 'play' else 'images/MainPlayPressed.tiff'
        on_press: root._play_pause()

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (18, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainNextSeek.tiff'
        background_down: 'images/MainNextSeekHover.tiff'
        on_press: root._next_seek()

    Button:
        pos_hint: {'center_y':.5}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainNextMovie.tiff'
        background_down: 'images/MainNextMovieHover.tiff'
        on_press: root._next_movie()

<ConfigPanel>:
    orientation: 'horizontal'
    spacing: 4
    size: (20*2 + root.spacing, 45)

    Button:
        pos_hint: {'center_y':.7}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainControlPanel.tiff'
        background_down: 'images/MainControlPanelHover.tiff'

    Button:
        pos_hint: {'center_y':.7}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainPlaylist.tiff'
        background_down: 'images/MainPlaylistHover.tiff'

<YuvPanel>:
    container: container
    cols: 1

    FloatLayout:
        cols: 1
        id: container

    GridLayout:
        cols: 1
        size_hint_y: None
        height: 58

        canvas:
            Color:
                rgb: .8, .8, .8
            Rectangle:
                size: self.size
                pos: self.pos

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: 13

            Label:
                size_hint_x: None
                width: 50
                text: '[size=10][color=555]%s[/color][/size]' % root._label_left(root.position, root.duration)
                markup: True
            YuvProgressBar:
                video: root
                max: root.duration or 1
                value: root.position
            Label:
                size_hint_x: None
                width: 50
                text: '[size=10][color=555]-%s[/color][/size]' % root._label_right(root.position, root.duration)
                markup: True

        FloatLayout:
            size_hint_y: None
            height: 45

            VolumePanel:
                x: root.x + 8
                size_hint: None, None
                video: root

            PlayPanel:
                pos_hint: {'center_x':.5}
                size_hint: None, None
                video: root

            ConfigPanel:
                right: root.right - 8
                size_hint: None, None
                video: root
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


class VolumePanel(BoxLayout):
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


class PlayPanel(BoxLayout):
    video = ObjectProperty(None)
    state = OptionProperty('stop', options=('play', 'pause', 'stop'))

    def __init__(self, **kwargs):
        super(PlayPanel, self).__init__(**kwargs)

    def on_video(self, instance, value):
        self.video.bind(state=self.setter('state'))

    def _play_pause(self):
        if   self.video.state == 'stop':
            self.video.state = 'play'
            print '_play_pause'
        elif self.video.state == 'play':
            self.video.state = 'pause'
        else:
            self.video.state = 'play'

    def _prev_movie(self):
        print 'on_prev_movie'
    def _next_movie(self):
        print 'on_next_movie'

    def _prev_seek(self):
        if self.video.duration == 0:
            return
        seek = (self.video.position - 1) / float(self.video.duration)
        self.video.seek(seek)

        d = self.video.duration * seek
        hours   = int(d / 3600)
        minutes = int(d / 60) - (hours * 60)
        seconds = int(d) - (hours * 3600 + minutes * 60)
        text = '%02d:%02d:%02d' % (hours, minutes, seconds)

    def _next_seek(self):
        if self.video.duration == 0:
            return
        seek = (self.video.position + 1) / float(self.video.duration)
        self.video.seek(seek)


class ConfigPanel(BoxLayout):
    pass


class YuvProgressBar(ProgressBar):
    video = ObjectProperty(None)
    seek  = NumericProperty(None, allownone=True)
    alpha = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(YuvProgressBar, self).__init__(**kwargs)
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


class YuvPanel(GridLayout):
    source    = StringProperty('')
    duration  = NumericProperty(-1)
    position  = NumericProperty(0)
    volume    = NumericProperty(1.0)
    state     = OptionProperty('stop', options=('play', 'pause', 'stop'))
    play      = BooleanProperty(False)

    options   = DictProperty({})
    container = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._video = None
        super(YuvPanel, self).__init__(cols=1, **kwargs)

    def on_source(self, instance, value):
        if not self.container:
            return
        self.container.clear_widgets()

    def on_state(self, instance, value):
        if self._video is None:
            self._video = YuvImage(source=self.source,
                                   state='stop',
                                   volume=self.volume,
                                   pos_hint={'x':0, 'y':0},
                                   **self.options)
            self._video.bind(texture=self._play_started,
                             state=self.setter('state'),
                             duration=self.setter('duration'),
                             position=self.setter('position'),
                             volume=self.setter('volume'))
        self._video.state = value

    def on_play(self, instance, value):
        value = 'play' if value else 'stop'
        return self.on_state(instance, value)

    def on_volume(self, instance, value):
        if not self._video:
            return
        self._video.volume = value

    def seek(self, percent):
        if not self._video:
            return
        self._video.seek(percent)

    def _play_started(self, instance, value):
        self.container.clear_widgets()
        self.container.add_widget(self._video)

    def _label_left(self, position, duration):
        if duration == 0:
            return '00:00:00'
        seek = position / float(duration)
        d = duration * seek
        hours   = int(d / 3600)
        minutes = int(d / 60) - (hours * 60)
        seconds = int(d) - (hours * 3600 + minutes * 60)
        return '%02d:%02d:%02d' % (hours, minutes, seconds)

    def _label_right(self, position, duration):
        if duration == 0:
            return '00:00:00'
        seek = position / float(duration)
        d = duration * (1. - seek)
        hours   = int(d / 3600)
        minutes = int(d / 60) - (hours * 60)
        seconds = int(d) - (hours * 3600 + minutes * 60)
        return '%02d:%02d:%02d' % (hours, minutes, seconds)


if __name__ == '__main__':
    import sys
    from kivy.base import runTouchApp
    runTouchApp(YuvPanel(source=sys.argv[1]))
