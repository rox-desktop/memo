from gtk import *
from memos import *

menu = GtkMenu()

item = GtkMenuItem("Add memo")
item.connect("activate", lambda w: new_memo())
menu.append(item)

item = GtkMenuItem("Quit")
item.connect("activate", mainquit)
menu.append(item)

menu.show_all()

def show_menu(event, item = None):
	menu.popup(None, None, None, event.button, event.time)
