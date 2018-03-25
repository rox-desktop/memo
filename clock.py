# Based on code in MiniClock v. 2.0.0 - a very very simple clock
# Copyright (C) 2005  Edoardo Spadolini <pedonzolo@email.it>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import rox
import time
import sys
import os
from rox import g, applet, Menu, options, processes, filer
from MenuWindow import MenuWindow
import main
import gobject
import pango

menuAdditions = {
    'topActions': [
        ("/Main Window", "toggle_main", "", ""),
    ],
    'bottomActions': [
        ('/', "", "<Separator>"),
        (_('/Set Time'), "set_time", "<StockItem>", "", g.STOCK_PROPERTIES),
    ]}

set_prog = options.Option('set_program', "gksu time-admin")

line1 = options.Option("line1", "%X")
line2 = options.Option("line2", "%x")
tip = options.Option("tip", "%c")

line1_font = options.Option("line1_font", None)
line1_color = options.Option("line1_color", "#000000")

line2_font = options.Option("line2_font", None)
line2_color = options.Option("line2_color", "#000000")


class Clock:
    def __init__(self):
        self.tooltip = g.Tooltips()
        if tip.value == "":
            self.tooltip.disable()
        self.vbox = g.VBox(spacing=2)

        self.line1_label = g.Label("")
        if line1.value != "":
            self.vbox.add(self.line1_label)

        self.line2_label = g.Label("")
        if line2.value != "":
            self.vbox.add(self.line2_label)

        self.set_border_width(5)
        self.add(self.vbox)

        rox.app_options.add_notify(self.options_changed)

        self.add_events(g.gdk.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.button_press)

        self.connect("destroy", self.destroyed)

        self.update_clock()
        self.timeout = gobject.timeout_add(1000, self.update_clock)

        self.show_all()

    def update_clock(self):
        self.line1_label.set_text(time.strftime(line1.value))
        self.line2_label.set_text(time.strftime(line2.value))
        self.update_font()
        self.update_color()
        self.tooltip.set_tip(self, time.strftime(tip.value))
        return True

    def update_font(self):
        new_font1 = pango.FontDescription(line1_font.value)
        new_font2 = pango.FontDescription(line2_font.value)
        if new_font1:
            self.line1_label.modify_font(new_font1)
        if new_font2:
            self.line2_label.modify_font(new_font2)

    def update_color(self):
        new_color1 = g.gdk.color_parse(line1_color.value)
        new_color2 = g.gdk.color_parse(line2_color.value)
        if new_color1:
            self.line1_label.modify_fg(g.STATE_NORMAL, new_color1)
        if new_color2:
            self.line2_label.modify_fg(g.STATE_NORMAL, new_color2)

    def destroyed(self, window):
        gobject.source_remove(self.timeout)
        main.main_window.destroy()

    def button_press(self, window, event):
        if event.button == 3:
            self.popup_menu(event)

    def options_changed(self):
        if line1.has_changed:
            if line1.value == '':
                self.vbox.remove(self.line1_label)
            else:
                self.vbox.add(self.line1_label)
                if line2.value:
                    self.vbox.remove(self.line2_label)
                    self.vbox.add(self.line2_label)

        if line2.has_changed:
            if line2.value == '':
                self.vbox.remove(self.line2_label)
            else:
                self.vbox.add(self.line2_label)

        if tip.has_changed:
            if tip.value == '':
                self.tooltip.disable()
            else:
                self.tooltip.enable()

        if line1_font.has_changed or line2_font.has_changed:
            self.update_font()
        if line1_color.has_changed or line2_color.has_changed:
            self.update_color()

        self.update_clock()

    def set_time(self):
        rox.processes.PipeThroughCommand(set_prog.value, None, None).wait()

    def toggle_main(self):
        if main.main_window.get_property('visible'):
            main.main_window.hide()
        else:
            main.main_window.set_decorated(False)  # should be done only once?
            self.position_window(main.main_window)
            main.main_window.present()


class ClockApplet(applet.Applet, Clock, MenuWindow):
    def __init__(self):
        applet.Applet.__init__(self, sys.argv[1])
        Clock.__init__(self)
        MenuWindow.__init__(self, attach=False, additions=menuAdditions)
        main.main_window.memo_list.connect(
            "MemoListChanged", self.memo_list_changed)

    def button_press(self, window, event):
        if event.type != g.gdk.BUTTON_PRESS:
            return
        if event.button == 1:
            self.toggle_main()
        elif event.button == 3:
            self.popup_menu(event, self.position_menu)

    def get_panel_orientation(self):
        """Return the panel orientation ('Top', 'Bottom', 'Left', 'Right')
        and the margin for displaying a popup menu"""
        pos = self.socket.property_get('_ROX_PANEL_MENU_POS', 'STRING', False)
        if pos:
            pos = pos[2]
        if pos:
            side, margin = pos.split(',')
            margin = int(margin)
        else:
            side, margin = None, 2
        return side, margin

    def memo_list_changed(self, memo_list=None):
        def reposition():
            if main.main_window.get_property('visible'):
                self.position_window(main.main_window)
        # Give the window a chance to resize itself first...
        gobject.idle_add(reposition)

    def position_window(self, win):
        """Set the position of the popup"""
        side, margin = self.get_panel_orientation()
        x, y = self.socket.get_origin()
        w, h = win.size_request()

        # widget (x, y, w, h, bits)
        geometry = self.socket.get_geometry()

        if side == 'Bottom':
            win.move(x, y-h)
        elif side == 'Top':
            win.move(x, y+geometry[3])
        elif side == 'Left':
            win.move(x+geometry[2], y)
        elif side == 'Right':
            win.move(x-w, y)
        else:
            # shouldn't happen?
            self.thing.move(x, y)
