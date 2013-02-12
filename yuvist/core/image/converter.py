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

__all__ = ('Converter', )


class Converter(object):

    YUV_FIX       = 16            # fixed-point precision
    YUV_RANGE_MIN = -227          # min value of r/g/b output
    YUV_RANGE_MAX = 256 + 226     # max value of r/g/b output
    YUV_HALF      = 1 << (YUV_FIX - 1)
    VP8kVToR      = [0] * 256
    VP8kUToB      = [0] * 256
    VP8kVToG      = [0] * 256
    VP8kUToG      = [0] * 256
    VP8kClip      = [0] * (YUV_RANGE_MAX - YUV_RANGE_MIN)

    def __init__(self):

        for i in xrange(256):
            self.VP8kVToR[i] = (89858 * (i - 128) + self.YUV_HALF) >> self.YUV_FIX
            self.VP8kUToG[i] = -22014 * (i - 128) + self.YUV_HALF
            self.VP8kVToG[i] = -45773 * (i - 128)
            self.VP8kUToB[i] = (113618 * (i - 128) + self.YUV_HALF) >> self.YUV_FIX

        for i in xrange(self.YUV_RANGE_MIN, self.YUV_RANGE_MAX):
            k = ((i - 16) * 76283 + self.YUV_HALF) >> self.YUV_FIX
            k = 0 if k < 0 else 255 if k > 255 else k
            self.VP8kClip[i - self.YUV_RANGE_MIN] = k

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

    def raster(self, yuv, buf):

        format   = yuv.format
        subpixel = yuv.image['subpixel']
        ysize    = yuv.image['size'][0]
        csize    = yuv.image['size'][1]

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

    def convert(self, yuv, buf, type='float'):

        converter = None
        if type == 'int':
            converter = self.rgb_int
        elif type == 'table':
            converter = self.rgb_table
        else: # type == 'float':
            converter = self.rgb_float

        rgb = []

        for y, u, v in self.raster(yuv, buf):
            r, g, b = converter(y, u, v)
            rgb.append(r)
            rgb.append(g)
            rgb.append(b)

        rgb = ''.join(map(chr, rgb))
        return rgb, '', ''
