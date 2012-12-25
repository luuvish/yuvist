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

from kivy.lang import Builder
from kivy.properties import (ObjectProperty, OptionProperty, ListProperty)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup


Builder.load_string('''
[VSeparator@Widget]:
    size_hint_x: None
    width: 10
    canvas:
        Color:
            rgba: .8, .8, .8, .3
        Rectangle:
            size: 1, self.height
            pos: self.center_x, self.y

[HSeparator@Label]:
    size_hint_y: None
    height: max(dp(45), self.texture_size[1] + dp(10))
    text: ctx.text if 'text' in ctx else ''
    text_size: self.width, None
    valign: 'middle'
    halign: 'center'
    canvas.before:
        Color:
            rgba: .2, .2, .2, .8
        Rectangle:
            size: self.size
            pos: self.pos

<ImageSizePanel>:
    orientation: 'vertical'
    spinner: spinner

    BoxLayout:
        orientation: 'horizontal'

        RelativeLayout:
            orientation: 'vertical'
            size_hint_x: .5

            Label:
                pos_hint: {'top':1}
                size_hint_y: None
                height: 45
                text: 'Resolution'
                canvas.before:
                    Color:
                        rgba: .2, .2, .2, .8
                    Rectangle:
                        size: self.size
                        pos: self.pos

            Spinner:
                id: spinner
                pos_hint: {'center_x':.5, 'center_y':.6}
                size_hint: (.8, None)
                height: 40

            GridLayout:
                rows: 2
                cols: 2
                pos_hint: {'center_x':.5, 'center_y':.35}
                size_hint_y: None
                height: 40

                TextInput:
                    size_hint: (.3, None)
                    height: 40
                    text: str(root.resolution[0])
                    on_text: root.resolution[0] = int(self.text)
                Slider:
                    size_hint: (.7, None)
                    height: 40
                    max: 8192
                    value: root.resolution[0]
                    step: 1
                    on_value: root.resolution[0] = int(self.value)
                TextInput:
                    size_hint: (.3, None)
                    height: 40
                    text: str(root.resolution[1])
                    on_text: root.resolution[1] = int(self.text)
                Slider:
                    size_hint: (.7, None)
                    height: 40
                    max: 4320
                    value: root.resolution[1]
                    step: 1
                    on_value: root.resolution[1] = int(self.value)

        VSeparator

        RelativeLayout:
            orientation: 'vertical'
            size_hint_x: .5

            Label:
                pos_hint: {'top':1}
                size_hint_y: None
                height: 45
                text: 'Chroma Format'
                canvas.before:
                    Color:
                        rgba: .2, .2, .2, .8
                    Rectangle:
                        size: self.size
                        pos: self.pos

            GridLayout:
                pos_hint: {'center_x':.5, 'center_y':.4}
                size_hint: (.8, None)
                height: 150
                rows: 5

                ToggleButton:
                    text: '4:0:0'
                    group: 'chroma'
                    state: 'down' if root.format == 'yuv400' else 'normal'
                    on_press: root.format = 'yuv400'
                ToggleButton:
                    text: '4:2:0'
                    group: 'chroma'
                    state: 'down' if root.format == 'yuv420' else 'normal'
                    on_press: root.format = 'yuv420'
                ToggleButton:
                    text: '4:2:2'
                    group: 'chroma'
                    state: 'down' if root.format == 'yuv422' else 'normal'
                    on_press: root.format = 'yuv422'
                ToggleButton:
                    text: '4:2:2v'
                    group: 'chroma'
                    state: 'down' if root.format == 'yuv422v' else 'normal'
                    on_press: root.format = 'yuv422v'
                ToggleButton:
                    text: '4:4:4'
                    group: 'chroma'
                    state: 'down' if root.format == 'yuv444' else 'normal'
                    on_press: root.format = 'yuv444'

    Widget:
        size_hint_y: None
        height: 28

    GridLayout:
        size_hint_y: None
        height: 32
        cols: 2

        Button:
            text: 'Cancel'
            on_press: root.cancel()
        Button:
            text: 'Ok'
            on_press: root.ok(root.format, root.resolution)

<PlaylistPanel>:
    cols: 2

    BoxLayout:
        orientation: 'vertical'

    BoxLayout:
        orientation: 'vertical'

<ConfigPanel>:
    orientation: 'horizontal'
    spacing: 4
    size: (20*2 + root.spacing, 45)

    Button:
        pos_hint: {'center_y':.7}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainControlPanel.tiff'
        background_down: 'images/MainControlPanelHover.tiff'
        on_press: root._imagesize()

    Button:
        pos_hint: {'center_y':.7}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainPlaylist.tiff'
        background_down: 'images/MainPlaylistHover.tiff'
        on_press: root._playlist()
''')


