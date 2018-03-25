import findrox; findrox.version(2, 0, 3)
import rox
from rox import choices, OptionsBox

def build_filechooser(self, node, label, option):
	"""<filechooser name='...' label='...'/>Tooltip</filechooser>.
	Lets the user choose a file (using a GtkFileChooser or by drag-and-drop).
	Note: Since the FileChooserButton widget requires GTK >= 2.6, lesser GTK
	versions will just show a normal text entry box, which should work with DND.
	"""
	if g.gtk_version >= (2,6,0):
		filebutton = g.FileChooserButton(label)
		eb = g.EventBox()
		eb.add(filebutton)
		clearbutton = g.Button("Clear")
		self.may_add_tip(eb, node)
		hbox = g.HBox(False, 4)
		if label:
			hbox.pack_start(g.Label(label + ":"), False, True, 0)
		hbox.pack_start(eb, True, True, 0)
		hbox.pack_start(clearbutton, False, True, 0)
		self.handlers[option] = (
			lambda: filebutton.get_filename(),
			lambda: filebutton.set_filename(option.value))
		filebutton.connect('selection-changed', lambda w: self.check_widget(option))
		clearbutton.connect('clicked', lambda w: filebutton.set_filename("") )
		return [hbox]
	else:
		# Fallback to text input
		return self.build_entry(node, label, option)

OptionsBox.widget_registry['filechooser'] = build_filechooser

choices.migrate('Memo', 'rox.sourceforge.net')

import os, builtins
builtins._ = rox.i18n.translation(os.path.join(rox.app_dir, 'Messages'))

rox.setup_app_options('Memo', site = 'rox.sourceforge.net')

from rox.Menu import set_save_name
set_save_name('Memo', site = 'rox.sourceforge.net')

import Window, memos, clock
try:
	# Need this for the Systray options
	import Systray
except AssertionError:
	pass

# All options must be registered by the time we get here
rox.app_options.notify()

# This is just to prevent us from loading two copies...
memo_service = 'net.sourceforge.rox.Memo'
from rox import xxmlrpc, g, tasks
try:
	proxy = xxmlrpc.XXMLProxy(memo_service)
	# Check to make sure it really is running...
	def check():
		call = proxy.get_object('/').get_pid()
		yield call, tasks.TimeoutBlocker(2)
		if call.happened:
			pid = call.get_response()
			rox.alert('Memo is already running (PID = %d)!' % pid)
			os._exit(1)
		g.main_quit()
	tasks.Task(check())
	g.main()
	print("Possible existing copy of Memo is not responding")
except xxmlrpc.NoSuchService:
	pass # Good
server = xxmlrpc.XXMLRPCServer(memo_service)
class MemoObject:
	allowed_methods = ['get_pid']
	def get_pid(self):
		return os.getpid()
server.add_object('/', MemoObject())

memo_list = memos.MasterList()

main_window = Window.Window(memo_list)

def main():
	try:
		rox.mainloop()
	finally:
		import dbus_notify
		dbus_notify.close_all()
