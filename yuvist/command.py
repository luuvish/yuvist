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

__all__ = ('Command', )

from argparse import ArgumentParser

import yuvist
from yuvist.core.video import YUV_CHROMA_FORMAT, OUT_COLOR_FORMAT


class Command(object):

    def parse(self, args):

        parser = ArgumentParser(prog='yuvist.py',
                description='Yuvist Kivy YUV image viewer',
                epilog='Copyright (C) 2013 Luuvish <luuvish@gmail.com>')

        parser.add_argument('-1', help='half screen size',
                dest='size_hint', action='store_const', const=(.5, .5))
        parser.add_argument('-2', help='normal screen size',
                dest='size_hint', action='store_const', const=(1., 1.))
        parser.add_argument('-3', help='double screen size',
                dest='size_hint', action='store_const', const=(2., 2.))
        parser.add_argument('-4', help='fit to window size',
                dest='size_hint', action='store_const', const=(.0, .0))
        parser.add_argument('-f', '--fullscreen', help='fullscreen mode',
                dest='fullscreen', action='store_true')

        parser.add_argument('-v', '--volume', help='volume of audio',
                dest='volume', action='store', metavar='VALUE',
                default=100, type=int, choices=xrange(0, 101))
        parser.add_argument('-s', '--state', help='state after starting',
                dest='state', action='store', metavar='STATE',
                default='play', choices=['play', 'pause', 'stop'])

        parser.add_argument('--format', help='YUV image chroma format',
                dest='format', action='store',
                default=YUV_CHROMA_FORMAT[1], choices=YUV_CHROMA_FORMAT)
        parser.add_argument('--colorfmt', help='output color format',
                dest='colorfmt', action='store',
                default=OUT_COLOR_FORMAT[1], choices=OUT_COLOR_FORMAT)
        parser.add_argument('--fps', help='display frames per second',
                dest='yuv_fps', action='store', metavar='VALUE',
                default=30., type=float)
        parser.add_argument('--size', help='YUV image width and height',
                dest='yuv_size', action='store', metavar=('WIDTH', 'HEIGHT'),
                default=[1920, 1080], type=int, nargs=2)

        parser.add_argument('-l', '--playlist', help='filename of playlist',
                dest='playlist', action='store', metavar='FILENAME')

        parser.add_argument('playitem', help='YUV image filename',
                action='store', metavar='FILENAME',
                nargs='*')

        self.size_hint = (None, None)
        parser.parse_args(args=args, namespace=self)
        self.volume /= 100.

        return vars(self)


if __name__ == '__main__':

    import sys
    cmd = Command()
    print 'Command', cmd.parse(sys.argv[1:])
