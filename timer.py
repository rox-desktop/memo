# Copyright (C) 2006, Thomas Leonard

from gi.repository import Gtk, GObject
from rox import Dialog, info, confirm
import time
import dbus_notify

edit_timer_box = None


class TimerButton(Gtk.Button):
    """An 'egg-timer' button for the main window'"""

    def __init__(self):
        Gtk.Button.__init__(self, 'T')
        self.end_time = None
        self.timeout = None
        self.set_can_focus(False)

        self.set_tooltip_text(_('Click here to set the count-down timer.'))

        self.connect('clicked', edit_timer)

    def set_timer(self, secs):
        self.end_time = time.time() + secs

        def update_timer():
            wait = self.end_time - time.time()
            if wait < 0:
                self.timeout = None
                self.alarm()
                return False
            if wait >= 60:
                text = '%dm%d' % (int(wait / 60), int(wait % 60))
            else:
                text = '%ss' % int(wait)
            self.set_label(text)
            return True
        assert self.timeout is None
        if update_timer():
            self.timeout = GObject.timeout_add(1000, update_timer)

    def alarm(self):
        self.clear_timer()
        if dbus_notify.is_available():
            dbus_notify.timer()
        else:
            info(_('Memo : Time is up!'))

    def clear_timer(self):
        self.set_label('T')
        self.end_time = None
        if self.timeout:
            GObject.source_remove(self.timeout)
            self.timeout = None


def edit_timer(timer):
    global edit_timer_box
    if edit_timer_box:
        edit_timer_box.destroy()

    if timer.end_time:
        if confirm(_('The timer is already set - clear it?'), Gtk.STOCK_CLEAR):
            timer.clear_timer()
        return

    edit_timer_box = Dialog(
        title=_('Memo Timer'), parent=timer.get_toplevel())  # FIXME:, flags=Gtk.DIALOG_NO_SEPARATOR)

    def destroyed(box):
        global edit_timer_box
        assert edit_timer_box is box
        edit_timer_box = None
    edit_timer_box.connect('destroy', destroyed)

    def response(d, resp):
        if resp == int(Gtk.ResponseType.OK):
            timer.set_timer(min.get_value() * 60 + sec.get_value())
        d.destroy()
    edit_timer_box.connect('response', response)

    vbox = Gtk.VBox(False, 0)
    vbox.set_border_width(8)
    edit_timer_box.vbox.pack_start(vbox, True, True, 0)
    vbox.pack_start(
        Gtk.Label(_('Set the count-down timer and click OK.')), True, True, 0)

    hbox = Gtk.HBox(False, 0)
    vbox.pack_start(hbox, False, True, 8)

    min = Gtk.Adjustment(0, 0, 999, 1, 1)
    spin = Gtk.SpinButton(adjustment=min)
    spin.set_digits(0)
    spin.set_activates_default(True)
    hbox.pack_start(spin, True, True, 0)
    hbox.pack_start(Gtk.Label(_('min ')), False, True, 2)

    sec = Gtk.Adjustment(0, 0, 59, 1, 1)
    spin = Gtk.SpinButton(adjustment=sec)
    spin.set_digits(0)
    spin.set_activates_default(True)
    hbox.pack_start(spin, True, True, 0)
    hbox.pack_start(Gtk.Label(_('sec')), False, True, 2)

    edit_timer_box.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
    edit_timer_box.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
    edit_timer_box.set_default_response(Gtk.ResponseType.OK)

    edit_timer_box.show_all()
