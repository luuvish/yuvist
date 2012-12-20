#!/usr/bin/env python
# -*- coding: utf-8 -*-

import kivy
kivy.require('1.5.1')

import sys, os
from kivy.app import App
from mainpanel import MainPanel

class Yuvist(App):

	def build(self):
		filename = sys.argv[1] if len(sys.argv) > 1 else ''
		print("Kivy YUV Image Viewer")
		print("Copyright (C) 2012 Luuvish <luuvish@gmail.com>")
		return MainPanel(source=filename, state='pause')

if __name__ == '__main__':
	Yuvist().run()
