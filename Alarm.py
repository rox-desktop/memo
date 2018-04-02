from gi.repository import Gtk
import rox
import time
from Memo import Memo

HIDE = 1
EDIT = 2


class Alarm(Gtk.MessageDialog):
    def __init__(self, memo):
        Gtk.MessageDialog.__init__(self, None, Gtk.DIALOG_MODAL,
                                 Gtk.MESSAGE_INFO, Gtk.BUTTONS_NONE,
                                 _('Alarm set for %s:\n%s') %
                                 (time.ctime(memo.time), memo.message))

        now = time.time()
        delay = memo.time - now
        earlyAlert = delay > 0

        button = rox.ButtonMixed(Gtk.STOCK_ZOOM_OUT, _('_Hide memo'))
        button.set_flags(Gtk.CAN_DEFAULT)
        self.add_action_widget(button, HIDE)
        button.show()

        button = rox.ButtonMixed(Gtk.STOCK_PROPERTIES, _('_Edit'))
        button.set_flags(Gtk.CAN_DEFAULT)
        self.add_action_widget(button, EDIT)
        button.show()

        self.add_button(Gtk.STOCK_OK, Gtk.RESPONSE_OK)

        self.set_title('Memo:')
        self.set_modal(True)
        self.set_position(Gtk.WIN_POS_CENTER)

        if earlyAlert:
            memo.state = Memo.EARLY
        else:
            memo.state = Memo.DONE

        from main import memo_list
        memo_list.notify_changed()

        self.memo = memo

        self.connect('response', self.response)
        self.set_default_response(Gtk.RESPONSE_OK)

    def response(self, widget, response):
        if response == int(Gtk.RESPONSE_OK):
            pass
        elif response == HIDE:
            from main import memo_list
            memo_list.set_hidden(self.memo, 1)
        elif response == EDIT:
            from EditBox import EditBox
            EditBox(self.memo).show()
        elif response == int(Gtk.RESPONSE_DELETE_EVENT):
            return
        else:
            print("Unknown response", response)
            return
        self.destroy()
