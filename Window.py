import rox
from rox import g, TRUE, FALSE, app_options
from rox.Menu import Menu
from rox.options import Option

import pretty_time, time
from Alarm import Alarm

time_format = Option('time_format', 'text')
app_options.register(time_format)

menu = Menu('main', [
                ('/Add Memo...', 'new_memo',    ''),
                ('/Show All...', 'show_all_memos', ''),
		('/',		 '',		'<Separator>'),
                ('/Options...',  'show_options',''),
                ('/Help',        'help',	''),
                ('/Quit',        'destroy',     ''),
                ])

class Window(g.Window):
	def __init__(self, memo_list):
		g.Window.__init__(self)
		self.set_wmclass('Memo', 'Memo')
		self.set_title('Memo')
		self.set_resizable(FALSE)
		self.set_type_hint(g.gdk.WINDOW_TYPE_HINT_DIALOG)

		self.memo_list = memo_list

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
		# the text in the column comes from column 0
		column = g.TreeViewColumn('Time', cell, text = 0)
		self.list.append_column(column)
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
		g.timeout_add(10000, self.update)	# Update clock

		self.timeout = None	# For next alarm
		self.alert_box = None
		self.show_all_box = None
		self.prime()

		# If we had more than one window, we'd need a remove too...
		memo_list.watchers.append(self.prime)
		app_options.add_notify(self.update)
		
		self.show_all()

		self.show_all_memos()
	
	def show_options(self):
		rox.edit_options()
	
	def update(self):
		if time_format.value == 'text':
			text = pretty_time.rough_time(time.time())
		else:
			text = time.strftime('%a %d/%b/%Y %H:%M')
		self.time_label.set_text(text)
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
		g.timeout_remove(self.timeout)
		self.timeout = 0
		self.prime()
		return 0
	
	def schedule(self, delay):
		if self.timeout:
			g.timeout_remove(self.timeout)

		# Avoid overflows - don't resched more than a day ahead
		if delay > 60 * 60 * 24:
			delay = 60 * 60 * 24

		self.timeout = g.timeout_add(1000 * delay, self.timeout_cb)
