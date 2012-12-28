#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kivy
kivy.require('1.5.1')

from kivy.config import Config
Config.set('kivy', 'window_icon', 'images/yuvist.png')

from kivy.app import App
from mainpanel import MainPanel


class Yuvist(App):

	def __init__(self, **kwargs):
		super(Yuvist, self).__init__(**kwargs)

		self.filename   = kwargs.get('filename', '')
		self.format     = kwargs.get('format', 'yuv420')
		self.resolution = kwargs.get('resolution', [1920, 1080])
		self.state      = kwargs.get('state', 'pause')

	def build(self):
		return MainPanel(source=self.filename,
						 format=self.format,
						 resolution=self.resolution,
						 state=self.state)


if __name__ == '__main__':

	print("Kivy YUV Image Viewer")
	print("Copyright (C) 2012 Luuvish <luuvish@gmail.com>")

	import sys
	filename = sys.argv[1] if len(sys.argv) > 1 else ''
	app = Yuvist(filename=filename)
	app.run()
