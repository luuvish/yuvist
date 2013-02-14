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

    image    = ObjectProperty(None)

    def __init__(self, **kwargs):
        self._buffer_lock = Lock()
        self._next_frame = None

        self.converter = Converter()

        super(Yuv, self).__init__(**kwargs)

        self.size       = kwargs.get('size', [0, 0])
        self.yuv_format = kwargs.get('yuv_format', self.YUV_CHROMA_FORMAT[1])
        self.out_format = kwargs.get('out_format', self.OUT_COLOR_FORMAT[1])
        self.filename   = kwargs.get('filename', None)

        if self.filename is not None:
            self._load_image()

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

    def on_position(self, instance, value):
        fp = self.image['file']
        if value is not None and fp is not None:
            value = int(value)
            if value < 0:
                pass
            elif 0 <= value < self.duration:
                self._read_image(value)
            elif value == self.duration:
                self.eos = True
                self.dispatch('on_eos')
            else:
                raise Exception('Overflow seek position > duration')

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

    def _read_image(self, value):
        fp = self.image['file']
        fp.seek(value * self.image['byte'][2], os.SEEK_SET)

        frame = None
        if self.out_format == self.OUT_COLOR_FORMAT[0]:
            y = fp.read(self.image['byte'][0])
            u = fp.read(self.image['byte'][1])
            v = fp.read(self.image['byte'][1])
            frame = self.converter.convert(self, frame, type='float')
        elif self.out_format == self.OUT_COLOR_FORMAT[1]:
            y = fp.read(self.image['byte'][0])
            u = fp.read(self.image['byte'][1])
            v = fp.read(self.image['byte'][1])
            frame = y, u, v
        elif self.out_format == self.OUT_COLOR_FORMAT[2]:
            y = fp.read(self.image['byte'][0])
            frame = y, None, None

        with self._buffer_lock:
            if self._next_frame is None:
                self._next_frame = frame

    def get_next_frame(self):
        buf = None
        with self._buffer_lock:
            buf = self._next_frame
            self._next_frame = None
        return buf
