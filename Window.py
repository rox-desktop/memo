import rox
from rox import g, TRUE, FALSE, app_options
from rox.Menu import Menu
from rox.options import Option
import gobject

import dbus_notify
import pretty_time, time
from Alarm import Alarm

time_format = Option('time_format', 'text')
main_sticky = Option('main_sticky', 1)

menu = Menu('main', [
                (_('/Add Memo...'), 'new_memo',    ''),
                (_('/Show All...'), 'show_all_memos', ''),
		('/',		 '',		'<Separator>'),
                (_('/Options...'),  'show_options',''),
                (_('/Help'),        'help',	''),
                (_('/Quit'),        'destroy',     ''),
                ])

class Window(g.Window):
	def __init__(self, memo_list):
		g.Window.__init__(self)
		self.set_wmclass('Memo', 'Memo')
		self.set_title('Memo')
		self.set_resizable(FALSE)
		#self.set_type_hint(g.gdk.WINDOW_TYPE_HINT_DIALOG)

		if main_sticky.int_value:
			self.stick()

		self.memo_list = memo_list
		self.last_day = None

		vbox = g.VBox(FALSE, 0)
		self.add(vbox)

		self.time_label = g.Label('')
		time_button = g.Button()
		time_button.add(self.time_label)
		time_button.unset_flags(g.CAN_FOCUS)
		vbox.pack_start(time_button, expand = FALSE)

		self.list = g.TreeView(memo_list.visible)
		vbox.pack_start(self.list, expand = TRUE)
		self.list.unset_flags(g.CAN_FOCUS)

		cell = g.CellRendererText()
		column = g.TreeViewColumn('Time', cell, text = 0)
		cell.set_property('xalign', 1)
		self.list.append_column(column)

		cell = g.CellRendererText()
		column = g.TreeViewColumn('Message', cell, text = 1)
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
		time_button.connect('button-press-event', self.button_press)
		time_button.connect('clicked', self.new_memo)

		menu.attach(self, self)

		rox.toplevel_ref()

		self.connect('destroy', lambda w: rox.toplevel_unref())

		self.update()
		gobject.timeout_add(10000, self.update)	# Update clock

		self.timeout = None	# For next alarm
		self.alert_box = None
		self.show_all_box = None
		self.save_box = None
		self.prime()

		# If we had more than one window, we'd need a remove too...
		memo_list.watchers.append(self.prime)
		app_options.add_notify(self.options_changed)
		
		self.show_all()
	
	def show_options(self):
		rox.edit_options()
	
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
		else:
			# Note: importing gtk breaks strftime for am/pm
			text = time.strftime('%a %d-%b-%Y  ') + \
					pretty_time.str_time()
		self.time_label.set_text(text)
		
		t = time.localtime()
		year, month, day, hour, minute, second,	weekday, julian, dst = t
		if self.last_day != day:
			if self.last_day is not None:
				self.memo_list.new_day()
			self.last_day = day

		return TRUE
	
	def new_memo(self, widget = None):
		from EditBox import EditBox
		EditBox().show()
	
	def help(self):
		from rox import filer
		filer.open_dir(rox.app_dir + '/Help')

	def button_press(self, widget, event):
		if event.type != g.gdk.BUTTON_PRESS:
			return
		elif event.button == 2 or event.button == 3:
			menu.popup(self, event)
			return 1
		return 0
	
	def show_all_memos(self):
		if self.show_all_box:
			self.show_all_box.present()
			return
		def destroyed(widget): self.show_all_box = None
		from ShowAll import ShowAll
		self.show_all_box = ShowAll()
		self.show_all_box.connect('destroy', destroyed)
		self.show_all_box.show()

	# Deal with any missed alarms
	# Set a timeout for the next alarm
	def prime(self):
		if self.alert_box:
			return		# Don't do anything until closed
			
		missed, delay = self.memo_list.catch_up()
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
