from rox import g
import rox
import time
from Memo import Memo

HIDE = 1
EDIT = 2

class Alarm(g.MessageDialog):
	def __init__(self, memo):
		g.MessageDialog.__init__(self, None, g.DIALOG_MODAL,
					 g.MESSAGE_INFO, g.BUTTONS_NONE,
					 _('Alarm set for %s:\n%s') %
					 (time.ctime(memo.time), memo.message))

		now = time.time()
		delay = memo.time - now
		earlyAlert = delay > 0

		button = rox.ButtonMixed(g.STOCK_ZOOM_OUT, _('_Hide memo'))
		button.set_flags(g.CAN_DEFAULT)
		self.add_action_widget(button, HIDE)
		button.show()

		button = rox.ButtonMixed(g.STOCK_PROPERTIES, _('_Edit'))
		button.set_flags(g.CAN_DEFAULT)
		self.add_action_widget(button, EDIT)
		button.show()

		self.add_button(g.STOCK_OK, g.RESPONSE_OK)

		self.set_title('Memo:')
		self.set_modal(True)
		self.set_position(g.WIN_POS_CENTER)

		if earlyAlert:
			memo.state = Memo.EARLY
		else:
			memo.state = Memo.DONE

		from main import memo_list
		memo_list.notify_changed()

		self.memo = memo
		
		self.connect('response', self.response)
		self.set_default_response(g.RESPONSE_OK)
	
	def response(self, widget, response):
		if response == int(g.RESPONSE_OK):
			pass
		elif response == HIDE:
			from main import memo_list
			memo_list.set_hidden(self.memo, 1)
		elif response == EDIT:
			from EditBox import EditBox
			EditBox(self.memo).show()
		elif response == int(g.RESPONSE_DELETE_EVENT):
			return
		else:
			print("Unknown response", response)
			return
		self.destroy()
