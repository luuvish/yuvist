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

from core.image.yuv import Yuv


class VideoYuv(VideoBase):

    def __init__(self, **kwargs):
        self._do_load = False
        self._player = None

        self._size       = kwargs.get('size', [0, 0])
        self._yuv_format = kwargs.get('yuv_format', None)
        self._out_format = kwargs.get('out_format', None)

        super(VideoYuv, self).__init__(**kwargs)

    def load(self):
        self.unload()

    def unload(self):
        if self._player:
            self._player.stop()
            self._player = None
        self._state = ''
        self._do_load = False

    def play(self):
        if self._player:
            self.unload()
        self._player = Yuv(filename=self._filename,
                           size=self._size,
                           yuv_format=self._yuv_format,
                           out_format=self._out_format)
        self._player.play()
        self._state = 'playing'
        self._do_load = True

    def stop(self):
        self.unload()

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
        return self._player.get_duration()

    def _get_position(self):
        if self._player is None:
            return 0
        return self._player.position
        return self._player.get_position()

    def _get_volume(self):
        if self._player is None:
            return 0
        self._volume = self._player.volume
        #self._volume = self._player.get_volume()
        return self._volume

    def _set_volume(self, volume):
        if self._player is None:
            return
        self._player.volume = volume
        #self._player.set_volume(volume)

    def _do_eos(self):
        self.unload()
        super(VideoYuv, self)._do_eos()

    def _update(self, dt):
        if self._do_load:
            #self._player.open()
            self._do_load = False
            #return

        player = self._player
        if player is None:
            return
        #if player.is_open is False:
        #    self._do_eos()
        #    return

        frame = player.get_next_frame()
        if frame is None:
            return
        self._buffer = frame

        if player.out_format == player.OUT_COLOR_FORMAT[0]:
            ysize = player.image['size'][0]

            if self._texture is None:
                self._texture = [
                    self._create_texture(self._buffer[0], size=ysize, colorfmt='rgb'),
                    None,
                    None
                ]
                self.dispatch('on_load')

            self._texture[0].blit_buffer(self._buffer[0], size=ysize, colorfmt='rgb')
            self.dispatch('on_frame')
        elif player.out_format == player.OUT_COLOR_FORMAT[1]:
            ysize = player.image['size'][0]
            csize = player.image['size'][1]

            if self._texture is None:
                self._texture = [
                    self._create_texture(self._buffer[0], size=ysize, colorfmt='luminance'),
                    self._create_texture(self._buffer[1], size=csize, colorfmt='luminance'),
                    self._create_texture(self._buffer[2], size=csize, colorfmt='luminance')
                ]
                self.dispatch('on_load')

            self._texture[0].blit_buffer(self._buffer[0], size=ysize, colorfmt='luminance')
            self._texture[1].blit_buffer(self._buffer[1], size=csize, colorfmt='luminance')
            self._texture[2].blit_buffer(self._buffer[2], size=csize, colorfmt='luminance')
            self.dispatch('on_frame')
        elif player.out_format == player.OUT_COLOR_FORMAT[2]:
            ysize = player.image['size'][0]

            if self._texture is None:
                self._texture = [
                    self._create_texture(self._buffer[0], size=ysize, colorfmt='luminance'),
                    None,
                    None
                ]
                self.dispatch('on_load')

            self._texture[0].blit_buffer(self._buffer[0], size=ysize, colorfmt='luminance')
            self.dispatch('on_frame')

    def _create_texture(self, buffer, size, colorfmt):
        def populate_texture(texture):
            texture.flip_vertical()
            texture.blit_buffer(buffer, size=size, colorfmt=colorfmt)
        texture = Texture.create(size=size, colorfmt=colorfmt)
        texture.add_reload_observer(populate_texture)
        texture.flip_vertical()
        return texture
