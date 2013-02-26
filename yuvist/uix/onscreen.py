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

__all__ = ('OnScreen', 'OnScreenTransition', 'OnScreenManager', )

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout


class OnScreen(EventDispatcher):

    manager             = ObjectProperty(None, allownone=True)
    transition_progress = NumericProperty(0.)

    def __init__(self, **kwargs):
        self.register_event_type('on_pre_enter')
        self.register_event_type('on_enter')
        self.register_event_type('on_pre_leave')
        self.register_event_type('on_leave')
        super(OnScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        pass

    def on_enter(self, *args):
        pass

    def on_pre_leave(self, *args):
        pass

    def on_leave(self, *args):
        pass


class OnScreenTransition(EventDispatcher):

    screen    = ObjectProperty()
    duration  = NumericProperty(.7)
    manager   = ObjectProperty()
    is_active = BooleanProperty(False)
    _anim     = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        self.register_event_type('on_progress')
        self.register_event_type('on_complete')
        super(OnScreenTransition, self).__init__(**kwargs)

    def start(self, manager):
        if self.is_active:
            return
        self.manager = manager
        self._anim = Animation(d=self.duration, s=0)
        self._anim.bind(on_progress=self._on_progress,
                        on_complete=self._on_complete)

        self.add_screen(self.screen)
        self.screen.transition_progress = 0.
        self.screen.dispatch('on_pre_enter')

        self.is_active = True
        self._anim.start(self)
        self.dispatch('on_progress', 0)

    def stop(self):
        if self._anim is not None:
            self._anim.cancel(self)
            self.dispatch('on_complete')
            self._anim = None
        self.is_active = False

    def add_screen(self, screen):
        self.manager.add_widget(screen)

    def remove_screen(self, screen):
        self.manager.remove_widget(screen)

    def on_progress(self, progression):
        pass

    def on_complete(self):
        self.remove_screen(self.screen)

    def _on_progress(self, *l):
        progress = l[-1]
        self.screen.transition_progress = progress
        self.dispatch('on_progress', progress)

    def _on_complete(self, *l):
        self.is_active = False
        self.dispatch('on_complete')
        self.screen.dispatch('on_enter')
        self._anim = None


class OnScreenManager(RelativeLayout):

    transition = ObjectProperty(OnScreenTransition())
    screen     = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(OnScreenManager, self).__init__(**kwargs)
        #self.bind(pos=self._update_pos)

    def start(self):
        if self.screen is None:
            return
        self.transition.stop()
        self.transition.screen = self.screen
        self.transition.start(self)

    def add_widget(self, screen):
        screen.manager = self
        if screen.parent:
            screen.parent.remove_widget(screen)
        super(OnScreenManager, self).add_widget(screen)

    def remove_widget(self, screen):
        screen.manager = None
        super(OnScreenManager, self).remove_widget(screen)

    def on_touch_down(self, touch):
        if self.transition.is_active:
            return False
        return super(OnScreenManager, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.transition.is_active:
            return False
        return super(OnScreenManager, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.transition.is_active:
            return False
        return super(OnScreenManager, self).on_touch_up(touch)

    def _update_pos(self, instance, value):
        for child in self.children:
            if self.transition.is_active and child == self.transition.screen:
                continue
            child.pos = value
