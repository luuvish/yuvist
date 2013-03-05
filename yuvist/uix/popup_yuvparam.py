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

__all__ = ('YuvParamPopup', )

from kivy.lang import Builder
from kivy.properties import ObjectProperty, OptionProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from yuvist.core.video import YUV_CHROMA_FORMAT


Builder.load_string('''
#:import YUV_CHROMA_FORMAT yuvist.core.video.YUV_CHROMA_FORMAT

#:set YUV_SIZE_LIST (            \
    (( 128,   96), 'SQCIF'),     \
    (( 176,  144), 'QCIF'),      \
    (( 320,  240), 'QVGA'),      \
    (( 352,  240), '525 SIF'),   \
    (( 352,  288), 'CIF'),       \
    (( 352,  480), '525 HHR'),   \
    (( 352,  576), '625 HHR'),   \
    (( 640,  360), 'Q720p'),     \
    (( 640,  480), 'VGA'),       \
    (( 704,  480), '525 4SIF'),  \
    (( 720,  480), '525 SD'),    \
    (( 704,  576), '4CIF'),      \
    (( 720,  576), '625 SD'),    \
    (( 864,  480), '480p'),      \
    (( 800,  600), 'SVGA'),      \
    (( 960,  540), 'QHD'),       \
    ((1024,  768), 'XGA'),       \
    ((1280,  720), '720p HD'),   \
    ((1280,  960), '4VGA'),      \
    ((1280, 1024), 'SXGA'),      \
    ((1408,  960), '525 16SIF'), \
    ((1408, 1152), '16CIF'),     \
    ((1600, 1200), '4SVGA'),     \
    ((1920, 1080), '1080 HD'),   \
    ((2048, 1024), '2Kx1K'),     \
    ((2048, 1080), '2Kx1080'),   \
    ((2560, 1920), '16VGA'),     \
    ((3616, 1536), '3616x1536'), \
    ((3680, 1536), '3672x1536'), \
    ((3840, 2160), '4HD'),       \
    ((4096, 2048), '4Kx2K'),     \
    ((4096, 2160), '4096x2160'), \
    ((4096, 2304), '4096x2304'), \
    ((7680, 4320), '7680x4320'), \
    ((8192, 4096), '8192x4096'), \
    ((8192, 4320), '8192x4320')  \
)

#:set YUV_CHROMA_LIST ('4:0:0', '4:2:0', '4:2:2', '4:2:2v', '4:4:4')

#:set MIN_YUV_WIDTH  1
#:set MIN_YUV_HEIGHT 1
#:set MAX_YUV_WIDTH  8192
#:set MAX_YUV_HEIGHT 4320

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
    pos_hint: ctx.pos_hint if 'pos_hint' in ctx else None
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

<YuvSizeOption>:
    size_hint_y: None
    height: 40

<YuvSizeDropDown>:
    max_height: 200

<YuvParamLayout>:
    orientation: 'vertical'

    BoxLayout:
        orientation: 'horizontal'

        RelativeLayout:
            orientation: 'vertical'
            size_hint_x: .5

            HSeparator:
                pos_hint: {'top':1}
                text: 'Image Size'

            Spinner:
                option_cls: root.option_cls
                dropdown_cls: root.dropdown_cls
                pos_hint: {'center_x':.5, 'center_y':.6}
                size_hint: (.8, None)
                height: 40
                values: ('%dx%d' % res for res, name in YUV_SIZE_LIST)
                text: '%dx%d' % tuple(root.yuv_size)
                on_text: root.yuv_size = map(int, self.text.split('x'))

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
                    text: str(root.yuv_size[0])
                    on_text: if root._check_yuv_size(self.text, min=MIN_YUV_WIDTH, max=MAX_YUV_WIDTH): root.yuv_size[0] = int(self.text)
                Widget:
                    size_hint: (.03, None)
                    height: 40
                Slider:
                    size_hint: (.7, None)
                    height: 40
                    min: MIN_YUV_WIDTH
                    max: MAX_YUV_WIDTH
                    value: root.yuv_size[0]
                    step: 1
                    on_value: root.yuv_size[0] = int(self.value)

                TextInput:
                    size_hint: (.27, None)
                    height: 40
                    padding: (6, 12)
                    multiline: False
                    text: str(root.yuv_size[1])
                    on_text: if root._check_yuv_size(self.text, min=MIN_YUV_HEIGHT, max=MAX_YUV_HEIGHT): root.yuv_size[1] = int(self.text)
                Widget:
                    size_hint: (.03, None)
                    height: 40
                Slider:
                    size_hint: (.7, None)
                    height: 40
                    min: MIN_YUV_HEIGHT
                    max: MAX_YUV_HEIGHT
                    value: root.yuv_size[1]
                    step: 1
                    on_value: root.yuv_size[1] = int(self.value)

        VSeparator

        RelativeLayout:
            orientation: 'vertical'
            size_hint_x: .5

            HSeparator:
                pos_hint: {'top':1}
                text: 'Chroma Format'

            GridLayout:
                pos_hint: {'center_x':.5, 'center_y':.4}
                size_hint: (.8, None)
                height: 150
                rows: 5

                ToggleButton:
                    text: YUV_CHROMA_LIST[0]
                    group: 'chroma'
                    state: 'down' if root.format == YUV_CHROMA_FORMAT[0] else 'normal'
                    on_press: root.format = YUV_CHROMA_FORMAT[0]
                ToggleButton:
                    text: YUV_CHROMA_LIST[1]
                    group: 'chroma'
                    state: 'down' if root.format == YUV_CHROMA_FORMAT[1] else 'normal'
                    on_press: root.format = YUV_CHROMA_FORMAT[1]
                ToggleButton:
                    text: YUV_CHROMA_LIST[2]
                    group: 'chroma'
                    state: 'down' if root.format == YUV_CHROMA_FORMAT[2] else 'normal'
                    on_press: root.format = YUV_CHROMA_FORMAT[2]
                ToggleButton:
                    text: YUV_CHROMA_LIST[3]
                    group: 'chroma'
                    state: 'down' if root.format == YUV_CHROMA_FORMAT[3] else 'normal'
                    on_press: root.format = YUV_CHROMA_FORMAT[3]
                ToggleButton:
                    text: YUV_CHROMA_LIST[4]
                    group: 'chroma'
                    state: 'down' if root.format == YUV_CHROMA_FORMAT[4] else 'normal'
                    on_press: root.format = YUV_CHROMA_FORMAT[4]

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
            on_press: root.confirm(root.format, root.yuv_size)
''')


