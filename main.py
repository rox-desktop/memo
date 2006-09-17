import findrox; findrox.version(2, 0, 3)
import rox
from rox import choices

choices.migrate('Memo', 'rox.sourceforge.net')

import os, __builtin__
__builtin__._ = rox.i18n.translation(os.path.join(rox.app_dir, 'Messages'))

rox.setup_app_options('Memo', site = 'rox.sourceforge.net')

from rox.Menu import set_save_name
set_save_name('Memo', site = 'rox.sourceforge.net')

import Window, memos, clock

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
		g.mainquit()
	tasks.Task(check())
	g.main()
	print "Possible existing copy of Memo is not responding"
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
