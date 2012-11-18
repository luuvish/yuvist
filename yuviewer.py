#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import wx

class FileDrop(wx.FileDropTarget):

	def __init__(self, window):
		wx.FileDropTarget.__init__(self)
		self.window = window

	def OnDropFiles(self, x, y, filenames):
		for name in filenames:
			try:
				print("FileDrop = %s" % name)
				#f = open(name, 'rb')
				#f.close()
			except IOError:
				dlg = wx.MessageDialog(None, "Error opening file\n" + str(IOError))
				dlg.ShowModal()

class YuvPyPanel(wx.Panel):

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, style=wx.RAISED_BORDER)

		self.sliderFrame       = wx.Slider(self, value=0, minValue=0, maxValue=100)
		self.buttonVolume      = wx.Button(self, -1, '#', size=(30, -1))
		self.sliderVolume      = wx.Slider(self, value=0, minValue=0, maxValue=100, size=(150, -1))
		self.buttonPrev10Frame = wx.Button(self, -1, '<',    size=(30, -1))
		self.buttonPlay        = wx.Button(self, -1, 'Play', size=(40, -1))
		self.buttonStop        = wx.Button(self, -1, 'Stop', size=(40, -1))
		self.buttonNext10Frame = wx.Button(self, -1, '>',    size=(30, -1))
		self.buttonPrevImage   = wx.Button(self, -1, '{',    size=(30, -1))
		self.buttonNextImage   = wx.Button(self, -1, '}',    size=(30, -1))

		self.Bind(wx.EVT_BUTTON, parent.OnPushVolume,  self.buttonVolume)
	#	self.Bind(wx.EVT_BUTTON, parent.OnPrevFrame,   self.buttonPrevFrame)
	#	self.Bind(wx.EVT_BUTTON, parent.OnNextFrame,   self.buttonNextFrame)
		self.Bind(wx.EVT_BUTTON, parent.OnPrev10Frame, self.buttonPrev10Frame)
		self.Bind(wx.EVT_BUTTON, parent.OnNext10Frame, self.buttonNext10Frame)
	#	self.Bind(wx.EVT_BUTTON, parent.OnHeadFrame,   self.buttonHeadFrame)
	#	self.Bind(wx.EVT_BUTTON, parent.OnTailFrame,   self.buttonTailFrame)
		self.Bind(wx.EVT_BUTTON, parent.OnPrevImage,   self.buttonPrevImage)
		self.Bind(wx.EVT_BUTTON, parent.OnNextImage,   self.buttonNextImage)
		self.Bind(wx.EVT_BUTTON, parent.OnPlay,        self.buttonPlay)
		self.Bind(wx.EVT_BUTTON, parent.OnStop,        self.buttonStop)

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(self.sliderFrame, proportion=1)

		item1 = wx.BoxSizer(wx.HORIZONTAL)
		item1.Add(self.buttonVolume)
		item1.Add(self.sliderVolume)
		item2 = wx.BoxSizer(wx.HORIZONTAL)
		item2.Add(self.buttonPrev10Frame)
		item2.Add(self.buttonPlay)
		item2.Add(self.buttonStop)
		item2.Add(self.buttonNext10Frame)
		item3 = wx.BoxSizer(wx.HORIZONTAL)
		item3.Add(self.buttonPrevImage)
		item3.Add(self.buttonNextImage)

		hbox2 = wx.GridSizer(rows=1, cols=3, vgap=2, hgap=4)
		hbox2.AddMany([(item1, 0, wx.ALIGN_LEFT),
					   (item2, 0, wx.ALIGN_CENTER),
					   (item3, 0, wx.ALIGN_RIGHT)])

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hbox1, flag=wx.EXPAND|wx.BOTTOM, border=2)
		vbox.Add(hbox2, proportion=1, flag=wx.EXPAND)

		self.SetSizer(vbox)

