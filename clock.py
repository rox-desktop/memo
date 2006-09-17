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

import rox, time, sys
from rox import g, applet, Menu, options, processes
import main

menu = Menu.Menu('main', [
	("/Show Main Window", "show_main", "", ""),
	("/Set Time", "set_time", "<StockItem>", "", g.STOCK_PROPERTIES),
	("/Options", "options", "<StockItem>", "", g.STOCK_PREFERENCES),
	("/Quit",    "quit",    "<StockItem>", "", g.STOCK_QUIT)
])

clocktype = options.Option("clocktype", "2lines")
showtip = options.Option("showtip", True)
set_prog = options.Option('set_program', "gksu time-admin")

line1 = options.Option("line1", "%X")
line2 = options.Option("line2", "%x")
tip = options.Option("tip", "%c")

class Clock:
    def __init__(self):
        self.tooltip = g.Tooltips()
        if showtip.value == "False": self.tooltip.disable()
        self.vbox = g.VBox(spacing = 2)
        
        self.line1_label = g.Label("")
        self.vbox.add(self.line1_label)

        self.line2_label = g.Label("")
        if clocktype.value == "2lines":
            self.vbox.add(self.line2_label)
            
        self.set_border_width(5)
        self.add(self.vbox)

        rox.app_options.add_notify(self.options_changed)
        
        self.add_events(g.gdk.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.button_press)

        self.connect("destroy", self.destroyed)

        self.update_clock()
        self.timeout = g.timeout_add(1000, self.update_clock)

        self.show_all()

    def update_clock(self):
        self.line1_label.set_text(time.strftime(line1.value))
        self.line2_label.set_text(time.strftime(line2.value))
        self.tooltip.set_tip(self, time.strftime(tip.value))
        return True

    def destroyed(self, window):
        g.timeout_remove(self.timeout)

    def button_press(self, window, event):
        if event.button == 3:
            menu.popup(window, event)

    def options_changed(self):
        if clocktype.has_changed:
            if clocktype.value == "1line":
                self.vbox.remove(self.line2_label)
            else:
                self.vbox.add(self.line2_label)

        if showtip.has_changed:
            if showtip.value == "True":
                self.tooltip.enable()
            else:
                self.tooltip.disable()

        self.update_clock()

    def options(self):
        rox.edit_options()

    def quit(self):
        self.destroy()
	main.main_window.destroy()
    
    def set_time(self):
        rox.processes.PipeThroughCommand(set_prog.value , None, None).wait()

    def show_main(self):
	if main.main_window.get_property('visible'):
	    main.main_window.hide()
	else:
	    main.main_window.present()

class ClockApplet(applet.Applet, Clock):
    def __init__(self):
        applet.Applet.__init__(self, sys.argv[1])
        Clock.__init__(self)

    def button_press(self, window, event):
        if event.button == 1:
	    self.show_main()
        elif event.button == 3:
            menu.popup(window, event, self.position_menu)

