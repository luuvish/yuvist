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
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.properties import BooleanProperty, NumericProperty, OptionProperty
from kivy.uix.image import Image

import sys
sys.path.insert(0, '..')
from yuvfile import YuvFile


Builder.load_string('''
<YuvImage>:
    canvas:
        Color:
            rgb: (1, 1, 1)
        Rectangle:
            texture: self.texture
            size: self.size
            pos: self.pos
        BindTexture:
            texture: self.texture1
            index: 1
        BindTexture:
            texture: self.texture2
            index: 2
''')

class YuvImage(Image):

    FS_CONVERT_YUV420_RGB = '''$HEADER$
    uniform sampler2D texture1;
    uniform sampler2D texture2;

    void main(void) {
        float r, g, b, y, u, v;

        y = texture2D(texture0, tex_coord0).s;
        u = texture2D(texture1, tex_coord0).s;
        v = texture2D(texture2, tex_coord0).s;

        y = 1.1643 * (y - 0.0625);
        u = u - 0.5;
        v = v - 0.5;

        r = y + 1.5958  * v;
        g = y - 0.39173 * u - 0.81290 * v;
        b = y + 2.017   * u;

        gl_FragColor = vec4(r, g, b, 1.0);
    }
    '''
    FS_BYPASS_RGB = '''$HEADER$
    uniform sampler2D texture1;
    uniform sampler2D texture2;

    void main(void) {
        float r, g, b;

        r = texture2D(texture0, tex_coord0).r;
        g = texture2D(texture0, tex_coord0).g;
        b = texture2D(texture0, tex_coord0).b;

        gl_FragColor = vec4(r, g, b, 1.0);
    }
    '''
    fs = StringProperty(None)

    texture1 = ObjectProperty(None, allownone=True)
    texture2 = ObjectProperty(None, allownone=True)

    state    = OptionProperty('stop', options=('play', 'pause', 'stop'))
    play     = BooleanProperty(False)
    eos      = BooleanProperty(False)
    position = NumericProperty(-1)
    duration = NumericProperty(-1)
    volume   = NumericProperty(1.)
    options  = ObjectProperty({})

    def __init__(self, **kwargs):
        self._coreimage = None

        from kivy.core.window import Window
        from kivy.graphics import RenderContext
        self.canvas = RenderContext(fs=self.FS_CONVERT_YUV420_RGB)
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['texture1'] = 1
        self.canvas['texture2'] = 2

        super(Image, self).__init__(**kwargs)
        self.bind(source=self._trigger_image_load)

        if self.source:
            self._trigger_image_load()

    def seek(self, percent):
        if self._coreimage is None:
            raise Exception('YuvImage not loaded.')
        self._coreimage.seek(percent)

    def on_texture(self, instance, value):
        if value is not None:
            self.texture_size = list(value.size)

    def on_fs(self, instance, value):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')

    def on_play(self, instance, value):
        value = 'play' if value else 'stop'
        return self.on_state(instance, value)

    def on_state(self, instance, value):
        if not self._coreimage:
            return
        if value == 'play':
            if self.eos:
                self._coreimage.stop()
                self._coreimage.position = 0.
                self._coreimage.eos = False
            self.eos = False
            self._coreimage.play()
        elif value == 'pause':
            self._coreimage.pause()
        else:
            self._coreimage.stop()
            self._coreimage.position = 0.
            self._coreimage.eos = False

    def on_volume(self, instance, value):
        if self._coreimage:
            self._coreimage.volume = value
            pass

    def _trigger_image_load(self, *largs):
        Clock.unschedule(self._image_load)
        Clock.schedule_once(self._image_load, -1)

    def _image_load(self, *largs):
        if self._coreimage:
            self._coreimage.stop()
        if not self.source:
            if self._coreimage is not None:
                self._coreimage.unbind(on_texture=self._on_tex_change)
            self._coreimage = None
            self.texture  = None
            self.texture1 = None
            self.texture2 = None
        else:
            from kivy.resources import resource_find
            filename = resource_find(self.source)
            if filename is None:
                return
            if self._coreimage is not None:
                self._coreimage.unbind(on_texture=self._on_tex_change)
            self._coreimage = ci = YuvFile(filename, size=(1920, 1080), format='yuv')
            self._coreimage.volume = self.volume
            ci.bind(on_texture=self._on_tex_change, on_eos=self._on_eos)
            if self.state == 'play' or self.play:
                self._coreimage.play()
            self.duration = 1.
            self.position = 0.

    def _on_tex_change(self, *largs):
        self.duration = self._coreimage.duration
        self.position = self._coreimage.position
        self.texture  = self._coreimage.texture[0]
        self.texture1 = self._coreimage.texture[1]
        self.texture2 = self._coreimage.texture[2]
        self.canvas.ask_update()
        print('FPS: %2.4f (real draw: %d)' % (Clock.get_fps(), Clock.get_rfps()))

    def _on_eos(self, *largs):
        self.state = 'stop'
        self.eos = True


if __name__ == '__main__':
    from kivy.app import App
    import sys

    if len(sys.argv) != 2:
        print "usage: %s file" % sys.argv[0]
        sys.exit(1)

    class YuvImageApp(App):
        def build(self):
            self.yuv = YuvImage(source=sys.argv[1], state='play')
            self.yuv.bind(state=self.replay)
            return self.yuv

        def replay(self, *largs):
            if self.yuv.state == 'stop':
                self.yuv.state = 'play'

    YuvImageApp().run()
