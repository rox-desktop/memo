from rox import g
import time

from memos import memo_list

DELETE = 1
EDIT = 2

class Alarm(g.MessageDialog):
	def __init__(self, memo):
		g.MessageDialog.__init__(self, None, g.DIALOG_MODAL,
					 g.MESSAGE_INFO, g.BUTTONS_NONE,
					 'Alarm set for %s:\n%s' %
					 (time.ctime(memo.time), memo.message))
		self.add_button(g.STOCK_DELETE, DELETE)
		self.add_button(g.STOCK_PROPERTIES, EDIT)
		self.add_button(g.STOCK_OK, g.RESPONSE_OK)

		self.set_title('Memo:')
		self.set_modal(g.TRUE)
		self.set_position(g.WIN_POS_CENTER)
		memo.silent = 1
		self.memo = memo
		
		self.connect('response', self.response)
		self.set_default_response(g.RESPONSE_OK)
	
	def response(self, widget, response):
		if response == g.RESPONSE_OK:
			pass
		elif response == DELETE:
			memo_list.delete(self.memo)
			memo_list.save()
			pass
		elif response == EDIT:
			from EditBox import EditBox
			EditBox(self.memo).show()
		elif response == g.RESPONSE_DELETE_EVENT:
			return
		else:
			print "Unknown response", response
			return
		self.destroy()
