from gtk import *
from time import *
import os
import string
import choices
from xmllib import *
from support import *
from TimeDisplay import month_name

from Memo import Memo
from Alarm import *
from EditBox import EditBox

memo_box = None

def new_memo():
	edit_memo(None)

def edit_memo(memo = None):
	global memo_box
	if memo_box:
		memo_box.destroy()
	memo_box = EditBox(memo)
	memo_box.show()

class MemoList(GtkCList):
	def __init__(self):
		global memo_list
		memo_list = self

		GtkCList.__init__(self, 2)
		self.set_shadow_type(SHADOW_NONE)
		self.set_column_auto_resize(0, TRUE)
		self.set_column_justification(0, JUSTIFY_RIGHT)
		self.memos = []
		self.timeout = 0

		path = choices.load('Memo', 'Entries')
		if path:
			self.loading = TRUE
			try:
				l = Loader(self, path)
				f = open(path, 'rb')
				l.feed(f.read())
				l.close()
			except:
				report_exception()
		self.loading = FALSE

		self.connect('select-row', self.select_row)

		self.prime()
	
	def select_row(self, list, row, col, bev):
		list.unselect_row(row, col)
		memo = self.memos[row]
		edit_memo(memo)
	
	def add(self, memo, remove = None):
		if remove:
			self.delete(remove, save = FALSE)
			
		i = 0
		for m in self.memos:
			if m.comes_after(memo):
				break
			i = i + 1
		self.insert(i, (memo.str_when() + ':', memo.brief))
		self.memos.insert(i, memo)

		if not self.loading:
			self.save()
			self.prime()
	
	def delete(self, memo, save = TRUE):
		i = self.memos.index(memo)
		del self.memos[i]
		self.remove(i)
		if save:
			self.save()
			self.prime()
	
	def save(self):
  		path = choices.save('Memo', 'Entries.new')
		if not path:
			sys.stderr.write(
				"Memo: Saving disabled by CHOICESPATH\n")
			return
		try:
			f = None
			try:
				f = os.open(path,
					    os.O_CREAT | os.O_WRONLY,
					    0600)
				os.write(f, '<?xml version="1.0"?>\n<memos>\n')
				for m in self.memos:
					m.save(f)
				os.write(f, '</memos>\n')
			finally:
				if f != None:
					os.close(f)
			real_path = choices.save('Memo', 'Entries')
			os.rename(path, real_path)
		except:
  			report_exception()
	
	# Deal with any missed alarms
	# Set a timeout for the next alarm
	def prime(self):
		for m in self.memos[:]:
			if m.silent or not m.at:
				continue
			delay = m.time - time()

			if delay <= 0:
				show_alarm(m)
			else:
				self.schedule(delay)
				return

	def timeout_cb(self):
		timeout_remove(self.timeout)
		self.timeout = 0
		self.prime()
		return 0
	
	def schedule(self, delay):
		if self.timeout:
			timeout_remove(self.timeout)

		# Avoid overflows - don't resched more than a day ahead
		if delay > 60 * 60 * 24:
			delay = 60 * 60 * 24

		self.timeout = timeout_add(1000 * delay, self.timeout_cb)

class Loader(XMLParser):
	def __init__(self, list, path):
		XMLParser.__init__(self)
		self.list = list
		f = open(path, 'rb')
		self.elements = {
			'memo': (self.start_memo, self.end_memo),
			'time': (self.start_time, None),
			'message': (self.start_message, None)
		}
		self.attributes = {
			'memo' : {'at': '0', 'silent': '0'}
		}
		self.data_tag = None
	
	def start_memo(self, attribs):
		self.time = ''
		self.message = ''
		self.at = int(attribs['at'])
		self.silent = int(attribs['silent'])
	
	def end_memo(self):
		m = Memo(int(self.time), self.message, self.at, self.silent)
		self.list.add(m)
	
	def start_message(self, attribs):
		self.data_tag = 'message'
		self.message = ''
	
	def start_time(self, attribs):
		self.data_tag = 'time'
		self.time = ''
	
	def unknown_endtag(self, tag):
		self.data_tag = None
	
	def handle_data(self, d):
		if not self.data_tag:
			return
		setattr(self, self.data_tag, getattr(self, self.data_tag) + d)

MemoList()
