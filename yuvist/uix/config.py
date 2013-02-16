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
from kivy.properties import ObjectProperty
from kivy.uix.relativelayout import RelativeLayout

from .dialog_yuv_cfg import YuvCfgDialog
from .dialog_playlist import PlaylistDialog


Builder.load_string('''
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


class Config(RelativeLayout):
    video = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Config, self).__init__(**kwargs)

    def _resolution(self):
        def confirm(format, resolution):
            self.video.format = format
            self.video.resolution = resolution
            self.video.state = 'play'
        popup = YuvCfgDialog(format=self.video.format,
                             yuv_size=self.video.resolution,
                             confirm=confirm)
        popup.open()

    def _playlist(self):
        def confirm(playitem):
            self.video.source = playitem['source']
            self.video.format = playitem['format']
            self.video.resolution = playitem['resolution']
            self.video.state = 'play'
        popup = PlaylistDialog(playlist=self.video.playlist,
                               confirm=confirm)
        popup.open()