class YuvSizeOption(Button):
    pass


class YuvSizeDropDown(DropDown):

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


class YuvParamLayout(BoxLayout):

    option_cls   = ObjectProperty(YuvSizeOption)
    dropdown_cls = ObjectProperty(YuvSizeDropDown)

    popup    = ObjectProperty(None)
    format   = OptionProperty(YUV_CHROMA_FORMAT[1], options=YUV_CHROMA_FORMAT)
    yuv_size = ListProperty([0, 0])

    def confirm(self, format, yuv_size):
        if self.popup.confirm is not None:
            self.popup.confirm(format, yuv_size)
        self.popup.dismiss()

    def cancel(self):
        self.popup.dismiss()

    def _check_yuv_size(self, value, min=1, max=8192):
        try:
            return min <= int(value) <= max
        except ValueError:
            return False


class YuvParamPopup(Popup):

    confirm = ObjectProperty(None)

    def __init__(self, **kwargs):

        super(YuvParamPopup, self).__init__()

        format         = kwargs.get('format', YUV_CHROMA_FORMAT[1])
        yuv_size       = kwargs.get('yuv_size', [0, 0])

        self.confirm   = kwargs.get('confirm', None)

        self.title     = kwargs.get('title', 'Configuration YUV image')
        self.size_hint = kwargs.get('size_hint', (None, None))
        self.size      = kwargs.get('size', (400, 400))
        self.content   = YuvParamLayout(popup=self, format=format, yuv_size=yuv_size)
