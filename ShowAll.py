import rox
from rox import g, TRUE, FALSE

from main import memo_list
import pretty_time
import time
import memos


class ShowAll(g.Dialog):
    def __init__(self):
        g.Dialog.__init__(self)
        self.set_title(_('All memos'))
        self.set_has_separator(FALSE)

        self.add_button(g.STOCK_CLOSE, g.RESPONSE_CANCEL)

        frame = g.Frame()
        self.vbox.pack_start(frame, TRUE, TRUE, 0)
        frame.set_shadow_type(g.SHADOW_IN)

        hbox = g.HBox(FALSE, 0)
        frame.add(hbox)

        scroll = g.VScrollbar()
        hbox.pack_end(scroll, FALSE, TRUE, 0)

        self.list = g.TreeView(memo_list)
        hbox.pack_start(self.list, TRUE, TRUE, 0)
        self.list.set_scroll_adjustments(None, scroll.get_adjustment())
        self.list.set_size_request(-1, 12)
        self.set_default_size(-1, 300)

        text = g.CellRendererText()

        toggle = g.CellRendererToggle()
        column = g.TreeViewColumn(_('Hide'), toggle,
                                  active=memos.HIDDEN)
        self.list.append_column(column)
        toggle.connect('toggled',
                       lambda t, path: memo_list.toggle_hidden(path))

        column = g.TreeViewColumn(_('Time'), text, text=memos.TIME)
        self.list.append_column(column)

        column = g.TreeViewColumn(_('Message'), text, text=memos.BRIEF)
        self.list.append_column(column)

        self.list.set_headers_visible(TRUE)

        sel = self.list.get_selection()
        sel.set_mode(g.SELECTION_MULTIPLE)

        def activate(view, path, column):
            memo = memo_list.get_memo_by_path(path)
            from EditBox import EditBox
            EditBox(memo).show()

        self.add_events(g.gdk.BUTTON_PRESS_MASK)
        self.list.connect('row-activated', activate)

        self.connect('response', self.response)

        self.set_default_response(g.RESPONSE_CANCEL)

        actions = g.HButtonBox()
        self.vbox.pack_start(actions, FALSE, TRUE, 0)
        actions.set_layout(g.BUTTONBOX_END)
        actions.set_border_width(5)
        actions.set_spacing(4)

        def new(b):
            from EditBox import EditBox
            EditBox().show()
        button = g.Button(stock=g.STOCK_NEW)
        actions.add(button)
        button.connect('clicked', new)

        def delete(b):
            sel = self.list.get_selection()
            memos = []
            for iter in memo_list:
                if sel.iter_is_selected(iter):
                    m = memo_list.get_memo_by_iter(iter)
                    memos.append(m)
            if not memos:
                rox.alert(_('You need to select some memos first!'))
                return
            l = len(memos)
            if l == 1:
                message = _("Really delete memo '%s'?") % memos[0].brief
            else:
                message = _('Really delete %d memos?') % l

            box = g.MessageDialog(None, 0, g.MESSAGE_QUESTION,
                                  g.BUTTONS_CANCEL, message)

            if rox.confirm(message, g.STOCK_DELETE):
                for m in memos:
                    memo_list.delete(m, update=0)
                memo_list.notify_changed()
        button = g.Button(stock=g.STOCK_DELETE)
        actions.add(button)
        button.connect('clicked', delete)

        def edit(b):
            sel = self.list.get_selection()
            memos = []
            for iter in memo_list:
                if sel.iter_is_selected(iter):
                    m = memo_list.get_memo_by_iter(iter)
                    memos.append(m)
            if len(memos) != 1:
                rox.alert(_('You need to select exactly one memo first!'))
                return
            from EditBox import EditBox
            EditBox(memos[0]).show()
        button = rox.ButtonMixed(g.STOCK_PROPERTIES, _('_Edit'))
        actions.add(button)
        button.connect('clicked', edit)

        self.show_all()

    def response(self, box, response):
        if response == int(g.RESPONSE_CANCEL):
            self.destroy()
