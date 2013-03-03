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


__version__ = '0.10.0'


import sys
yuvist_args = sys.argv[1:]
sys.argv = sys.argv[:1]

import kivy
kivy.require('1.5.1')

from kivy.app import App

from command import Command
from mainscreen import MainScreen


class YuvistApp(App):

    title   = 'Yuvist-' + __version__
    icon    = 'data/images/yuvist.png'
    command = []

    def __init__(self, **kwargs):
        super(YuvistApp, self).__init__(**kwargs)
        self.command = kwargs.get('command', [])

    def build(self):
        return MainScreen()

    def on_start(self):

        command = Command().parse(self.command)

        controller = self.root.controller

        size_hint = command.get('size_hint', (None, None))
        fullscreen = command.get('fullscreen', False)
        if fullscreen:
            controller.dispatch('on_fullscreen')
        elif size_hint != (None, None):
            controller.dispatch('on_customsize', yuv_size, size_hint)

        format   = command.get('format',   controller.format)
        colorfmt = command.get('colorfmt', controller.colorfmt)
        yuv_size = command.get('yuv_size', controller.yuv_size)
        yuv_fps  = command.get('yuv_fps',  controller.yuv_fps)

        playitem = command.get('playitem', [])

        for filename in playitem:
            playitem = [filename, format, colorfmt, yuv_size, yuv_fps]
            controller.playlist.append(playitem)

        controller.volume = command.get('volume', controller.volume)
        if len(controller.playlist) > 0:
            controller.playitem = controller.playlist[0]
            controller.state = command.get('state',  controller.state)
        else:
            controller.playitem = ['', format, colorfmt, yuv_size, yuv_fps]


if __name__ == '__main__':

    app = YuvistApp(command=yuvist_args)
    app.run()
