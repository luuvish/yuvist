#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kivy
kivy.require('1.4.1')

import sys, os
from kivy.app import App
from yuvistplayer import YuvistPlayer

class Yuvist(App):

	def build(self):
		if len(sys.argv) > 1:
			filename = sys.argv[1]
		else:
			filename = os.path.join(os.path.dirname(__file__), 'persona4.mp4')
		print("Kivy YUV Image Viewer")
		print("Copyright (C) 2012 Luuvish <luuvish@gmail.com>")
		return YuvistPlayer(source=filename, state='play')

if __name__ == '__main__':
	Yuvist().run()
