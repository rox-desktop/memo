from gi.repository import Gtk
import findrox
findrox.version(2, 0, 3)
import rox
from rox import OptionsBox


def build_filechooser(self, node, label, option):
    """<filechooser name='...' label='...'/>Tooltip</filechooser>.
    Lets the user choose a file (using a GtkFileChooser or by drag-and-drop).
    Note: Since the FileChooserButton widget requires GTK >= 2.6, lesser GTK
    versions will just show a normal text entry box, which should work with DND.
    """
    filebutton = Gtk.FileChooserButton(label)
    eb = Gtk.EventBox()
    eb.add(filebutton)
    clearbutton = Gtk.Button("Clear")
    self.may_add_tip(eb, node)
    hbox = Gtk.HBox(False, 4)
    if label:
        hbox.pack_start(Gtk.Label(label + ":"), False, True, 0)
    hbox.pack_start(eb, True, True, 0)
    hbox.pack_start(clearbutton, False, True, 0)
    self.handlers[option] = (
        lambda: filebutton.get_filename(),
        lambda: filebutton.set_filename(option.value))
    filebutton.connect('selection-changed',
                       lambda w: self.check_widget(option))
    clearbutton.connect('clicked', lambda w: filebutton.set_filename(""))
    return [hbox]


OptionsBox.widget_registry['filechooser'] = build_filechooser

import os
import builtins
builtins._ = rox.i18n.translation(os.path.join(rox.app_dir, 'Messages'))

rox.setup_app_options('Memo', site='rox.sourceforge.net')

from rox.Menu import set_save_name
set_save_name('Memo', site='rox.sourceforge.net')

import Window
import memos
import clock
try:
    # Need this for the Systray options
    import Systray
except AssertionError:
    pass

# All options must be registered by the time we get here
rox.app_options.notify()

# FIXME: This does not work reliably, it raises BadAtom sometimes.
# This is just to prevent us from loading two copies...
#memo_service = 'net.sourceforge.rox.Memo'
#from rox import xxmlrpc, tasks
#try:
#    proxy = xxmlrpc.XXMLProxy(memo_service)
#    # Check to make sure it really is running...
#
#    def check():
#        call = proxy.get_object('/').get_pid()
#        yield call, tasks.TimeoutBlocker(2)
#        if call.happened:
#            pid = call.get_response()
#            rox.alert('Memo is already running (PID = %d)!' % pid)
#            os._exit(1)
#        Gtk.main_quit()
#    tasks.Task(check())
#    Gtk.main()
#    print("Possible existing copy of Memo is not responding")
#except xxmlrpc.NoSuchService:
#    pass  # Good
#server = xxmlrpc.XXMLRPCServer(memo_service)
#
#
#class MemoObject:
#    allowed_methods = ['get_pid']
#
#    def get_pid(self):
#        return os.getpid()
#
#
#server.add_object('/', MemoObject())

memo_list = memos.MasterList()

main_window = Window.Window(memo_list)


def main():
    try:
        rox.mainloop()
    finally:
        import dbus_notify
        dbus_notify.close_all()
