import os
import string
import time

import gobject

from pretty_time import month_name, str_time

def memo_from_node(node):
	assert node.localName == 'memo'

	def flag(attr):
		v = node.getAttribute(attr)
		try:
			return int(v)
		except:
			return 0

	time, = node.getElementsByTagName('time')
	message, = node.getElementsByTagName('message')

	message = ''.join([n.nodeValue for n in message.childNodes])

	return Memo(float(time.childNodes[0].nodeValue),
		    message, flag('at'), flag('silent'), flag('hidden'))

class Memo(gobject.GObject):
	# 'time' is seconds since epoch
	# 'at' is TRUE if the time of day matters
	def __init__(self, time, message, at, silent = 0, hidden = 0):
		self.__gobject_init__()

		assert at == 0 or at == 1
		assert silent == 0 or silent == 1
		assert hidden == 0 or hidden == 1

		self.time = int(time)
		self.message = message.strip()
		self.at = at
		self.silent = silent
		self.hidden = hidden
		self.brief = self.message.split('\n', 1)[0]
	
	def str_when(self):
		now_y, now_m, now_d = time.localtime(time.time() + 5 * 60)[:3]
		now_m = now_m - 1

		year, month, day, hour, min = time.localtime(self.time)[:5]
		month = month - 1

		if year != now_y:
			return '%s-%d' % (month_name[month][:3], year)

		if month != now_m or day != now_d:
			return '%02d-%s' % (day, month_name[month][:3])

		if self.at:
			return str_time(hour, min)

		return 'Today'
	
	def comes_after(self, other):
		return self.time > other.time
	
	def save(self, parent):
		doc = parent.ownerDocument

		node = doc.createElement('memo')
		node.setAttribute('at', str(self.at))
		node.setAttribute('silent', str(self.silent))
		node.setAttribute('hidden', str(self.hidden))
		parent.appendChild(node)

		time = doc.createElement('time')
		time.appendChild(doc.createTextNode(str(self.time)))
		node.appendChild(time)

		message = doc.createElement('message')
		message.appendChild(doc.createTextNode(self.message))
		node.appendChild(message)
	
	def set_hidden(self, hidden):
		assert hidden == 0 or hidden == 1

		self.hidden = hidden
