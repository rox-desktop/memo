from gtk import *
from time import *

from Arrow import Arrow
from Memo import Memo
import memos
from support import *

class EditBox(GtkWindow):
	def __init__(self, memo):
		GtkWindow.__init__(self, WINDOW_DIALOG)
		self.memo = memo
		if memo:
			self.set_title("Edit memo:")
		else:
			self.set_title("Create memo:")
			
		self.set_border_width(2)

		vbox = GtkVBox(FALSE, 0)
		self.add(vbox)

		hbox = GtkHBox(FALSE, 0)
		vbox.pack_start(hbox, FALSE, TRUE, 0)

		if memo:
			t = localtime(memo.time)
		else:
			t = localtime(time() + 5 * 60)
		year, month, day, hour, minute, second,	weekday, julian, dst = t
		self.hour = hour
		self.min = minute

		self.cal = GtkCalendar()
		hbox.pack_start(self.cal, FALSE, TRUE, 4)
		self.cal.select_month(month - 1, year)
		self.cal.select_day(day)

		self.text = GtkText()
		self.text.set_editable(TRUE)
		if memo:
			self.text.insert_defaults(memo.message)
		hbox.pack_start(self.text, TRUE, TRUE, 0)
		scrollbar = GtkVScrollbar(self.text.get_vadjustment())
		hbox.pack_start(scrollbar, FALSE, TRUE, 0)

		hbox = GtkHBox(FALSE, 0)
		vbox.pack_start(hbox, FALSE, TRUE, 0)


		at = GtkCheckButton('At...')
		hbox.pack_start(at, FALSE, TRUE, 4)
		if memo and memo.at:
			at.set_active(TRUE)
		at.connect('toggled', self.at_toggled)

		at_box = GtkHBox(FALSE, 0)
		self.at_box = at_box
		hbox.pack_start(at_box, FALSE, TRUE, 0)

		arrow = Arrow(ARROW_LEFT, self.adj_time, -60)
		at_box.pack_start(arrow, FALSE, TRUE, 4)
		arrow = Arrow(ARROW_RIGHT, self.adj_time, 60)
		at_box.pack_start(arrow, FALSE, TRUE, 4)

		self.time_display = GtkLabel(str_time(self.hour, self.min))
		self.time_display.set_padding(4, 0)
		frame = GtkFrame()
		frame.add(self.time_display)
		at_box.pack_start(frame, FALSE, TRUE, 0)

		arrow = Arrow(ARROW_LEFT, self.adj_time, -1)
		at_box.pack_start(arrow, FALSE, TRUE, 4)
		arrow = Arrow(ARROW_RIGHT, self.adj_time, 1)
		at_box.pack_start(arrow, FALSE, TRUE, 4)

		
		hbox = GtkHBox(FALSE, 0)
		vbox.pack_start(hbox, FALSE, TRUE, 0)

		hbox = GtkHBox(TRUE, 0)
		vbox.pack_start(hbox, FALSE, TRUE, 2)

		button = GtkButton("OK")
		hbox.pack_start(button, TRUE, TRUE, 30)
		button.set_flags(CAN_DEFAULT)
		button.grab_default()
		button.connect('clicked', self.ok_clicked)

		button = GtkButton("Remove")
		hbox.pack_start(button, TRUE, TRUE, 30)
		button.set_flags(CAN_DEFAULT)
		button.connect('clicked', self.remove_clicked)
		if not self.memo:
			button.set_sensitive(FALSE)

		button = GtkButton("Cancel")
		hbox.pack_start(button, TRUE, TRUE, 30)
		button.set_flags(CAN_DEFAULT)
		button.connect('clicked', lambda w, win: win.destroy(), self)
		
		vbox.show_all()
		if memo == None or memo.at == 0:
			at_box.hide()
		self.text.grab_focus()
	
	def remove_clicked(self, button):
		memos.memo_list.delete(self.memo)
		self.destroy()
	
	def ok_clicked(self, button):
		(y, m ,d) = self.cal.get_date()
		t = mktime((y, m + 1, d, self.hour, self.min, 0, -1, -1, -1))
		at = self.at_box.flags() & VISIBLE
		memo = Memo(t, self.text.get_chars(0, -1), at = at)
		memos.memo_list.add(memo, remove = self.memo)
		self.destroy()
	
	def adj_time(self, increment):
		min = self.min + increment
		if min < 0 and self.hour == 0:
			return
		if min > 59 and self.hour == 23:
			return
		if min < 0:
			min = min + 60
			self.hour = self.hour - 1
		if min > 59:
			min = min - 60
			self.hour = self.hour + 1
		self.min = min
		self.time_display.set_text(str_time(self.hour, self.min))
	
	def at_toggled(self, at):
		if at.get_active():
			self.at_box.show()
		else:
			self.at_box.hide()
