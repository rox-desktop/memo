import memos
from gtk import *
from support import *

current_alarm = None
alarms = []

def show_alarm(memo):
	def process_next(widget = None, process_next = None):
		if len(alarms) > 0:
			current_alarm = Alarm(alarms[0])
			del alarms[0]
			current_alarm.connect('destroy', process_next)
			memos.memo_list.save()
			gdk_beep()
			current_alarm.show()
	alarms.append(memo)
	if current_alarm == None:
		process_next(process_next = process_next)

class Alarm(GtkWindow):
	def __init__(self, memo):
		GtkWindow.__init__(self, WINDOW_DIALOG)
		self.set_title('Memo:')
		self.set_modal(TRUE)
		self.set_position(WIN_POS_CENTER)
		self.set_border_width(2)
		memo.silent = 1
		self.memo = memo

		vbox = GtkVBox(FALSE, 0)
		self.add(vbox)

		message = GtkLabel(memo.message)
		message.set_line_wrap(TRUE)
		text_container = GtkEventBox()
		text_container.set_border_width(40)
		text_container.add(message)
		vbox.pack_start(text_container, TRUE, TRUE, 0)

		action_area = GtkHBox(TRUE, 5)
		action_area.set_border_width(2)
		vbox.pack_start(GtkHSeparator(), FALSE, TRUE, 2)
		vbox.pack_start(action_area, FALSE, TRUE, 0)

		default_button = None
		for b in ['Remove', 'Silence', 'Edit']:
			label = GtkLabel(b)
			label.set_padding(16, 2)
			button = GtkButton()
			button.add(label)
			button.set_flags(CAN_DEFAULT)
			action_area.pack_start(button, TRUE, TRUE, 0)
			button.connect('clicked', self.button, b)
			if not default_button:
				default_button = button
		
		default_button.grab_focus()
		default_button.grab_default()
		action_area.set_focus_child(default_button)

		self.show_all(vbox)
	
	def button(self, button, text):
		self.destroy()
		if text == 'Remove':
			memos.memo_list.delete(self.memo)
		elif text == 'Edit':
			memos.edit_memo(self.memo)
