from __future__ import generators

import rox, gobject
from rox import g, choices, app_options, options

import time
import os

from Memo import Memo, memo_from_node

max_visible = options.Option('max_visible', 5)
max_future = options.Option('max_future', 6)

# Columns
TIME = 0
BRIEF = 1
MEMO = 2
HIDDEN = 3

class MemoList(g.ListStore):
	def __init__(self):
		g.ListStore.__init__(self, gobject.TYPE_STRING,	# Time
					gobject.TYPE_STRING,	# Brief
					gobject.TYPE_OBJECT,	# Memo
					gobject.TYPE_BOOLEAN)	# Deleted
		self.watchers = []
	
	def __iter__(self):
		"When used as a python iterator, return a list of TreeIters"
		iter = self.get_iter_first()
		while iter:
			yield iter
			if not self.iter_next(iter):
				iter = None
	
	def delete(self, memo, update = 1):
		for iter in self:
			m = self.get_value(iter, MEMO)
			if m is memo:
				self.remove(iter)
				if update:
					self.notify_changed()
				return
		# Not found. That's OK.
	
	def add(self, memo, update = 1):
		assert isinstance(memo, Memo)

		for iter in self:
			m = self.get_value(iter, MEMO)
			if m.comes_after(memo):
				break
		else:
			iter = None

		if iter:
			new = self.insert_before(iter)
		else:
			# PyGtk bug
			new = self.append()
		
		self.set(new,
			 TIME, memo.str_when(),
			 BRIEF, memo.brief,
			 MEMO, memo,
			 HIDDEN, memo.hidden)

		if update:
			self.notify_changed()
	
	def notify_changed(self):
		"Called after a Memo is added, removed or updated."
		map(apply, self.watchers)
	
	def get_memo_by_path(self, path):
		iter = self.get_iter(path)
		return self.get_memo_by_iter(iter)
	
	def get_memo_by_iter(self, iter):
		return self.get_value(iter, MEMO)

	def catch_up(self):
		"Returns a list of alarms to go off, and the time until the "
		"next alarm (in seconds) or None."
		
		missed = []
		now = time.time()

		for iter in self:
			m = self.get_value(iter, MEMO)

			if m.silent or m.hidden or not m.at:
				continue

			delay = m.time - now

			if delay <= 0:
				missed.append(m)
			else:
				return (missed, delay)
		return (missed, None)

class MasterList(MemoList):
	def __init__(self):
		MemoList.__init__(self)

		self.visible = MemoList()

		path = choices.load('Memo', 'Entries')
		if path:
			try:
				from xml.dom import minidom, Node
				doc = minidom.parse(path)
			except:
				rox.report_exception()

			errors = 0
			root = doc.documentElement
			for node in root.getElementsByTagName('memo'):
				try:
					memo = memo_from_node(node)
					self.add(memo, update = 0)
				except:
					if not errors:
						rox.report_exception()
						errors = 1
		self.update_visible()
		app_options.add_notify(self.update_visible)
	
	def toggle_hidden(self, path):
		iter = self.get_iter_first()
		self.get_iter_from_string(iter, path)
		memo = self.get_memo_by_iter(iter)
		self.set_hidden(memo, not memo.hidden)
	
	def set_hidden(self, memo, hidden):
		self.delete(memo, update = 0)
		memo.set_hidden(hidden)
		self.add(memo)
	
	def save(self):
  		path = choices.save('Memo', 'Entries.new')
		if not path:
			sys.stderr.write(
				"Memo: Saving disabled by CHOICESPATH\n")
			return
		try:
			f = os.open(path, os.O_CREAT | os.O_WRONLY, 0600)
			self.save_to_stream(os.fdopen(f, 'w'))

			real_path = choices.save('Memo', 'Entries')
			os.rename(path, real_path)
		except:
  			rox.report_exception()

	def save_to_stream(self, stream):
		from xml.dom import minidom
		doc = minidom.Document()

		root = doc.createElement('memos')
		doc.appendChild(root)
		for iter in self:
			m = self.get_value(iter, MEMO)
			m.save(root)
			root.appendChild(doc.createTextNode('\n'))
		doc.writexml(stream)
	
	def notify_changed(self):
		"Called after a Memo is added, removed or updated."
		MemoList.notify_changed(self)
		self.update_visible()
		self.save()
	
	def choose_visible(self):
		"Return a list of Memos which should be made/kept visible."
		now = time.time()
		A_DAY = 60 * 60 * 24

		VISIBLE_REGION = A_DAY * 31 * max_future.int_value

		out = []
		for iter in self:
			memo = self.get_value(iter, MEMO)

			if memo.hidden:
				continue
			
			if memo.time > now + VISIBLE_REGION:
				break	# Way too far ahead
			
			if memo.time > now + A_DAY:
				# Skip future memos if the list is too long
				if len(out) >= max_visible.int_value:
					break

			out.append(memo)

		return out
	
	def update_visible(self):
		# Find what was in the visible list
		old_vis = {}
		for iter in self.visible:
			old_vis[self.visible.get_value(iter, MEMO)] = None

		new_vis = self.choose_visible()

		# Find what has changed
		to_hide = []
		to_show = []
		for memo in new_vis:
			if memo in old_vis:
				del old_vis[memo]
			else:
				to_show.append(memo)

		# Anything remaining was visible but isn't now
		for memo in old_vis:
			to_hide.append(memo)
					
		if not to_show and not to_hide:
			return
			
		# Apply changes
		for m in to_hide:
			self.visible.delete(m, update = 0)
		for m in to_show:
			self.visible.add(m, update = 0)
		self.visible.notify_changed()

	def warn_if_not_visible(self, memo):
		if memo.hidden:
			return
		for iter in self.visible:
			m = self.visible.get_value(iter, MEMO)
			if m is memo:
				return
		rox.info("This memo has been added, but is not shown in the main "
			 "window. Use Show All from the popup menu to see it.\n\n"
			 "You can use the Options window to control when memos "
			 "are shown in the main window.")
