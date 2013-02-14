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

__all__ = ('YuvVideo', )

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import RenderContext
from kivy.resources import resource_find
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, \
        ObjectProperty, ListProperty, OptionProperty
from kivy.uix.video import Video

from core.image.yuv import Yuv
from core.video.video_yuv import VideoYuv


Builder.load_string('''
<YuvVideo>:
    canvas:
        Color:
            rgba: self.color
        Rectangle:
            texture: self.texture
            size: self.norm_image_size
            pos: self.center_x - self.norm_image_size[0] / 2., self.center_y - self.norm_image_size[1] / 2.
        BindTexture:
            texture: self.texture1
            index: 1
        BindTexture:
            texture: self.texture2
            index: 2
''')


class YuvVideo(Video):

    FS_CONVERT_RGB = '''$HEADER$
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

    FS_CONVERT_YUV = '''$HEADER$
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

    FS_CONVERT_MONO = '''$HEADER$
    uniform sampler2D texture1;
    uniform sampler2D texture2;

    void main(void) {
        float y;

        y = texture2D(texture0, tex_coord0).s;
        y = 1.1643 * (y - 0.0625);

        gl_FragColor = vec4(y, y, y, 1.0);
    }
    '''

    fs         = StringProperty(None)
    texture1   = ObjectProperty(None, allownone=True)
    texture2   = ObjectProperty(None, allownone=True)

    yuv_size   = ListProperty([0, 0])
    yuv_format = OptionProperty(Yuv.YUV_CHROMA_FORMAT[1], options=Yuv.YUV_CHROMA_FORMAT)
    out_format = OptionProperty(Yuv.OUT_COLOR_FORMAT[1], options=Yuv.OUT_COLOR_FORMAT)

    def __init__(self, **kwargs):
        self.canvas = RenderContext(fs=self.FS_CONVERT_YUV)
        self.canvas['texture1'] = 1
        self.canvas['texture2'] = 2

        super(YuvVideo, self).__init__(**kwargs)

        convert_fs = {
            Yuv.OUT_COLOR_FORMAT[0]: self.FS_CONVERT_RGB,
            Yuv.OUT_COLOR_FORMAT[1]: self.FS_CONVERT_YUV,
            Yuv.OUT_COLOR_FORMAT[2]: self.FS_CONVERT_MONO
        }
        self.fs = convert_fs[self.out_format]

    def on_fs(self, instance, value):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')

    def on_size(self, instance, value):
        self.canvas['projection_mat'] = Window.render_context['projection_mat']

    def on_state(self, instance, value):
        if not self._video:
            return
        if value == 'stop':
            self._video.stop()
        else:
            super(YuvVideo, self).on_state(instance, value)

    def _do_video_load(self, *largs):
        if self._video:
            self._video.stop()
        if not self.source:
            self._video   = None
            self.texture  = None
            self.texture1 = None
            self.texture2 = None
        else:
            filename = self.source
            if filename.split(':')[0] not in (
                    'http', 'https', 'file', 'udp', 'rtp', 'rtsp'):
                filename = resource_find(filename)
            self._video = VideoYuv(filename=filename,
                                   size=self.yuv_size,
                                   yuv_format=self.yuv_format,
                                   out_format=self.out_format)
            self._video.volume = self.volume
            self._video.bind(on_load=self._on_video_frame,
                             on_frame=self._on_video_frame,
                             on_eos=self._on_eos)
            if self.state == 'play' or self.play:
                self._video.play()
            self.duration = 1.
            self.position = 0.

    def _on_video_frame(self, *largs):
        self.duration = self._video.duration
        self.position = self._video.position
        self.texture  = self._video.texture[0]
        self.texture1 = self._video.texture[1]
        self.texture2 = self._video.texture[2]
        self.canvas.ask_update()
        #print('FPS: %2.4f (real draw: %d)' % (Clock.get_fps(), Clock.get_rfps()))

    def _on_eos(self, *largs):
        self.state = 'pause'
        self.eos = True


if __name__ == '__main__':
    from kivy.app import App
    import sys

    if len(sys.argv) != 2:
        print "usage: %s file" % sys.argv[0]
        sys.exit(1)

    class YuvVideoApp(App):
        def build(self):
            self.v = YuvVideo(source=sys.argv[1], state='play')
            self.v.bind(eos=self.replay)
            return self.v

        def replay(self, *args):
            if self.v.eos:
                self.v.state = 'play'

    YuvVideoApp().run()
