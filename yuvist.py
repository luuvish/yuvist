#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import wx
from yuvpyframe import YuvPyFrame

class YuvPyApp(wx.App):

	def OnInit(self):
		frame = YuvPyFrame(None)
		frame.Show(True)
		self.SetTopWindow(frame)
		print("Python YUV Image Viewer")
		print("Copyright (C) 2012 Luuvish <luuvish@gmail.com>")
		return True

if __name__ == '__main__':
	app = YuvPyApp()
	app.MainLoop()
