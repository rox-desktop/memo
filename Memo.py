import os
import string
from time import *

from support import *
from TimeDisplay import month_name

class Memo:
	# 'time' is seconds since epoch
	# 'at' is TRUE if the time of day matters
	def __init__(self, time, message, at, silent = 0):
		self.time = time
		self.message = string.strip(message)
		self.at = at != 0
		self.silent = silent != 0
		self.brief = string.split(self.message, '\n', 1)[0]
	
	def str_when(self):
		now_y, now_m, now_d = localtime(time() + 5 * 60)[:3]
		now_m = now_m - 1

		year, month, day, hour, min = localtime(self.time)[:5]
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
	
	def save(self, stream):
		os.write(stream, '  <memo at="%d" silent="%d">\n' %
						(self.at, self.silent))
		os.write(stream, '    <time>%d</time>\n' % self.time)
		os.write(stream, '    <message>%s</message>\n' % self.message)
		os.write(stream, '  </memo>\n')
