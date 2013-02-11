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

__all__ = ('Config', )

from kivy.lang import Builder
from kivy.properties import ObjectProperty, OptionProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown


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

<ResolutionOption>:
    size_hint_y: None
    height: 40

<ResolutionDropDown>:
    max_height: 200

<Resolution>:
    orientation: 'vertical'

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
                option_cls: root.option_cls
                dropdown_cls: root.dropdown_cls
                pos_hint: {'center_x':.5, 'center_y':.6}
                size_hint: (.8, None)
                height: 40
                values: ('%dx%d' % res for res, name in root.RESOLUTION_LIST)
                text: '%dx%d' % tuple(root.resolution)
                on_text: root.resolution = map(int, self.text.split('x'))

            GridLayout:
                rows: 2
                cols: 3
                pos_hint: {'center_x':.5, 'center_y':.35}
                size_hint_y: None
                height: 40

                TextInput:
                    size_hint: (.27, None)
                    height: 40
                    padding: (6, 12)
                    multiline: False
                    text: str(root.resolution[0])
                    on_text: if root._check_resolution_range(self.text, min=1, max=8192): root.resolution[0] = int(self.text)
                Widget:
                    size_hint: (.03, None)
                    height: 40
                Slider:
                    size_hint: (.7, None)
                    height: 40
                    min: 1
                    max: 8192
                    value: root.resolution[0]
                    step: 1
                    on_value: root.resolution[0] = int(self.value)
                TextInput:
                    size_hint: (.27, None)
                    height: 40
                    padding: (6, 12)
                    multiline: False
                    text: str(root.resolution[1])
                    on_text: if root._check_resolution_range(self.text, min=1, max=4320): root.resolution[1] = int(self.text)
                Widget:
                    size_hint: (.03, None)
                    height: 40
                Slider:
                    size_hint: (.7, None)
                    height: 40
                    min: 1
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
                    state: 'down' if root.format in ('yuv', 'yuv420') else 'normal'
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
            text: 'Confirm'
            on_press: root.confirm(root.format, root.resolution)

<Playlist>:
    orientation: 'vertical'
    layout: layout

    GridLayout:
        id: layout
        cols: 3

    GridLayout:
        size_hint_y: None
        height: 32
        cols: 2

        Button:
            text: 'Cancel'
            on_press: root.cancel()
        Button:
            text: 'Confirm'
            on_press: root.confirm(root.selection)

<Config>:
    size: 46, 51

    Button:
        pos: 0, 28
        size_hint: None, None
        size: 20, 18
        border: 0, 0, 0, 0
        background_normal: 'data/images/MainControlPanel.tiff'
        background_down: 'data/images/MainControlPanelHover.tiff'
        on_press: root._resolution()

    Button:
        pos: 24, 28
        size_hint: None, None
        size: 20, 18
        border: 0, 0, 0, 0
        background_normal: 'data/images/MainPlaylist.tiff'
        background_down: 'data/images/MainPlaylistHover.tiff'
        on_press: root._playlist()
