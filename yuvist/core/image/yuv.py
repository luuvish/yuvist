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

__all__ = ('Yuv', )

import os
from threading import Lock

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, \
        OptionProperty, ObjectProperty, ListProperty, ReferenceListProperty
from kivy.graphics.texture import Texture

from .converter import Converter


class Yuv(EventDispatcher):

    YUV_CHROMA_FORMAT = (
        'yuv400',
        'yuv420',
        'yuv422',
        'yuv422v',
        'yuv444'
    )

    YUV_CHROMA_SUBPIXEL = {
        'yuv400' : (1, 1),
        'yuv420' : (2, 2),
        'yuv422' : (1, 2),
        'yuv422v': (2, 1),
        'yuv444' : (1, 1)
    }

    OUT_COLOR_FORMAT = ('rgb', 'yuv', 'mono')

    copy_attributes = ('_size', '_filename', '_texture', '_image')

    filename = StringProperty(None)
    width    = NumericProperty(0)
    height   = NumericProperty(0)
    size     = ReferenceListProperty(width, height)
    yuv_format = OptionProperty(YUV_CHROMA_FORMAT[1], options=YUV_CHROMA_FORMAT)
    out_format = OptionProperty(OUT_COLOR_FORMAT[1], options=OUT_COLOR_FORMAT)

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

        self._buffer_lock = Lock()
        self._buffer = None

        self.converter = Converter()

        super(Yuv, self).__init__(**kwargs)

        self.size       = kwargs.get('size', [0, 0])
        self.yuv_format = kwargs.get('yuv_format', self.YUV_CHROMA_FORMAT[1])
        self.out_format = kwargs.get('out_format', self.OUT_COLOR_FORMAT[1])
        self.filename = arg

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
                if self.out_format == self.OUT_COLOR_FORMAT[1]:
                    self._buffer = y, u, v
                    self._update_texture(self._buffer)
                else:
                    self._buffer = self.converter.convert(self, (y, u, v), type='float')
                    self._update_texture_rgb(self._buffer)
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
        format   = self.yuv_format

        try:
            fp = open(filename, 'rb')
        except IOError:
            raise Exception("Can't open file %s" % filename)
        filesize = os.path.getsize(filename)

        if format not in self.YUV_CHROMA_SUBPIXEL:
            raise Exception("Not support chroma format")
        subpixel = self.YUV_CHROMA_SUBPIXEL[format]
        ysize = size
        csize = size[0] // subpixel[0], size[1] // subpixel[1]
        ybyte = ysize[0] * ysize[1]
        cbyte = csize[0] * csize[1]

        self.image = {
            'file'    : fp,
            'filesize': filesize,
            'subpixel': subpixel,
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

            texture = [Texture.create(size=ysize, colorfmt='rgb'), None, None]
            texture[0].add_reload_observer(populate_texture)
            texture[0].flip_vertical()

        texture[0].blit_buffer(self._buffer[0], size=ysize, colorfmt='rgb')
        self.texture = texture
