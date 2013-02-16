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

__all__ = ('OpenDialog', )

from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window


Builder.load_string('''
<OpenLayout>:
    BoxLayout:
        orientation: 'vertical'
        pos: root.pos
        size: root.size

        FileChooserListView:
            id: filechooser
            multiselect: False
            path: root.path

        BoxLayout:
            size_hint_y: None
            height: 30

            Button:
                text: 'Cancel'
                on_release: root.cancel()

            Button:
                text: 'Open'
                on_release: root.confirm(filechooser.path, filechooser.selection)
''')


class OpenLayout(FloatLayout):

    popup = ObjectProperty(None)
    path  = StringProperty('.')

    def confirm(self, path, selected):
        if len(selected) > 0 and self.popup.confirm is not None:
            self.popup.confirm(path, selected[0])
            self.path = path
        self.popup.dismiss()

    def cancel(self):
        self.popup.dismiss()


class OpenDialog(Popup):

    confirm = ObjectProperty(None)

    def __init__(self, **kwargs):

        super(OpenDialog, self).__init__()

        path           = kwargs.get('path', '.')

        self.confirm   = kwargs.get('confirm', None)

        self.title     = kwargs.get('title', 'Open Image File')
        self.size_hint = kwargs.get('size_hint', (None, None))
        self.size      = kwargs.get('size', (Window.size[0] - 160, Window.size[1] - 100))
        self.content   = OpenLayout(popup=self, path=path)
