import rox
from rox import g, TRUE, FALSE

from __main__ import memo_list
import pretty_time, time
import memos

class ShowAll(g.Dialog):
	def __init__(self):
		g.Dialog.__init__(self)
		self.set_title('All memos')
		self.set_has_separator(FALSE)

		self.add_button(g.STOCK_CLOSE, g.RESPONSE_CANCEL)

		frame = g.Frame()
		self.vbox.pack_start(frame, TRUE, TRUE, 0)
		frame.set_shadow_type(g.SHADOW_IN)

		hbox = g.HBox(FALSE, 0)
		frame.add(hbox)

		scroll = g.VScrollbar()
		hbox.pack_end(scroll)
		
		self.list = g.TreeView(memo_list)
		hbox.pack_start(self.list, TRUE, TRUE, 0)
		self.list.set_scroll_adjustments(None, scroll.get_adjustment())
		self.list.set_size_request(-1, 12)
		self.set_default_size(-1, 300)

		text = g.CellRendererText()

		toggle = g.CellRendererToggle()
		column = g.TreeViewColumn('H', toggle,
					  active = memos.HIDDEN)
		self.list.append_column(column)
		toggle.connect('toggled',
			lambda t, path: memo_list.toggle_hidden(path))

		column = g.TreeViewColumn('Time', text, text = memos.TIME)
		self.list.append_column(column)
		
		column = g.TreeViewColumn('Message', text, text = memos.BRIEF)
		self.list.append_column(column)
		
		self.list.set_headers_visible(TRUE)
		
		sel = self.list.get_selection()
		sel.set_mode(g.SELECTION_MULTIPLE)

		def activate(view, path, column):
			memo = memo_list.get_memo_by_path(path)
			from EditBox import EditBox
			EditBox(memo).show()
		
		self.add_events(g.gdk.BUTTON_PRESS_MASK)
		self.list.connect('button-press-event', self.button_press)
		self.list.connect('row-activated', activate)

		#memo_list.watchers.append(self.prime)
		#def destroyed(widget): memo_list.watchers.remove(self.prime)
		#self.connect('destroy', destroyed)

		self.connect('response', self.response)
		
		self.show_all()
	
	def response(self, box, response):
		if response == g.RESPONSE_CANCEL:
			self.destroy()
	
	def button_press(self, widget, event):
		if event.type != g.gdk.BUTTON_PRESS:
			return
		elif event.button == 2 or event.button == 3:
			menu.popup(self, event)
			return 1
		return 0
