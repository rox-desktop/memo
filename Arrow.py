from gi.repository import Gtk, Gdk, GObject

refleak_bug_workaround = []


class Arrow(Gtk.EventBox):
    def __init__(self, arrow_type, callback, data, time=50):
        Gtk.EventBox.__init__(self)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        self.data = data
        self.callback = callback
        self.arrow_type = arrow_type
        self.time = time

        self.arrow = Gtk.Arrow(arrow_type, Gtk.ShadowType.OUT)

        self.add(self.arrow)
        self.button = 0

        self.connect('button-press-event', self.button_press)
        self.connect('button-release-event', self.button_release)

        self.connect('enter-notify-event',
                     lambda w, e: self.set_state(Gtk.StateType.PRELIGHT))
        self.connect('leave-notify-event',
                     lambda w, e: self.set_state(Gtk.StateType.NORMAL))

        self.connect('destroy', lambda w: refleak_bug_workaround.remove(self))
        refleak_bug_workaround.append(self)

    def button_press(self, box, event):
        if self.button != 0 or event.type != Gdk.EventType.BUTTON_PRESS:
            return
        self.button = event.button
        # Gtk.grab_add(self)
        self.arrow.set(self.arrow_type, Gtk.ShadowType.IN)
        self.cb = GObject.timeout_add(self.time * 2 + 300, self.incr)
        self.incr(resched=0)

    def button_release(self, box, event):
        if self.button != event.button:
            return
        self.button = 0
        # Gtk.grab_remove(self)
        self.arrow.set(self.arrow_type, Gtk.ShadowType.OUT)
        GObject.source_remove(self.cb)

    def incr(self, resched=1):
        if resched:
            GObject.source_remove(self.cb)
            self.cb = GObject.timeout_add(self.time, self.incr)
        self.callback(self.data)
        return 0
