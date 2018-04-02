from gi.repository import Gtk, Gdk
import rox

from main import memo_list
import pretty_time
import time
import memos


class ShowAll(Gtk.Dialog):
    def __init__(self):
        Gtk.Dialog.__init__(self)
        self.set_title(_('All memos'))
        #self.set_has_separator(False)

        self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CANCEL)

        frame = Gtk.Frame()
        self.vbox.pack_start(frame, True, True, 0)
        frame.set_shadow_type(Gtk.ShadowType.IN)

        hbox = Gtk.HBox(False, 0)
        frame.add(hbox)

        scroll = Gtk.VScrollbar()
        hbox.pack_end(scroll, False, True, 0)

        self.list = Gtk.TreeView(memo_list)
        hbox.pack_start(self.list, True, True, 0)
        self.list.set_vadjustment(scroll.get_adjustment())
        self.list.set_size_request(-1, 12)
        self.set_default_size(-1, 300)

        text = Gtk.CellRendererText()

        toggle = Gtk.CellRendererToggle()
        column = Gtk.TreeViewColumn(_('Hide'), toggle,
                                  active=memos.HIDDEN)
        self.list.append_column(column)
        toggle.connect('toggled',
                       lambda t, path: memo_list.toggle_hidden(path))

        column = Gtk.TreeViewColumn(_('Time'), text, text=memos.TIME)
        self.list.append_column(column)

        column = Gtk.TreeViewColumn(_('Message'), text, text=memos.BRIEF)
        self.list.append_column(column)

        self.list.set_headers_visible(True)

        sel = self.list.get_selection()
        sel.set_mode(Gtk.SelectionMode.MULTIPLE)

        def activate(view, path, column):
            memo = memo_list.get_memo_by_path(path)
            from EditBox import EditBox
            EditBox(memo).show()

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.list.connect('row-activated', activate)

        self.connect('response', self.response)

        self.set_default_response(Gtk.ResponseType.CANCEL)

        actions = Gtk.HButtonBox()
        self.vbox.pack_start(actions, False, True, 0)
        actions.set_layout(Gtk.ButtonBoxStyle.END)
        actions.set_border_width(5)
        actions.set_spacing(4)

        def new(b):
            from EditBox import EditBox
            EditBox().show()
        button = Gtk.Button(stock=Gtk.STOCK_NEW)
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

            box = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION,
                                  Gtk.ButtonsType.CANCEL, message)

            if rox.confirm(message, Gtk.STOCK_DELETE):
                for m in memos:
                    memo_list.delete(m, update=0)
                memo_list.notify_changed()
        button = Gtk.Button(stock=Gtk.STOCK_DELETE)
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
        button = rox.ButtonMixed(Gtk.STOCK_PROPERTIES, _('_Edit'))
        actions.add(button)
        button.connect('clicked', edit)

        self.show_all()

    def response(self, box, response):
        if response == int(Gtk.ResponseType.CANCEL):
            self.destroy()
