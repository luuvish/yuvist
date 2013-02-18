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

__all__ = ('PlaylistDialog', )

import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty
from kivy.adapters.dictadapter import DictAdapter
from kivy.uix.listview import ListItemButton, CompositeListItem, ListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup


Builder.load_string('''
<PlaylistLayout>:
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
''')


class PlaylistLayout(BoxLayout):

    layout    = ObjectProperty(None)
    selection = ListProperty([])

    popup     = ObjectProperty(None)
    playlist  = ListProperty([])

    def __init__(self, **kwargs):

        super(PlaylistLayout, self).__init__(**kwargs)

        integers_dict = {
            str(i): {'source': os.path.basename(self.playlist[i][0]),
                     'size': '%dx%d' % tuple(self.playlist[i][3]),
                     'format': self.playlist[i][1],
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
                 'kwargs': {'text': rec['size'],
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

    def confirm(self, selection):
        if selection and self.popup.confirm is not None:
            index = selection[0].index
            if 0 <= index < len(self.playlist):
                self.popup.confirm(self.playlist[index])
        self.popup.dismiss()

    def cancel(self):
        self.popup.dismiss()


class PlaylistDialog(Popup):

    confirm = ObjectProperty(None)

    def __init__(self, **kwargs):

        super(PlaylistDialog, self).__init__()

        playlist       = kwargs.get('playlist', [])

        self.confirm   = kwargs.get('confirm', None)

        self.title     = kwargs.get('title', 'PlayList YUV Image File')
        self.size_hint = kwargs.get('size_hint', (None, None))
        self.size      = kwargs.get('size', (700, 500))
        self.content   = PlaylistLayout(popup=self, playlist=playlist)
