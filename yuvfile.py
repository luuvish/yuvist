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

import os
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import (StringProperty, ObjectProperty,
                             BooleanProperty, NumericProperty, OptionProperty,
                             ListProperty, ReferenceListProperty)


YUV_FIX       = 16            # fixed-point precision
YUV_RANGE_MIN = -227          # min value of r/g/b output
YUV_RANGE_MAX = 256 + 226     # max value of r/g/b output
YUV_HALF      = 1 << (YUV_FIX - 1)
VP8kVToR      = [0] * 256
VP8kUToB      = [0] * 256
VP8kVToG      = [0] * 256
VP8kUToG      = [0] * 256
VP8kClip      = [0] * (YUV_RANGE_MAX - YUV_RANGE_MIN);

def _init():
    for i in xrange(256):
        VP8kVToR[i] = (89858 * (i - 128) + YUV_HALF) >> YUV_FIX
        VP8kUToG[i] = -22014 * (i - 128) + YUV_HALF
        VP8kVToG[i] = -45773 * (i - 128)
        VP8kUToB[i] = (113618 * (i - 128) + YUV_HALF) >> YUV_FIX

    for i in xrange(YUV_RANGE_MIN, YUV_RANGE_MAX):
        k = ((i - 16) * 76283 + YUV_HALF) >> YUV_FIX
        k = 0 if k < 0 else 255 if k > 255 else k
        VP8kClip[i - YUV_RANGE_MIN] = k

_init()


