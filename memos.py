from __future__ import generators

import rox, gobject
from rox import g, choices

import time
import os

from Memo import Memo, memo_from_node

# Columns
TIME = 0
BRIEF = 1
MEMO = 2

class MemoList(g.ListStore):
	def __init__(self):
		g.ListStore.__init__(self, gobject.TYPE_STRING,	# Time
					gobject.TYPE_STRING,	# Brief
					gobject.TYPE_OBJECT)	# Memo
		self.watchers = []

		path = choices.load('Memo', 'Entries')
		if path:
			try:
				from xml.dom import minidom, Node
				doc = minidom.parse(path)
			except:
				rox.report_exception()

			errors = 0
			for node in doc.documentElement.childNodes:
				if node.nodeType == Node.ELEMENT_NODE:
					try:
						memo = memo_from_node(node)
						self.add(memo)
					except:
						if not errors:
							rox.report_exception()
							errors = 1
	
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
					map(apply, self.watchers)
					self.save()
				return
		
		raise Exception('Memo %s not found!' % memo)
	
	def add(self, memo):
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
			 MEMO, memo)

		map(apply, self.watchers)
		self.save()
	
	def save(self):
  		path = choices.save('Memo', 'Entries.new')
		if not path:
			sys.stderr.write(
				"Memo: Saving disabled by CHOICESPATH\n")
			return
		try:
			from xml.dom import minidom
			doc = minidom.Document()

			root = doc.createElement('memos')
			doc.appendChild(root)
			for iter in self:
				m = self.get_value(iter, MEMO)
				m.save(root)

			f = os.open(path, os.O_CREAT | os.O_WRONLY,
				    0600)
			stream = os.fdopen(f, 'w')
			doc.writexml(stream)
			stream.close()

			real_path = choices.save('Memo', 'Entries')
			os.rename(path, real_path)
		except:
  			rox.report_exception()
	
	def get_memo_by_path(self, path):
		iter = memo_list.get_iter(path)
		return self.get_memo_by_iter(iter)
	
	def get_memo_by_iter(self, iter):
		return memo_list.get_value(iter, MEMO)

	def catch_up(self):
		"Returns a list of alarms to go off, and the time until the "
		"next alarm (in seconds) or None."
		
		missed = []
		now = time.time()

		for iter in self:
			m = self.get_value(iter, MEMO)

			if m.silent or not m.at:
				continue

			delay = m.time - now

			if delay <= 0:
				missed.append(m)
			else:
				return (missed, delay)
		return (missed, None)
	
memo_list = MemoList()
