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

from threading import Lock
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.resources import resource_find
from kivy.graphics.texture import Texture
from kivy.uix.image import Image

import sys
sys.path.insert(0, '..')
from yuvfile import YuvFile


class YuvImage(Image):

	def __init__(self, **kwargs):
		self._buffer_lock = Lock()
		self._buffer = None
		super(Image, self).__init__(**kwargs)
		self.bind(source=self.texture_update, mipmap=self.texture_update)
		if self.source:
			self.texture_update()

		Clock.schedule_interval(self._update, 1 / 30.)

	def texture_update(self, *largs):
		if not self.source:
			self.texture = None
		else:
			filename = resource_find(self.source)
			if filename is None:
				return
			self.im = YuvFile(filename, size=(1920,1080), format='yuv')
			self._buffer = self.im.read()
			self._update(None)

	def _populate_texture(self, texture):
		texture.flip_vertical()
		texture.blit_buffer(self._buffer, size=self.im.size, colorfmt='rgb')

	def _update_texture(self, buf):
		texture = Texture.create(size=self.im.size, colorfmt='rgb')
		texture.add_reload_observer(self._populate_texture)
		self._populate_texture(texture)
		self.texture = texture

	def _update(self, dt):
		with self._buffer_lock:
			if self._buffer is not None:
				self._update_texture(self._buffer)
				self._buffer = None
				self._buffer = self.im.read()

	def reload(self):
		uid = '%s|%s|%s' % (self.source, self.mipmap, 0)
		Cache.remove("kv.texture", uid)
		olsource = self.source
		self.source = ''
		self.source = olsource


if __name__ == '__main__':
	from kivy.app import App
	import sys

	if len(sys.argv) != 2:
		print "usage: %s file" % sys.argv[0]
		sys.exit(1)

	class YuvImageApp(App):
		def build(self):
			return YuvImage(source=sys.argv[1])

	YuvImageApp().run()
