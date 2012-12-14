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

import sys, os

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


class YuvFile(object):

    chroma = {
        'yuv'   : (2,2),
        'yuv400': (1,1),
        'yuv420': (2,2),
        'yuv422': (1,2),
        'yuv224': (2,1),
        'yuv444': (1,1)
    }

    def __init__(self, filename, size, format='yuv'):
        try:
            self.file = open(filename, 'rb')
        except IOError:
            raise Exception("Can't open file %s" % filename)
        self.size   = size
        self.format = format

        self.oneframe = self.size[0] * self.size[1] * 3 / 2

        self.filesize = os.path.getsize(filename)
        self.duration = self.filesize // self.oneframe
        self.position = 0

        if format not in YuvFile.chroma:
            raise Exception("Not support chroma format")
        self.scale = YuvFile.chroma[format]

    def close(self):
        if self.file:
            self.file.close()

    def read(self, position=None):
        if position:
            self.seek(position)
        if self.position >= self.duration:
            self.seek(0)

        y = self.file.read(self.size[0] * self.size[1])
        u = self.file.read(self.size[0] * self.size[1] / 4)
        v = self.file.read(self.size[0] * self.size[1] / 4)
        self.position += 1
        return y, u, v

        buf = self.file.read(self.oneframe)
        buf = self.YUVtoRGB(buf)
        buf = ''.join(map(chr, buf))
        return buf

    def seek(self, position):
        if position < self.duration:
            self.position = position
            self.file.seek(position * self.oneframe, os.SEEK_SET)

    def YUVtoRGB(self, yuvs):
        def raster(yuvs):
            format = self.format
            size   = self.size
            scale  = self.scale
            ubase  = size[0] * size[1]
            vbase  = ubase + (size[0] // scale[0]) * (size[1] // scale[1])
            cwidth = size[0] // scale[0]
            y, u, v = 128, 128, 128
            for posy in xrange(size[1]):
                for posx in xrange(size[0]):
                    y = yuvs[size[0] * posy + posx]
                    if format != 'yuv400':
                        u = yuvs[ubase + cwidth * (posy // scale[1]) + (posx // scale[0])]
                        v = yuvs[vbase + cwidth * (posy // scale[1]) + (posx // scale[0])]
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

        rgbs = []
        for y, u, v in raster(yuvs):
            r, g, b = rgb3(y, u, v)
            rgbs.append(r)
            rgbs.append(g)
            rgbs.append(b)
        return rgbs
