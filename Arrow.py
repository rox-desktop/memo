from gtk import *
from GDK import *

class Arrow(GtkEventBox):
	def __init__(self, arrow_type, callback, data, time = 50):
		GtkEventBox.__init__(self)
		self.add_events(BUTTON_PRESS_MASK)

		self.data = data
		self.callback = callback
		self.arrow_type = arrow_type
		self.time = time

		self.arrow = GtkArrow()
		self.arrow.set(arrow_type, SHADOW_OUT)

		self.add(self.arrow)
		self.button = 0
		
		self.connect('button-press-event', self.button_press)
		self.connect('button-release-event', self.button_release)
	
	def button_press(self, box, event):
		if self.button != 0 or event.type != BUTTON_PRESS:
			return
		self.button = event.button
		grab_add(self)
		self.arrow.set(self.arrow_type, SHADOW_IN)
		self.cb = timeout_add(self.time * 2 + 300, self.incr)
		self.incr(resched = 0)
	
	def button_release(self, box, event):
		if self.button != event.button:
			return
		self.button = 0
		grab_remove(self)
		self.arrow.set(self.arrow_type, SHADOW_OUT)
		timeout_remove(self.cb)
	
	def incr(self, resched = 1):
		if resched:
			timeout_remove(self.cb)
			self.cb = timeout_add(self.time, self.incr)
		self.callback(self.data)
		return 0
