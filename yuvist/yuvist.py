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


__version__ = '0.9.2'


import kivy
kivy.require('1.5.1')

from kivy.app import App

from mainscreen import MainScreen


class YuvistApp(App):

    title = 'Yuvist-' + __version__
    icon  = 'data/images/yuvist.png'

    def __init__(self, **kwargs):

        super(YuvistApp, self).__init__(**kwargs)

        self.filename = kwargs.get('filename', '')
        self.format   = kwargs.get('format', 'yuv420')
        self.yuv_size = kwargs.get('yuv_size', [1920, 1080])
        self.state    = kwargs.get('state', 'pause')

    def build(self):
        return MainScreen(source=self.filename,
                          format=self.format,
                          yuv_size=self.yuv_size,
                          state=self.state)


if __name__ == '__main__':

    print("Kivy YUV Image Viewer")
    print("Copyright (C) 2012 Luuvish <luuvish@gmail.com>")

    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else ''
    app = YuvistApp(filename=filename)
    app.run()
