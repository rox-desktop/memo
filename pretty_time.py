import time

day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
	    'Saturday', 'Sunday']

month_name = ['January', 'February', 'March', 'April',
	      'May', 'June', 'July', 'August',
	      'September', 'October', 'November', 'December']

about_message = ['nearly', 'nearly', 'about', 'just gone', 'just gone']

section_name = ['', 'five past ', 'ten past ', 'a quarter past ',
	        'twenty past ', 'twenty-five past ', 'half past ',
		'twenty-five to ', 'twenty to ', 'a quarter to ',
		'ten to ', 'five to ']

number = [None, 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
	  'nine', 'ten', 'eleven']

def hour_name(hour):
	assert hour >= 0 and hour < 24

	if hour == 0:
		return "midnight"
	elif hour == 12:
		return "noon"
	return number[hour % 12]

def th(n):
	"Cardinal integer to ordinal string."
	if n > 3 and n < 20:
		return "%dth" % n

	d = n % 10
	if d == 1:
		return "%dst" % n
	elif d == 2:
		return "%dnd" % n
	elif d == 3:
		return "%drd" % n
	else:
		return "%dth" % n

def rough_time(time_in_seconds):
	"Convert a time (as returned by time()) to a string."
	t = time.localtime(time_in_seconds + 150)
	year, month, day, hour, minute, second,	weekday, julian, dst = t

	off = about_message[minute % 5]

	if minute / 5 > 6:
		hour = (hour + 1) % 24

	if minute / 5 == 0 and hour != 0 and hour != 12:
		o_clock = " o'clock"
	else:
		o_clock = ""

	return "It's %s %s%s%s" % (about_message[minute % 5],
				   section_name[minute / 5],
				   hour_name(hour), o_clock)

def str_time(hour = None, min = None):
	if hour == None:
		t = time.localtime(time.time())
		year, month, day, hour, min, second, weekday, julian, dst = t

	h = hour % 12
	if h == 0:
		h = 12
	if hour < 12:
		am = 'am'
	else:
		am = 'pm'
	return '%s:%02d %s' % (h, min, am)
