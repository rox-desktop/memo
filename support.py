from rox.MultipleChoice import MultipleChoice

# Open a modal dialog box showing a message.
# The user can choose from a selection of buttons at the bottom.
# Returns -1 if the window is destroyed, or the number of the button
# if one is clicked (starting from zero).
#
# If a dialog is already open, returns -1 without waiting AND
# brings the current dialog to the front.
current_dialog = None
def get_choice(message, title, buttons):
	global current_dialog

	if current_dialog:
		current_dialog.hide()
		current_dialog.show()
		return -1

	current_dialog = MultipleChoice(message, buttons)
	current_dialog.set_title(title)
	choice_return = current_dialog.wait()

	current_dialog = None

	return choice_return

def str_time(hour, min):
	h = hour % 12
	if h == 0:
		h = 12
	if hour < 12:
		am = 'am'
	else:
		am = 'pm'
	return '%s:%02d %s' % (h, min, am)
