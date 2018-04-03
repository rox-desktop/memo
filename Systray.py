from gi.repository import Gtk
import rox
from rox import options, app_options
from MenuWindow import MenuWindow
import main

import os.path

systrayEnable = options.Option('systray_enable', True)
systrayHideOnStartup = options.Option('systray_hide_on_startup', False)
systrayWorkaround = options.Option('systray_workaround', False)

# Require gtk version 2.10.x or better for the 'StatusIcon' widget
#assert(Gtk.gtk_version >= (2, 10, 0))

menuAdditions = {
    'topActions': [
        ("/Main Window", "toggle_main", "", ""),
    ]
}

mainAdditions = {'topMain': [
    (_('Hide Main Window'), "hide", "")
]}


class Systray(Gtk.StatusIcon, MenuWindow):
    def __init__(self, showOnStartup=None):
        Gtk.StatusIcon.__init__(self)
        MenuWindow.__init__(self, attach=False, additions=menuAdditions)
        icon = os.path.join(rox.app_dir, '.DirIcon')
        self.set_from_file(icon)
        self.firstChange = True
        self.showOnStartup = showOnStartup
        self.was_embedded = None
        main.memo_list.connect("MemoListChanged", self.tooltip_refresh)
        self.tooltip_refresh(main.memo_list)
        self.connect("popup-menu", self.popup)
        self.connect("activate", self.toggle_main)
        self.connect("notify::visible", self.visibility)
        self.connect("notify::embedded", self.check_embed)

    def tooltip_refresh(self, memo_list):
        (all, hidden) = memo_list.count_today()
        visible = all-hidden
        vplural = "s"
        if visible == 1:
            vplural = ""
        self.set_tooltip_text("Memo - %d reminder%s today" % (visible, vplural))

    def position_menu(self, menu, x, y, *args):
        return Gtk.StatusIcon.position_menu(menu, x, y, self)

    def popup(self, status_icon, button, activate_time):
        # Rox's 'menu' class doesn't actually need a 'gtk.gdk.Event', just an object
        # with 'button' and 'time' parameters - Which is good, since gtk.gdk.Event
        # won't accept a 'long' value, which is what both 'button' and
        # 'activate_time' are (plus activate_time is usually too large to properly
        # cast into a signed python 'int' type
        class e:
            pass
        event = e()
        event.button = button
        event.time = activate_time
        self.popup_menu(event, self.position_menu)

    def size_change(self, icon=None, size=None):
        self.check_embed()

    def is_present(self):
        return self.is_embedded and self.get_visible()

    def visibility(self, object=None, property=None):
        if self.get_visible():
            self._embedded()
        else:
            self._unembedded()

    def _embedded(self):
        # Systray present, allow main window to hide
        main.main_window.addAdditions(mainAdditions)

    def _unembedded(self):
        # Systray no longer present, show the main window, and disallow hiding
        main.main_window.removeAdditions(mainAdditions)
        if not main.main_window.get_property('visible'):
            main.main_window.present()

    def check_embed(self, object=None, property=None):
        if self.is_embedded() and (not self.was_embedded or self.firstChange):
            self._embedded()
            # Check for "hide on startup" flag
            if self.showOnStartup is not None:
                if not self.showOnStartup:
                    main.main_window.hide()
                else:
                    if not main.main_window.get_property('visible'):
                        main.main_window.present()
            self.was_embedded = True
        elif not self.is_embedded() and (self.was_embedded or self.firstChange):
            self._unembedded()
            self.was_embedded = False
        self.firstChange = False
        return True

    def toggle_main(self, event=None):
        if main.main_window.get_property('visible'):
            main.main_window.hide()
        else:
            main.main_window.present()

    def quit(self, event=None):
        main.main_window.destroy()


class HideableSystray(object):
    def __init__(self):
        if systrayEnable.int_value:
            self.icon = Systray(
                showOnStartup=not systrayHideOnStartup.int_value)
        else:
            self.icon = None
            main.main_window.present()
        app_options.add_notify(self.options_changed)

    def options_changed(self):
        if systrayEnable.has_changed:
            if systrayEnable.int_value:
                self.show()
            else:
                self.hide()
        if systrayWorkaround.has_changed:
            if systrayEnable.int_value and systrayWorkaround.int_value:
                self.hide()
                self.show()

    def show(self):
        if not self.icon:
            self.icon = Systray()
        else:
            self.icon.set_visible(True)

    def hide(self):
        if self.icon:
            self.icon.set_visible(False)
            # Workaround for broken systrays (like older fluxbox versions) which
            # may not support set_visible(True) - Delete the systray icon (which
            # will be re-created at 'show' time.
            if systrayWorkaround.int_value:
                del self.icon
                self.icon = None

    def is_embedded(self):
        if self.icon:
            return self.icon.is_embedded()
        return False

    def get_visible(self):
        if self.icon:
            return self.icon.get_visible()
        return False

    def is_present(self):
        if self.icon:
            return self.icon.is_present()
        return False
