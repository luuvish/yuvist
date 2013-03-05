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

__all__ = ('ConvertYuv', )

from yuvist.core.video import YUV_CHROMA_FORMAT, YUV_CHROMA_SUBPIXEL


class ConvertYuv(object):

    YUV_FIX       = 16            # fixed-point precision
    YUV_RANGE_MIN = -227          # min value of r/g/b output
    YUV_RANGE_MAX = 256 + 226     # max value of r/g/b output
    YUV_HALF      = 1 << (YUV_FIX - 1)
    VP8kVToR      = [0] * 256
    VP8kUToB      = [0] * 256
    VP8kVToG      = [0] * 256
    VP8kUToG      = [0] * 256
    VP8kClip      = [0] * (YUV_RANGE_MAX - YUV_RANGE_MIN)

    def __init__(self, **kwargs):

        for i in xrange(256):
            self.VP8kVToR[i] = (89858 * (i - 128) + self.YUV_HALF) >> self.YUV_FIX
            self.VP8kUToG[i] = -22014 * (i - 128) + self.YUV_HALF
            self.VP8kVToG[i] = -45773 * (i - 128)
            self.VP8kUToB[i] = (113618 * (i - 128) + self.YUV_HALF) >> self.YUV_FIX

        for i in xrange(self.YUV_RANGE_MIN, self.YUV_RANGE_MAX):
            k = ((i - 16) * 76283 + self.YUV_HALF) >> self.YUV_FIX
            k = 0 if k < 0 else 255 if k > 255 else k
            self.VP8kClip[i - self.YUV_RANGE_MIN] = k

        type   = kwargs.get('type', 'float')
        format = kwargs.get('format', YUV_CHROMA_FORMAT[1])
        ysize  = kwargs.get('size', [0, 0])

        if format not in YUV_CHROMA_SUBPIXEL:
            raise Exception("Not support chroma format")

        subpixel = YUV_CHROMA_SUBPIXEL[format]
        csize = ysize[0] // subpixel[0], ysize[1] // subpixel[1]
        if format in YUV_CHROMA_FORMAT[0]:
            csize = (0, 0)

        convert = None
        if type == 'int':
            convert = self.rgb_int
        elif type == 'table':
            convert = self.rgb_table
        else: # type == 'float':
            convert = self.rgb_float

        self._convert  = convert
        self._format   = format
        self._ysize    = ysize
        self._csize    = csize
        self._subpixel = subpixel

    def clip(self, value):
        return min(max(0, value), 255)

    def rgb_float(self, y, u, v):

        r = 1.164 * (y-16)                   + 1.596 * (v-128)
        g = 1.164 * (y-16) - 0.391 * (u-128) - 0.813 * (v-128)
        b = 1.164 * (y-16) + 2.018 * (u-128)

        return self.clip(int(r)), self.clip(int(g)), self.clip(int(b))

    def rgb_int(self, y, u, v):

        r = 298 * (y-16)                 + 409 * (v-128)
        g = 298 * (y-16) - 100 * (u-128) - 208 * (v-128)
        b = 298 * (y-16) + 516 * (u-128)

        return self.clip((r+128)>>8), self.clip((g+128)>>8), self.clip((b+128)>>8)

    def rgb_table(self, y, u, v):

        r_off = self.VP8kVToR[v]
        g_off = (self.VP8kVToG[v] + self.VP8kUToG[u]) >> self.YUV_FIX
        b_off = self.VP8kUToB[u]

        r = self.VP8kClip[y + r_off - self.YUV_RANGE_MIN]
        g = self.VP8kClip[y + g_off - self.YUV_RANGE_MIN]
        b = self.VP8kClip[y + b_off - self.YUV_RANGE_MIN]

        return r, g, b

    def raster(self, buf):

        format   = self._format
        ysize    = self._ysize
        csize    = self._csize
        subpixel = self._subpixel

        ybuf, ubuf, vbuf = buf
        y, u, v = 128, 128, 128

        for posy in xrange(ysize[1]):
            for posx in xrange(ysize[0]):
                y = ybuf[ysize[0] * posy + posx]
                if format != YUV_CHROMA_FORMAT[0]:
                    p = csize[0] * (posy // subpixel[1]) + (posx // subpixel[0])
                    u = ubuf[p]
                    v = vbuf[p]
                yield ord(y), ord(u), ord(v)

    def convert(self, buf):

        rgb = []

        for y, u, v in self.raster(buf):
            r, g, b = self._convert(y, u, v)
            rgb.append(r)
            rgb.append(g)
            rgb.append(b)

        rgb = ''.join(map(chr, rgb))
        return rgb, '', ''
