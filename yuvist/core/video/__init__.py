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

__all__ = ()


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

OUT_COLOR_FORMAT = ('rgb', 'luminance')
