from gtk import *
import _gtk
import time

day_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
	    "Saturday", "Sunday"]

month_name = ["January", "February", "March", "April",
	      "May", "June", "July", "August",
	      "September", "October", "November", "December"]

about_message = ["nearly", "nearly", "about", "just gone", "just gone"]

section_name = ["", "five past ", "ten past ", "a quarter past ",
	        "twenty past ", "twenty-five past ", "half past ",
		"twenty-five to ", "twenty to ", "a quarter to ",
		"ten to ", "five to "]

number = [None, "one", "two", "three", "four", "five", "six", "seven", "eight",
	  "nine", "ten", "eleven"]

def hour_name(hour):
	if hour == 0:
		return "midnight"
	elif hour == 12:
		return "noon"
	return number[hour % 12]

def th(n):
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

class TimeDisplay(GtkLabel):
	def __init__(self):
		GtkLabel.__init__(self)
		self.update()
		_gtk.gtk_timeout_add(30000, self.update)
		self.set_padding(8, 2)
	
	def update(self):
		t = time.localtime(time.time() + 150)
		year, month, day, hour, minute, second,	weekday, julian, dst = t

		off = about_message[minute % 5]

		if minute / 5 > 6:
			hour = (hour + 1) % 24

		if minute / 5 == 0 and hour != 0 and hour != 12:
			o_clock = " o'clock"
		else:
			o_clock = ""

		self.set_text("It's %s %s%s%s" % \
			(about_message[minute % 5],
			 section_name[minute / 5],
			 hour_name(hour),
			 o_clock))
		return TRUE