class YuvPyFrame(wx.Frame):

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, 'Yuv Viewer', size=(400, 200))
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		self.createMenuBar()
		self.createPanel()

	def menuData(self):
		return [("&File", (("&Open...\tcmd-o", "Open yuv image file", self.OnOpen),
						   ("Open in &New Window...\tcmd-n", "Open yuv image file", self.OnOpenNewWindow),
						   ("Open &Recent", "Open yuv image file", self.OnOpenRecent),
						   ("", "", ""),
						   ("&Close\tcmd-w", "Close yuv image file", self.OnClose))),
				("&View", (("&Stop\tspace", "", self.OnStop),
						   ("", "", ""),
						   ("Prev Frame\t[", "Prev Frame", self.OnPrevFrame),
						   ("Next Frame\t]", "Prev Frame", self.OnNextFrame),
						   ("Prev 10 Frame\tleft", "Prev 10 Frame", self.OnPrev10Frame),
						   ("Next 10 Frame\tright", "Next 10 Frame", self.OnNext10Frame),
						   ("Head Frame\thome", "Head Frame", self.OnHeadFrame),
						   ("Tail Frame\tend", "Tail Frame", self.OnTailFrame),
						   ("", "", ""),
						   ("Prev Image\tctrl-cmd-left", "Prev Image", self.OnHeadFrame),
						   ("Next Image\tctrl-cmd-right", "Next Image", self.OnTailFrame))),
				("&Video", (("Half Size\tcmd-0", "Half Size", self.OnHalfSize),
							("Normal Size\tcmd-1", "Normal Size", self.OnNormalSize),
							("Double Size\tcmd-2", "Double Size", self.OnDoubleSize),
							("", "", "")))]

	def createMenuBar(self):
		menuBar = wx.MenuBar()
		for eachMenuData in self.menuData():
			menuLabel = eachMenuData[0]
			menuItems = eachMenuData[1]
			menuBar.Append(self.createMenu(menuItems), menuLabel)
		self.SetMenuBar(menuBar)

	def createMenu(self, menuData):
		menu = wx.Menu()
		for eachItem in menuData:
			if len(eachItem) == 2:
				label = eachItem[0]
				subMenu = self.createMenu(eachItem[1])
				menu.AppendMenu(wx.NewId(), label, subMenu)
			else:
				self.createMenuItem(menu, *eachItem)
		return menu

	def createMenuItem(self, menu, label, status, handler, kind=wx.ITEM_NORMAL):
		if not label:
			menu.AppendSeparator()
			return
		menuItem = menu.Append(-1, label, status, kind)
		self.Bind(wx.EVT_MENU, handler, menuItem)

	def createPanel(self):
		self.view = wx.Panel(self)
		self.view.SetBackgroundColour(wx.BLACK)
		self.control = YuvPyPanel(self)

		self.control.buttonPlay.Show(True)
		self.control.buttonStop.Show(False)

		dt = FileDrop(self.view)
		self.view.SetDropTarget(dt)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.view, proportion=1, flag=wx.EXPAND)
		sizer.Add(self.control, flag=wx.EXPAND|wx.BOTTOM|wx.TOP, border=10)

		self.SetSizer(sizer)
		self.SetMinSize((640, 480))
		self.SetSize((640, 480))

	def ReadFile(self, filename):
		if filename:
			try:
				f = open(filename, 'rb')
				f.close()
			except IOError:
				wx.MessageBox("%s is not a yuv image file." % filename,
							  "oops!", style=wx.OK|wx.ICON_EXCLAMATION)

	wildcard = "YUV image files (*.yuv)|*.yuv|All files (*.*)|*.*"

	def OnOpen(self, event):
		dlg = wx.FileDialog(self, "Open yuv image file...",
							os.getcwd(), style=wx.OPEN, wildcard=self.wildcard)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetPath()
			self.ReadFile(filename)
			self.SetTitle(' Yuv Viewer -- ' + filename)
		dlg.Destroy()

	def OnOpenNewWindow(self, event):
		dlg = wx.FileDialog(self, "Open yuv image file...",
							os.getcwd(), style=wx.OPEN, wildcard=self.wildcard)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetPath()
			self.ReadFile(filename)
			self.SetTitle(' Yuv Viewer -- ' + filename)
		dlg.Destroy()

	def OnOpenRecent(self, event): pass

	def OnClose(self, event): pass

	def OnCloseWindow(self, event):
		self.Destroy()

	def OnPushVolume(self, event): pass

	def OnPrevFrame(self, event): pass
	def OnNextFrame(self, event): pass
	def OnPrev10Frame(self, event): pass
	def OnNext10Frame(self, event): pass
	def OnHeadFrame(self, event): pass
	def OnTailFrame(self, event): pass
	def OnPrevImage(self, event): pass
	def OnNextImage(self, event): pass
	def OnPlay(self, event):
		self.control.buttonPlay.Show(False)
		self.control.buttonStop.Show(True)
		self.control.Refresh()
	def OnStop(self, event):
		self.control.buttonPlay.Show(True)
		self.control.buttonStop.Show(False)
		self.control.Refresh()

	def OnHalfSize(self, event): pass
	def OnNormalSize(self, event): pass
	def OnDoubleSize(self, event): pass
