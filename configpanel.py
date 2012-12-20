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
from kivy.uix.boxlayout import BoxLayout


Builder.load_string('''
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

    Button:
        pos_hint: {'center_y':.7}
        size_hint: (None, None)
        size: (20, 18)
        border: (0, 0, 0, 0)
        background_normal: 'images/MainPlaylist.tiff'
        background_down: 'images/MainPlaylistHover.tiff'
''')


class ConfigPanel(BoxLayout):
    pass
