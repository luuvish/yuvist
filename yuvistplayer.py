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
                             DictProperty, OptionProperty)
from kivy.animation import Animation
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.video import Image

from yuvimage import YuvImage


Builder.load_string('''
<YuvistPlayer>:
    container: container
    cols: 1

    FloatLayout:
        cols: 1
        id: container

    GridLayout:
        rows: 1
        size_hint_y: None
        height: 44

        YuvistPlayerStop:
            size_hint_x: None
            video: root
            width: 44
            source: root.image_stop

        YuvistPlayerPlayPause:
            size_hint_x: None
            video: root
            width: 44
            source: root.image_pause if root.state == 'play' else root.image_play

        YuvistPlayerVolume:
            video: root
            size_hint_x: None
            width: 44
            source: root.image_volumehigh if root.volume > 0.8 else root.image_volumemedium if root.volume > 0.4 else root.image_volumelow if root.volume > 0 else root.image_volumemuted

        Widget:
            size_hint_x: None
            width: 5

        YuvistPlayerProgressBar:
            video: root
            max: root.duration or 1
            value: root.position

        Widget:
            size_hint_x: None
            width: 10
''')


class YuvistPlayerVolume(Image):
    video = ObjectProperty(None)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        touch.grab(self)
        touch.ud[self.uid] = [self.video.volume, 0]
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        dy = abs(touch.y - touch.oy)
        if dy > 10:
            dy = min(dy - 10, 100)
            touch.ud[self.uid][1] = dy
            self.video.volume = dy / 100.
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        dy = abs(touch.y - touch.oy)
        if dy < 10:
            if self.video.volume > 0:
                self.video.volume = 0
            else:
                self.video.volume = 1.


class YuvistPlayerPlayPause(Image):
    video = ObjectProperty(None)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.video.state == 'play':
                self.video.state = 'pause'
            else:
                self.video.state = 'play'
            return True


class YuvistPlayerStop(Image):
    video = ObjectProperty(None)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.video.state = 'stop'
            self.video.position = 0
            return True


class YuvistPlayerProgressBar(ProgressBar):
    video = ObjectProperty(None)
    seek  = NumericProperty(None, allownone=True)
    alpha = NumericProperty(1.)

    def __init__(self, **kwargs):
        super(YuvistPlayerProgressBar, self).__init__(**kwargs)
        self.bubble = Factory.Bubble(size=(50,44))
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
        minutes = int(d / 60)
        seconds = int(d - (minutes * 60))
        self.label.text = '%d:%02d' % (minutes, seconds)
        self.bubble.center_x = self.x + seek * self.width
        self.bubble.y = self.top

    def _showhide_bubble(self, instance, value):
        if value == 'play':
            self._hide_bubble()
        else:
            self._show_bubble()


class YuvistPlayer(GridLayout):
    source    = StringProperty('')
    duration  = NumericProperty(-1)
    position  = NumericProperty(0)
    volume    = NumericProperty(1.0)
    state     = OptionProperty('stop', options=('play', 'pause', 'stop'))
    play      = BooleanProperty(False)

    options   = DictProperty({})
    container = ObjectProperty(None)

    THEME_DIR = 'atlas://data/images/defaulttheme/'

    image_play         = StringProperty(THEME_DIR + 'media-playback-start')
    image_stop         = StringProperty(THEME_DIR + 'media-playback-stop')
    image_pause        = StringProperty(THEME_DIR + 'media-playback-pause')
    image_volumehigh   = StringProperty(THEME_DIR + 'audio-volume-high')
    image_volumemedium = StringProperty(THEME_DIR + 'audio-volume-medium')
    image_volumelow    = StringProperty(THEME_DIR + 'audio-volume-low')
    image_volumemuted  = StringProperty(THEME_DIR + 'audio-volume-muted')

    def __init__(self, **kwargs):
        self._video = None
        super(YuvistPlayer, self).__init__(cols=1, **kwargs)

    def on_source(self, instance, value):
        if not self.container:
            return
        self.container.clear_widgets()

    def on_state(self, instance, value):
        if self._video is None:
            if self.source.lower().endswith('.yuv'):
                from yuvimage import YuvImage as CoreImage
            else:
                from kivy.uix.video import Video as CoreImage
            self._video = CoreImage(source=self.source,
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


if __name__ == '__main__':
    import sys
    from kivy.base import runTouchApp
    runTouchApp(YuvistPlayer(source=sys.argv[1]))
