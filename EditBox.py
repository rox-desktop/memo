import rox
from rox import g, FALSE, TRUE
import time

from Arrow import Arrow
from Memo import Memo
from __main__ import memo_list

from pretty_time import str_time

DELETE = 1
HIDE = 2

refleak_bug_workaround = []

class EditBox(g.Dialog):
	def __init__(self, memo = None):
		g.Dialog.__init__(self)
		self.set_has_separator(FALSE)

		self.add_button(g.STOCK_HELP, g.RESPONSE_HELP)

		if memo:
			self.add_button(g.STOCK_DELETE, DELETE)

			button = rox.ButtonMixed(g.STOCK_ZOOM_OUT, '_Hide')
			button.set_flags(g.CAN_DEFAULT)
			self.add_action_widget(button, HIDE)

		self.add_button(g.STOCK_CANCEL, g.RESPONSE_CANCEL)

		button = rox.ButtonMixed(g.STOCK_YES, '_Set')
		button.set_flags(g.CAN_DEFAULT)
		self.add_action_widget(button, g.RESPONSE_YES)

		self.memo = memo
		if memo:
			self.set_title("Edit memo:")
			t = time.localtime(memo.time)
		else:
			self.set_title("Create memo:")
			t = time.localtime(time.time() + 5 * 60)
			
		year, month, day, hour, minute, second,	weekday, julian, dst = t
		self.hour = hour
		self.min = minute

		self.cal = g.Calendar()
		self.cal.select_month(month - 1, year)
		self.cal.select_day(day)

		at_box = self.make_at_box()

		text_frame = self.make_text_view()

		# Time/Date on the left, Text on the right
		hbox = g.HBox(FALSE, 0)
		self.vbox.pack_start(hbox, TRUE, TRUE, 0)

		# Date above time
		vbox = g.VBox(FALSE, 0)
		hbox.pack_start(vbox, FALSE, TRUE, 0)
		vbox.set_border_width(4)
		vbox.pack_start(self.cal, FALSE, TRUE, 0)

		spacer = g.Alignment()
		vbox.pack_start(spacer, FALSE, TRUE, 2)

		vbox.pack_start(at_box, FALSE, TRUE, 0)

		hbox.pack_start(text_frame, TRUE, TRUE, 0)

		self.vbox.show_all()

		if memo:
			buffer = self.text.get_buffer()
			try:
				buffer.insert_at_cursor(memo.message)
			except TypeError:
				buffer.insert_at_cursor(memo.message, -1)
		if memo and memo.at:
			self.at.set_active(TRUE)
		if memo == None or memo.at == 0:
			self.at_box.hide()

		self.connect('response', self.response)
		self.text.grab_focus()
		self.set_default_response(g.RESPONSE_YES)

		self.connect('destroy', lambda w: refleak_bug_workaround.remove(self))
		refleak_bug_workaround.append(self)

	def make_text_view(self):
		# The TextView / time of day settings
		vbox = g.VBox(FALSE, 0)
		l = g.Label('Message:')
		l.set_alignment(0, 1)
		l.set_padding(0, 4)
		vbox.pack_start(l, FALSE, TRUE, 0)

		frame = g.Frame()
		vbox.pack_start(frame, TRUE, TRUE, 0)
		frame.set_shadow_type(g.SHADOW_IN)

		hbox = g.HBox(FALSE, 0)
		frame.add(hbox)

		text = g.TextView()
		hbox.pack_start(text, TRUE, TRUE, 0)
		text.set_wrap_mode(g.WRAP_WORD)

		scrollbar = g.VScrollbar()
		adj = scrollbar.get_adjustment()
		text.set_scroll_adjustments(None, adj)
		hbox.pack_start(scrollbar, FALSE, TRUE, 0)

		text.set_size_request(200, 200)

		self.text = text

		return vbox

	def make_at_box(self):
		# The time of day setting
		hbox = g.HBox(FALSE, 0)

		self.at = g.CheckButton('At...')
		hbox.pack_start(self.at, FALSE, TRUE, 4)
		self.at.connect('toggled', self.at_toggled)

		at_box = g.HBox(FALSE, 0)
		self.at_box = at_box
		hbox.pack_start(at_box, FALSE, TRUE, 0)

		arrow = Arrow(g.ARROW_LEFT, self.adj_time, -60)
		at_box.pack_start(arrow, FALSE, TRUE, 0)
		arrow = Arrow(g.ARROW_RIGHT, self.adj_time, 60)
		at_box.pack_start(arrow, FALSE, TRUE, 0)

		self.time_display = g.Label(str_time(self.hour, self.min))
		self.time_display.set_padding(4, 0)
		frame = g.Frame()
		frame.add(self.time_display)
		at_box.pack_start(frame, FALSE, TRUE, 0)

		arrow = Arrow(g.ARROW_LEFT, self.adj_time, -1)
		at_box.pack_start(arrow, FALSE, TRUE, 0)
		arrow = Arrow(g.ARROW_RIGHT, self.adj_time, 1)
		at_box.pack_start(arrow, FALSE, TRUE, 0)

		return hbox
	
	def response(self, widget, response):
		try:
			if response == DELETE:
				memo_list.delete(self.memo)
			elif response == HIDE:
				self.add(hide = 1)
			elif response == g.RESPONSE_YES:
				self.add()
			elif response == g.RESPONSE_HELP:
				from rox import filer
				filer.open_dir(rox.app_dir + '/Help')
				return
			elif response == g.RESPONSE_CANCEL:
				pass
			elif response == g.RESPONSE_DELETE_EVENT:
				return
			else:
				raise Exception("Unknown response: %d" % response)
		except:
			rox.report_exception()
		self.destroy()
	
	def add(self, hide = 0):
		(y, m, d) = self.cal.get_date()
		t = time.mktime((y, m + 1, d, self.hour, self.min,
				 0, -1, -1, -1))
		at = self.at_box.flags() & g.VISIBLE
		buffer = self.text.get_buffer()
		start = buffer.get_start_iter()
		end = buffer.get_end_iter()
		message = buffer.get_text(start, end, TRUE)
		memo = Memo(t, message, at = at != 0, hidden = hide)
		if self.memo:
			memo_list.delete(self.memo, update = 0)
		memo_list.add(memo)
		memo_list.warn_if_not_visible(memo)
	
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
