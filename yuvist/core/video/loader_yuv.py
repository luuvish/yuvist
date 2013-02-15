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

__all__ = ('LoaderYuv', )

import os
from threading import Lock

from kivy.clock import Clock
from kivy.event import EventDispatcher

from . import YUV_CHROMA_FORMAT, YUV_CHROMA_SUBPIXEL, OUT_COLOR_FORMAT
from .convert_yuv import ConvertYuv


class LoaderYuv(EventDispatcher):

    def __init__(self, **kwargs):
        self._buffer_lock = Lock()
        self._buffer = None
        self._file = None

        super(LoaderYuv, self).__init__()

        self._format   = kwargs.get('format', YUV_CHROMA_FORMAT[1])
        self._colorfmt = kwargs.get('colorfmt', OUT_COLOR_FORMAT[1])
        self._size     = kwargs.get('size', [0, 0])
        self._fps      = kwargs.get('fps', 30.)

        self._filename = kwargs.get('filename', None)
        self._position = 0.
        self._duration = 0.
        self._volume   = 1.
        self._eos      = False
        self._state    = ''

        if self._filename is not None:
            self._init_image()

    @property
    def width(self):
        return self._size[0]

    @property
    def height(self):
        return self._size[1]

    @property
    def size(self):
        return self._size[0], self._size[1]

    @property
    def format(self):
        return self._format

    @property
    def colorfmt(self):
        return self._colorfmt

    def _get_fps(self):
        return self._fps

    def _set_fps(self, fps):
        if fps == self._fps:
            return
        self._fps = fps

    fps = property(lambda self: self._get_fps(),
            lambda self, x: self._set_fps(x),
            doc='Get/set the frames per second')

    def _get_filename(self):
        return self._filename

    filename = property(lambda self: self._get_filename(),
            doc='Get the filename/uri of current yuv')

    def _get_position(self):
        return self._position

    def _set_position(self, position):
        if position == self._position:
            return

        if position < 0:
            self._position = 0
            self._eos = False
        elif position >= self._duration:
            self._position = self._duration
            self._eos = True
            self.pause()
        else:
            self._position = position
            self._eos = False
            self._read_image(int(position * self._fps))

    position = property(lambda self: self._get_position(),
            lambda self, x: self._set_position(x),
            doc='Get/set the position in the yuv (in seconds)')

    def _get_duration(self):
        return self._duration

    duration = property(lambda self: self._get_duration(),
            doc='Get the yuv duration (in seconds)')

    def _get_volume(self):
        return self._volume

    def _set_volume(self, volume):
        if volume == self._volume:
            return
        self._volume = volume

    volume = property(lambda self: self._get_volume(),
            lambda self, x: self._set_volume(x),
            doc='Get/set the volume in the yuv (1.0 = 100%)')

    def _get_state(self):
        return self._state

    state = property(lambda self: self._get_state(),
            doc='Get the yuv playing status')

    @property
    def eos(self):
        return self._eos

    @property
    def frame(self):
        buf = None
        with self._buffer_lock:
            buf = self._buffer
            self._buffer = None
        return buf

    @property
    def frame_size(self):
        if self._file is None:
            return self._size, self._size, self._size
        return self._ysize, self._csize, self._csize

    def play(self):
        Clock.unschedule(self._progress)
        Clock.schedule_interval(self._progress, 1 / float(self._fps))
        self._state = 'playing'

    def stop(self):
        Clock.unschedule(self._progress)
        self.position = 0
        self._state = ''

    def pause(self):
        Clock.unschedule(self._progress)
        self._state = 'paused'

    def seek(self, percent):
        self.position = percent * self.duration

    def _progress(self, dt):
        self.position += 1 / float(self.fps)

    def _init_image(self, *largs):
        format   = self._format
        colorfmt = self._colorfmt
        ysize    = self._size
        filename = self._filename

        try:
            fp = open(filename, 'rb')
        except IOError:
            raise Exception("Can't open file %s" % filename)
        filesize = os.path.getsize(filename)

        if format not in YUV_CHROMA_SUBPIXEL:
            raise Exception("Not support chroma format")
        if colorfmt not in OUT_COLOR_FORMAT:
            raise Exception("Not support color format")

        subpixel = YUV_CHROMA_SUBPIXEL[format]
        csize = ysize[0] // subpixel[0], ysize[1] // subpixel[1]
        if format in YUV_CHROMA_FORMAT[0]:
            csize = (0, 0)

        self._ysize = ysize
        self._csize = csize
        self._file  = fp
        self._ydata = ysize[0] * ysize[1]
        self._cdata = csize[0] * csize[1]
        self._pdata = self._ydata + self._cdata * 2

        self._duration = (filesize // self._pdata) / float(self._fps)
        self._position = 0.

        self._convert = ConvertYuv(format=format, size=ysize, type='float')

    def _close_image(self):
        if self._file is None:
            return
        self._file.close()
        self._file = None

    def _read_image(self, nframe):
        if self._file is None:
            return

        self._file.seek(nframe * self._pdata, os.SEEK_SET)

        y, u, v = None, None, None
        if self._ydata > 0:
            y = self._file.read(self._ydata)
        if self._cdata > 0:
            u = self._file.read(self._cdata)
            v = self._file.read(self._cdata)

        if self.colorfmt == OUT_COLOR_FORMAT[0]:
            y, u, v = self._convert.convert((y, u, v))

        with self._buffer_lock:
            if self._buffer is None:
                self._buffer = y, u, v