''')


class ResolutionOption(Button):
    pass


class ResolutionDropDown(DropDown):

    def _reposition(self, *largs):
        # calculate the coordinate of the attached widget in the window
        # coordinate sysem
        win = self._win
        widget = self.attach_to
        if not widget or not win:
            return
        wx, wy = widget.to_window(*widget.pos)
        wright, wtop = widget.to_window(widget.right, widget.top)

        # set width and x
        if self.auto_width:
            self.width = wright - wx

        # ensure the dropdown list doesn't get out on the X axis, with a
        # preference to 0 in case the list is too wide.
        x = wx
        if x + self.width > win.width:
            x = win.width - self.width
        if x < 0:
            x = 0
        self.x = x

        # determine if we display the dropdown upper or lower to the widget
        h_bottom = wy - self.height
        h_top = win.height - (wtop + self.height)
        if h_bottom > 0:
            self.top = wy
        elif h_top > 0:
            self.y = wtop
        else:
            # none of both top/bottom have enough place to display the widget at
            # the current size. Take the best side, and fit to it.
            height = max(h_bottom, h_top)
            if height == h_bottom:
                self.top = wy
                self.height = wy
            else:
                self.y = wtop
                self.height = win.height - wtop


class Resolution(BoxLayout):

    RESOLUTION_LIST = (
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

    option_cls   = ObjectProperty(ResolutionOption)
    dropdown_cls = ObjectProperty(ResolutionDropDown)

    format     = OptionProperty('yuv420', options=('yuv400', 'yuv420',
                                                   'yuv422', 'yuv422v', 'yuv444'))
    resolution = ListProperty([0, 0])
    confirm    = ObjectProperty(None)
    cancel     = ObjectProperty(None)

    def _check_resolution_range(self, value, min=1, max=8192):
        try:
            return min <= int(value) <= max
        except ValueError:
            return False


class Playlist(BoxLayout):
    playlist  = ListProperty([])
    confirm   = ObjectProperty(None)
    cancel    = ObjectProperty(None)
    layout    = ObjectProperty(None)
    selection = ListProperty([])

    def __init__(self, **kwargs):
        super(Playlist, self).__init__(**kwargs)

        from kivy.adapters.dictadapter import DictAdapter
        from kivy.uix.listview import ListItemButton, CompositeListItem, ListView
        import os
        integers_dict = {
            str(i): {'source': os.path.basename(self.playlist[i]['source']),
                     'format': self.playlist[i]['format'],
                     'resolution': '%dx%d' % tuple(self.playlist[i]['resolution']),
                     'playlist': self.playlist[i],
                     'is_selected': False} for i in xrange(len(self.playlist))
        }
        args_converter = lambda row_index, rec: {
            'text': rec['source'],
            'size_hint_y': None,
            'height': 25,
            'cls_dicts': [
                {'cls': ListItemButton,
                 'kwargs': {'text': rec['source']}},
                {'cls': ListItemButton,
                 'kwargs': {'text': rec['resolution'],
                            'size_hint_x': None, 'width': 100}},
                {'cls': ListItemButton,
                 'kwargs': {'text': rec['format'],
                            'size_hint_x': None, 'width': 70}}
            ]
        }
        item_strings = ["{0}".format(index) for index in xrange(len(self.playlist))]
        dict_adapter = DictAdapter(sorted_keys=item_strings,
                                   data=integers_dict,
                                   args_converter=args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=False,
                                   cls=CompositeListItem)
        dict_adapter.bind(selection=self.setter('selection'))
        list_view = ListView(adapter=dict_adapter)
        self.layout.add_widget(list_view)


class Config(RelativeLayout):
    video = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Config, self).__init__(**kwargs)

    def _resolution(self):
        popup = None
        def confirm(format, resolution):
            self.video.format = format
            self.video.resolution = resolution
            self.video.state = 'play'
            popup.dismiss()
        def cancel():
            popup.dismiss()
        popup = Popup(title='Configuration YUV image',
                      content=Resolution(resolution=self.video.resolution,
                                         format=self.video.format,
                                         confirm=confirm, cancel=cancel),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def _playlist(self):
        popup = None
        def confirm(selection):
            if selection:
                index = selection[0].index
                playlist = self.video.playlist
                if 0 <= index < len(playlist):
                    self.video.source = playlist[index]['source']
                    self.video.format = playlist[index]['format']
                    self.video.resolution = playlist[index]['resolution']
                    self.video.state = 'play'
            popup.dismiss()
        def cancel():
            popup.dismiss()
        popup = Popup(title='PlayList YUV Image File',
                      content=Playlist(playlist=self.video.playlist,
                                       confirm=confirm, cancel=cancel),
                      size_hint=(None, None), size=(700, 500))
        popup.open()
