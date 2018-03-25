import rox
from rox import g, TRUE, FALSE, app_options
from rox.Menu import Menu
from rox.options import Option
import gobject

from MenuWindow import MenuWindow
import dbus_notify
import pretty_time
import time
import timer
from Alarm import Alarm

time_format = Option('time_format', 'text')
main_sticky = Option('main_sticky', 1)
alert_early = Option('alert_early', 0)


class Window(rox.Window, MenuWindow):
    drag_start = None

    def __init__(self, memo_list):
        rox.Window.__init__(self)
        MenuWindow.__init__(self)
        self.set_wmclass('Memo', 'Memo')
        self.set_title('Memo')
        self.set_resizable(False)
        if hasattr(self, 'set_deletable'):
            self.set_deletable(False)
        # self.set_type_hint(g.gdk.WINDOW_TYPE_HINT_DIALOG)

        self.tips = g.Tooltips()

        if main_sticky.int_value:
            self.stick()

        self.memo_list = memo_list
        self.last_day = None
        self.prime_in_progress = False

        vbox = g.VBox(FALSE, 0)
        self.add(vbox)

        hbox = g.HBox(False, 0)
        vbox.pack_start(hbox, expand=False)

        self.time_label = g.Label('')
        self.time_button = g.Button()
        self.time_button.add(self.time_label)
        self.time_button.unset_flags(g.CAN_FOCUS)
        hbox.pack_start(self.time_button, expand=True)

        hbox.pack_start(timer.TimerButton(), expand=False)

        self.list = g.TreeView(memo_list.visible)
        vbox.pack_start(self.list, expand=TRUE)
        self.list.unset_flags(g.CAN_FOCUS)

        cell = g.CellRendererText()
        column = g.TreeViewColumn('Time', cell, text=0)
        cell.set_property('xalign', 1)
        self.list.append_column(column)

        cell = g.CellRendererText()
        column = g.TreeViewColumn('Message', cell, text=1)
        self.list.append_column(column)

        self.list.set_headers_visible(FALSE)

        sel = self.list.get_selection()
        sel.set_mode(g.SELECTION_NONE)

        def activate(view, path, column):
            memo = memo_list.visible.get_memo_by_path(path)
            from EditBox import EditBox
            EditBox(memo).show()

        self.add_events(g.gdk.BUTTON_PRESS_MASK)
        self.list.connect('button-press-event', self.button_press)
        self.list.connect('row-activated', activate)
        self.time_button.add_events(g.gdk.BUTTON1_MOTION_MASK)
        self.time_button.connect('button-press-event', self.button_press)
        self.time_button.connect('motion-notify-event', self.button_motion)
        self.time_button.connect('clicked', self.time_button_clicked)

        self.update()
        gobject.timeout_add(10000, self.update)  # Update clock

        self.timeout = None  # For next alarm
        self.alert_box = None
        self.show_all_box = None
        self.save_box = None
        self.prime()

        # If we had more than one window, we'd need a remove too...
        memo_list.connect("MemoListChanged", self.prime)
        app_options.add_notify(self.options_changed)

        vbox.show_all()

    def time_button_clicked(self, widget):
        ev = g.get_current_event()
        if ev.type == g.gdk.MOTION_NOTIFY and self.drag_start:
            # Fake release from motion handler
            self.begin_move_drag(
                1, self.drag_start[0], self.drag_start[1], ev.time)
            self.drag_start = None
        else:
            self.new_memo()

    def options_changed(self):
        if time_format.has_changed:
            self.update()

        if main_sticky.int_value:
            self.stick()
        else:
            self.unstick()

    def update(self):
        if time_format.value == 'text':
            text = pretty_time.rough_time(time.time())
            self.tips.set_tip(self.time_button,
                              time.strftime('%H:%M %a %Y-%m-%d'))
        else:
            # Note: importing gtk breaks strftime for am/pm
            text = time.strftime('%a %d-%b-%Y  ') + \
                pretty_time.str_time()
            self.tips.set_tip(self.time_button, None)
        self.time_label.set_text(text)

        t = time.localtime()
        year, month, day, hour, minute, second,	weekday, julian, dst = t
        if self.last_day != day:
            if self.last_day is not None:
                self.memo_list.new_day()
            self.last_day = day

        return TRUE

    def button_press(self, widget, event):
        if event.type != g.gdk.BUTTON_PRESS:
            return
        elif event.button == 2 or event.button == 3:
            self.popup_menu(event)
            return 1
        self.drag_start = list(map(int, (event.x_root, event.y_root)))
        return 0

    def button_motion(self, widget, mev):
        if self.drag_start is None:
            return
        pos = list(map(int, (mev.x_root, mev.y_root)))
        if self.time_button.drag_check_threshold(*(self.drag_start + pos)):
            self.time_button.released()
            if self.drag_start:
                # Release event was ignored (outside the button)
                self.time_button_clicked(widget)

    # Deal with any missed alarms
    # Set a timeout for the next alarm
    def prime(self, memo_list=None):
        if self.alert_box:
            return		# Don't do anything until closed

        if self.prime_in_progress:
            return		# Make this method atomic
        else:
            self.prime_in_progress = True

        missed, delay = self.memo_list.catch_up(alert_early.int_value)
        if missed:
            if dbus_notify.is_available():
                for m in missed:
                    dbus_notify.notify(m)
            else:
                # Show the first one.
                self.alert_box = Alarm(missed[0])

                def destroyed(widget):
                    self.alert_box = None
                    self.prime()
                self.alert_box.connect('destroy', destroyed)
                g.gdk.beep()
                g.gdk.flush()
                time.sleep(0.3)
                g.gdk.beep()
                g.gdk.flush()
                time.sleep(1)
                self.alert_box.show()
        if delay:
            self.schedule(delay)
        self.prime_in_progress = False

    def timeout_cb(self):
        gobject.source_remove(self.timeout)
        self.timeout = 0
        self.prime()
        return 0

    def schedule(self, delay):
        if self.timeout:
            gobject.source_remove(self.timeout)

        # Avoid overflows - don't resched more than a day ahead
        if delay > 60 * 60 * 24:
            delay = 60 * 60 * 24

        self.timeout = gobject.timeout_add(int(1000 * delay), self.timeout_cb)
