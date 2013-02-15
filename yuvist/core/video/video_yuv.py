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

__all__ = ('VideoYuv', )

from kivy.core.video import VideoBase
from kivy.graphics.texture import Texture

from . import YUV_CHROMA_FORMAT, OUT_COLOR_FORMAT
from loader_yuv import LoaderYuv


class VideoYuv(VideoBase):

    def __init__(self, **kwargs):
        self._player   = None

        self._format   = kwargs.get('format', YUV_CHROMA_FORMAT[1])
        self._colorfmt = kwargs.get('colorfmt', OUT_COLOR_FORMAT[1])
        self._size     = kwargs.get('size', [0, 0])

        super(VideoYuv, self).__init__(**kwargs)

    def load(self):
        self._state = ''
        self.eos = 'pause'

    def unload(self):
        self.stop()

    def play(self):
        if self._player is None:
            self._player = LoaderYuv(filename=self.filename,
                                     format=self._format,
                                     colorfmt=self._colorfmt,
                                     size=self._size)
        self._player.play()
        self._state = 'playing'

    def stop(self):
        if self._player:
            self._player.stop()
            self._player = None
        self._state = ''

    def pause(self):
        if self._player is None:
            return
        self._player.pause()
        self._state = 'paused'

    def seek(self, percent):
        if self._player is None:
            return
        self._player.seek(percent)

    def _get_duration(self):
        if self._player is None:
            return 0
        return self._player.duration

    def _get_position(self):
        if self._player is None:
            return 0
        return self._player.position

    def _get_volume(self):
        if self._player is None:
            return 0
        self._volume = self._player.volume
        return self._volume

    def _set_volume(self, volume):
        if self._player is None:
            return
        self._player.volume = volume

    def _update(self, dt):
        player = self._player
        if player is None:
            return

        if player.eos:
            self._do_eos()
            return

        frame = player.frame
        if frame is None:
            return
        self._buffer = frame

        size = player.frame_size
        colorfmt = player.colorfmt

        if self._texture is None:

            def create_texture(index, size, colorfmt):
                def populate_texture(texture):
                    texture.flip_vertical()
                    texture.blit_buffer(self._buffer[index], size=size, colorfmt=colorfmt)
                texture = Texture.create(size=size, colorfmt=colorfmt)
                texture.add_reload_observer(populate_texture)
                texture.flip_vertical()
                return texture

            texture = [None, None, None]
            for i in xrange(len(frame)):
                if size[i] > 0:
                    texture[i] = create_texture(i, size=size[i], colorfmt=colorfmt)
            self._texture = texture
            self.dispatch('on_load')

        for i in xrange(len(frame)):
            self._texture[i].blit_buffer(self._buffer[i], size=size[i], colorfmt=colorfmt)
            self.dispatch('on_frame')