class YuvFile(EventDispatcher):

    chroma = {
        'yuv400' : (1,1),
        'yuv420' : (2,2),
        'yuv422' : (1,2),
        'yuv422v': (2,1),
        'yuv444' : (1,1)
    }

    copy_attributes = ('_size', '_filename', '_texture', '_image')

    filename = StringProperty(None)
    format   = OptionProperty('yuv420', options=('yuv400', 'yuv420',
                                                 'yuv422', 'yuv422v', 'yuv444'))
    width    = NumericProperty(0)
    height   = NumericProperty(0)
    size     = ReferenceListProperty(width, height)

    eos      = BooleanProperty(False)
    position = NumericProperty(-1)
    duration = NumericProperty(-1)
    volume   = NumericProperty(1.)
    options  = ObjectProperty({})

    image    = ObjectProperty(None)
    texture  = ListProperty([])

    def __init__(self, arg, **kwargs):
        self.register_event_type('on_texture')
        self.register_event_type('on_eos')

        from threading import Lock
        self._buffer_lock = Lock()
        self._buffer = None

        super(YuvFile, self).__init__(**kwargs)

        self.format   = kwargs.get('format', 'yuv')
        self.size     = kwargs.get('size', [0, 0])
        self.filename = arg
        return

        if isinstance(arg, YuvFile):
            for attr in YuvFile.copy_attributes:
                self.__setattr__(attr, arg.__getattribute__(attr))
        elif isinstance(arg, basestring):
            self.filename = arg
        else:
            raise Exception('Unable to load image type %s' % str(type(arg)))

    def play(self):
        Clock.unschedule(self._update_glsl)
        Clock.schedule_interval(self._update_glsl, 1 / 30.)

    def step(self, next=1):
        self.position += next

    def stop(self):
        Clock.unschedule(self._update_glsl)
        self.position = -1

    def pause(self):
        Clock.unschedule(self._update_glsl)

    def seek(self, percent):
        self.position = percent * self.duration

    def on_filename(self, instance, value):
        if value is not None:
            self._load_image()

    def on_size(self, instance, value):
        pass

    def on_eos(self, *largs):
        pass

    def on_position(self, instance, value):
        fp = self.image['file']
        if value is not None and fp is not None:
            value = int(value)
            if value < 0:
                pass
            elif 0 <= value < self.duration:
                fp.seek(value * self.image['byte'][2], os.SEEK_SET)
                y = fp.read(self.image['byte'][0])
                u = fp.read(self.image['byte'][1])
                v = fp.read(self.image['byte'][1])
                #self._buffer = self._convert_rgb((y, u, v))
                #self._update_texture_rgb(self._buffer)
                self._buffer = y, u, v
                self._update_texture(self._buffer)
                self.dispatch('on_texture')
            elif value == self.duration:
                self.eos = True
                self.dispatch('on_eos')
            else:
                raise Exception('Overflow seek position > duration')

    def on_image(self, instance, value):
        return
        if value is not None:
            if hasattr(value, 'filename'):
                self.filename = value.filename
            self.size = value.size

    def on_texture(self, *largs):
        pass

    def _update_glsl(self, dt):
        self.position += 1

    def _load_image(self, *largs):
        filename = self.filename
        size     = self.size
        format   = self.format

        try:
            fp = open(filename, 'rb')
        except IOError:
            raise Exception("Can't open file %s" % filename)
        filesize = os.path.getsize(filename)

        if format not in YuvFile.chroma:
            raise Exception("Not support chroma format")
        subpixel = YuvFile.chroma[format]
        ysize = size
        csize = size[0] // subpixel[0], size[1] // subpixel[1]
        ybyte = ysize[0] * ysize[1]
        cbyte = csize[0] * csize[1]

        self.image = {
            'file'    : fp,
            'filesize': filesize,
            'subpixel': YuvFile.chroma[format],
            'size'    : (ysize, csize),
            'byte'    : (ybyte, cbyte, ybyte + cbyte * 2)
        }
        self.duration = float(self.image['filesize'] // self.image['byte'][2])
        self.position = 0.

    def _read_image(self, *largs):
        pass

    def _update(self, dt):
        buf = None
        with self._buffer_lock:
            buf = self._buffer
            self._buffer = None
        if buf is not None:
            self._update_texture(buf)
            self.dispatch('on_texture')

    def _update_texture(self, buf):
        ysize = self.image['size'][0]
        csize = self.image['size'][1]
        texture = self.texture

        if not texture:
            def populate_texture_y(texture):
                texture.flip_vertical()
                texture.blit_buffer(self._buffer[0], size=ysize, colorfmt='luminance')
            def populate_texture_u(texture):
                texture.flip_vertical()
                texture.blit_buffer(self._buffer[1], size=csize, colorfmt='luminance')
            def populate_texture_v(texture):
                texture.flip_vertical()
                texture.blit_buffer(self._buffer[2], size=csize, colorfmt='luminance')

            from kivy.graphics.texture import Texture
            texture = [Texture.create(size=ysize, colorfmt='luminance'),
                       Texture.create(size=csize, colorfmt='luminance'),
                       Texture.create(size=csize, colorfmt='luminance')]
            texture[0].add_reload_observer(populate_texture_y)
            texture[1].add_reload_observer(populate_texture_u)
            texture[2].add_reload_observer(populate_texture_v)
            texture[0].flip_vertical()
            texture[1].flip_vertical()
            texture[2].flip_vertical()

        texture[0].blit_buffer(self._buffer[0], size=ysize, colorfmt='luminance')
        texture[1].blit_buffer(self._buffer[1], size=csize, colorfmt='luminance')
        texture[2].blit_buffer(self._buffer[2], size=csize, colorfmt='luminance')
        self.texture = texture

    def _update_texture_rgb(self, buf):
        ysize = self.image['size'][0]
        csize = self.image['size'][1]
        texture = self.texture

        if not texture:
            def populate_texture(texture):
                texture.flip_vertical()
                texture.blit_buffer(self._buffer[0], size=ysize, colorfmt='rgb')

            from kivy.graphics.texture import Texture
            texture = [Texture.create(size=ysize, colorfmt='rgb'), None, None]
            texture[0].add_reload_observer(populate_texture)
            texture[0].flip_vertical()

        texture[0].blit_buffer(self._buffer[0], size=ysize, colorfmt='rgb')
        self.texture = texture

    def _convert_rgb(self, buf):
        format   = self.format
        subpixel = self.image['subpixel']
        ysize    = self.image['size'][0]
        csize    = self.image['size'][1]

        def raster(buf):
            ybuf, ubuf, vbuf = buf
            y, u, v = 128, 128, 128
            for posy in xrange(ysize[1]):
                for posx in xrange(ysize[0]):
                    y = ybuf[ysize[0] * posy + posx]
                    if format != 'yuv400':
                        p = csize[0] * (posy // subpixel[1]) + (posx // subpixel[0])
                        u = ubuf[p]
                        v = vbuf[p]
                    yield ord(y), ord(u), ord(v)

        clip = lambda x: min(max(0, x), 255)

        def rgb(y, u, v):
            r = 1.164 * (y-16)                   + 1.596 * (v-128)
            g = 1.164 * (y-16) - 0.391 * (u-128) - 0.813 * (v-128)
            b = 1.164 * (y-16) + 2.018 * (u-128)
            return clip(int(r)), clip(int(g)), clip(int(b))

        def rgb2(y, u, v):
            r = 298 * (y-16)                 + 409 * (v-128)
            g = 298 * (y-16) - 100 * (u-128) - 208 * (v-128)
            b = 298 * (y-16) + 516 * (u-128)
            return clip((r+128)>>8), clip((g+128)>>8), clip((b+128)>>8)

        def rgb3(y, u, v):
            r_off = VP8kVToR[v]
            g_off = (VP8kVToG[v] + VP8kUToG[u]) >> YUV_FIX
            b_off = VP8kUToB[u]

            r = VP8kClip[y + r_off - YUV_RANGE_MIN]
            g = VP8kClip[y + g_off - YUV_RANGE_MIN]
            b = VP8kClip[y + b_off - YUV_RANGE_MIN]
            return r, g, b

        rgb = []
        for y, u, v in raster(buf):
            r, g, b = rgb3(y, u, v)
            rgb.append(r)
            rgb.append(g)
            rgb.append(b)
        rgb = ''.join(map(chr, rgb))
        return rgb, '', ''