class ImageSizePanel(BoxLayout):

    resolutions = (
        (( 128,   96), 'SQCIF'),
        (( 176,  144), 'QCIF'),
        (( 320,  240), 'QVGA'),
        (( 352,  240), '525 SIF'),
        (( 352,  288), 'CIF'),
        (( 352,  480), '525 HHR'),
        (( 352,  576), '625 HHR'),
        (( 640,  360), 'Q720p'),
        (( 640,  480), 'VGA'),
        (( 704,  480), '525 4SIF'),
        (( 720,  480), '525 SD'),
        (( 704,  576), '4CIF'),
        (( 720,  576), '625 SD'),
        (( 864,  480), '480p'),
        (( 800,  600), 'SVGA'),
        (( 960,  540), 'QHD'),
        ((1024,  768), 'XGA'),
        ((1280,  720), '720p HD'),
        ((1280,  960), '4VGA'),
        ((1280, 1024), 'SXGA'),
        ((1408,  960), '525 16SIF'),
        ((1408, 1152), '16CIF'),
        ((1600, 1200), '4SVGA'),
        ((1920, 1080), '1080 HD'),
        ((2048, 1024), '2Kx1K'),
        ((2048, 1080), '2Kx1080'),
        ((2560, 1920), '16VGA'),
        ((3616, 1536), '3616x1536'),
        ((3680, 1536), '3672x1536'),
        ((3840, 2160), '4HD'),
        ((4096, 2048), '4Kx2K'),
        ((4096, 2160), '4096x2160'),
        ((4096, 2304), '4096x2304'),
        ((7680, 4320), '7680x4320'),
        ((8192, 4096), '8192x4096'),
        ((8192, 4320), '8192x4320')
    )

    spinner    = ObjectProperty(None)
    input_w    = ObjectProperty(None)
    input_h    = ObjectProperty(None)
    slider_w   = ObjectProperty(None)
    slider_h   = ObjectProperty(None)

    format     = OptionProperty('yuv', options=('yuv', 'yuv400', 'yuv420',
                                                'yuv422', 'yuv422v', 'yuv444'))
    resolution = ListProperty([0, 0])
    ok         = ObjectProperty(None)
    cancel     = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ImageSizePanel, self).__init__(**kwargs)

        if self.format == 'yuv':
            self.format = 'yuv420'

        def show_selected_value(spinner, text):
            self.resolution = map(int, text.split('x'))

        self.spinner.values = ('%dx%d' % res for res, name in self.resolutions)
        self.spinner.text = '%dx%d' % tuple(self.resolution)
        self.spinner.bind(text=show_selected_value)


class PlaylistPanel(BoxLayout):
    pass


class ConfigPanel(BoxLayout):
    video = ObjectProperty(None)
    state = OptionProperty('stop', options=('play', 'pause', 'stop'))

    def __init__(self, **kwargs):
        super(ConfigPanel, self).__init__(**kwargs)

    def on_video(self, instance, value):
        self.video.bind(state=self.setter('state'))

    def _imagesize(self):
        popup = None
        def ok(format, resolution):
            print 'resolution %s, format %s' % (resolution, format)
            self.video.resolution = resolution
            self.video.format = format
            popup.dismiss()
        def cancel():
            popup.dismiss()
        popup = Popup(title='Configuration YUV image',
                      content=ImageSizePanel(resolution=self.video.resolution,
                                             format=self.video.format,
                                             ok=ok, cancel=cancel),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def _playlist(self):
        popup = None
        def submit(instance, selected, touch=None):
            self.video.source = selected[0]
            self.video.state = 'play'
            popup.dismiss()
        from kivy.uix.label import Label
        popup = Popup(title='Open Image File',
                      content=Label(text='play list'),
                      size_hint=(None, None), size=(400, 400))
        popup.open()
