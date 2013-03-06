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
from kivy.resources import resource_find
from kivy.graphics import RenderContext
from kivy.properties import NumericProperty, StringProperty, ListProperty, \
        ObjectProperty, OptionProperty
from kivy.uix.video import Video

from yuvist.core.video import YUV_CHROMA_FORMAT, OUT_COLOR_FORMAT
from yuvist.core.video.video_yuv import VideoYuv


Builder.load_string('''
<YuvVideo>:
    allow_stretch: True

    canvas:
        Color:
            rgba: self.color
        BindTexture:
            texture: self.textures[2]
            index: 3
        BindTexture:
            texture: self.textures[1]
            index: 2
        BindTexture:
            texture: self.textures[0]
            index: 1
        Rectangle:
            size: self.norm_image_size
            pos: self.center_x - self.norm_image_size[0] / 2., self.center_y - self.norm_image_size[1] / 2.
''')


class YuvVideo(Video):

    FS_CONVERT_RGB = '''$HEADER$
    uniform sampler2D tex_y;
    uniform sampler2D tex_u;
    uniform sampler2D tex_v;

    void main(void) {
        float r, g, b;

        r = texture2D(tex_y, tex_coord0).r;
        g = texture2D(tex_y, tex_coord0).g;
        b = texture2D(tex_y, tex_coord0).b;

        gl_FragColor = vec4(r, g, b, 1.0);
    }
    '''

    FS_CONVERT_YUV = '''$HEADER$
    uniform sampler2D tex_y;
    uniform sampler2D tex_u;
    uniform sampler2D tex_v;

    void main(void) {
        float r, g, b, y, u, v;

        y = texture2D(tex_y, tex_coord0).s;
        u = texture2D(tex_u, tex_coord0).s;
        v = texture2D(tex_v, tex_coord0).s;

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
    uniform sampler2D tex_y;
    uniform sampler2D tex_u;
    uniform sampler2D tex_v;

    void main(void) {
        float y;

        y = texture2D(tex_y, tex_coord0).s;
        y = 1.1643 * (y - 0.0625);

        gl_FragColor = vec4(y, y, y, 1.0);
    }
    '''

    fs       = StringProperty(None)
    textures = ListProperty([None, None, None])

    format   = OptionProperty(YUV_CHROMA_FORMAT[1], options=YUV_CHROMA_FORMAT)
    colorfmt = OptionProperty(OUT_COLOR_FORMAT[1], options=OUT_COLOR_FORMAT)
    yuv_size = ListProperty([0, 0])
    yuv_fps  = NumericProperty(30.)

    def __init__(self, **kwargs):

        self.register_event_type('on_load')

        self.canvas = RenderContext(fs=self.FS_CONVERT_YUV)
        self.canvas['tex_y'] = 1
        self.canvas['tex_u'] = 2
        self.canvas['tex_v'] = 3

        super(YuvVideo, self).__init__(**kwargs)

        if self.colorfmt == OUT_COLOR_FORMAT[0]:
            self.fs = self.FS_CONVERT_RGB
        elif self.format != YUV_CHROMA_FORMAT[0]:
            self.fs = self.FS_CONVERT_YUV
        else:
            self.fs = self.FS_CONVERT_MONO

    def seek(self, percent):
        if self.eos == True:
            self.eos = False
        super(YuvVideo, self).seek(percent)

    def on_load(self, *largs):
        pass

    def on_fs(self, instance, value):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')

    def on_size(self, instance, value):
        window = self.get_parent_window()
        if window:
            self.canvas['projection_mat'] = window.render_context['projection_mat']

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
            self.textures = [None, None, None]
            self.texture  = None
        else:
            filename = self.source
            if filename.split(':')[0] not in (
                    'http', 'https', 'file', 'udp', 'rtp', 'rtsp'):
                filename = resource_find(filename)
            self._video = VideoYuv(filename=filename,
                                   format=self.format,
                                   colorfmt=self.colorfmt,
                                   size=self.yuv_size,
                                   fps=self.yuv_fps)
            self._video.volume = self.volume
            self._video.bind(on_load=self._on_video_load,
                             on_frame=self._on_video_frame,
                             on_eos=self._on_eos)
            if self.state == 'play' or self.play:
                self._video.play()
            self.duration = 1.
            self.position = 0.

    def _on_video_load(self, *largs):
        self._on_video_frame()
        self.dispatch('on_load')

    def _on_video_frame(self, *largs):
        self.duration = self._video.duration
        self.position = self._video.position
        self.textures = self._video.texture
        self.texture  = self._video.texture[0]
        self.canvas.ask_update()

    def _on_eos(self, *largs):
        self.duration = self._video.duration
        self.position = self._video.position
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
