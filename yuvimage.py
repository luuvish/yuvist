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

from threading import Lock
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.resources import resource_find
from kivy.graphics import RenderContext
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.core.window import Window

import sys
sys.path.insert(0, '..')
from yuvfile import YuvFile


Builder.load_string('''
<YuvImage>:
    canvas:
        Color:
            rgb: 1, 1, 1
        BindTexture:
            texture: self.texture2
            index: 2
        BindTexture:
            texture: self.texture1
            index: 1
        Rectangle:
            texture: self.texture0
            pos: self.pos
            size: self.size
''')

class YuvImage(Widget):

    CONVERT_YUV_RGB_FS = '''$HEADER$
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
    fs = StringProperty(None)

    source = StringProperty(None)

    texture0 = ObjectProperty(None, allownone=True)
    texture1 = ObjectProperty(None, allownone=True)
    texture2 = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self._buffer_lock = Lock()
        self._buffer = None
        self.canvas = RenderContext(fs=self.CONVERT_YUV_RGB_FS)
        self.canvas['projection_mat'] = Window.render_context['projection_mat']
        self.canvas['modelview_mat']  = Window.render_context['modelview_mat']
        self.canvas['texture1'] = 1
        self.canvas['texture2'] = 2
        super(YuvImage, self).__init__(**kwargs)
        self.bind(source=self.texture_update)
        if self.source:
            self.texture_update()
        Clock.schedule_interval(self.update_glsl, 1 / 30.)

    def on_fs(self, instance, value):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')

    def texture_update(self, *largs):
        if not self.source:
            self.texture = None
        else:
            filename = resource_find(self.source)
            if filename is None:
                return

            self.im = YuvFile(filename, size=(1920,1080), format='yuv')
            self._buffer = self.im.read()
            self.update_glsl(None)

    def _populate_texture_y(self, texture):
        texture.flip_vertical()
        texture.blit_buffer(self._buffer[0], size=(self.im.size[0]/1,self.im.size[1]/1), colorfmt='luminance')
    def _populate_texture_u(self, texture):
        texture.flip_vertical()
        texture.blit_buffer(self._buffer[1], size=(self.im.size[0]/2,self.im.size[1]/2), colorfmt='luminance')
    def _populate_texture_v(self, texture):
        texture.flip_vertical()
        texture.blit_buffer(self._buffer[2], size=(self.im.size[0]/2,self.im.size[1]/2), colorfmt='luminance')

    def _update_texture(self, buf):
        y_texture = Texture.create(size=(self.im.size[0]/1,self.im.size[1]/1), colorfmt='luminance')
        u_texture = Texture.create(size=(self.im.size[0]/2,self.im.size[1]/2), colorfmt='luminance')
        v_texture = Texture.create(size=(self.im.size[0]/2,self.im.size[1]/2), colorfmt='luminance')
        y_texture.add_reload_observer(self._populate_texture_y)
        u_texture.add_reload_observer(self._populate_texture_u)
        v_texture.add_reload_observer(self._populate_texture_v)
        self._populate_texture_y(y_texture)
        self._populate_texture_u(u_texture)
        self._populate_texture_v(v_texture)
        self.texture0 = y_texture
        self.texture1 = u_texture
        self.texture2 = v_texture

    def update_glsl(self, dt):
        with self._buffer_lock:
            if self._buffer is not None:
                self._update_texture(self._buffer)
                self._buffer = None
                self._buffer = self.im.read()

                print('FPS: %2.4f (real draw: %d)' % (Clock.get_fps(), Clock.get_rfps()))


if __name__ == '__main__':
    from kivy.app import App
    import sys

    if len(sys.argv) != 2:
        print "usage: %s file" % sys.argv[0]
        sys.exit(1)

    class YuvImageApp(App):
        def build(self):
            return YuvImage(source=sys.argv[1])

    YuvImageApp().run()
