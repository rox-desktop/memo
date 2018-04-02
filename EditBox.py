from gi.repository import Gtk
import rox
import time

from Arrow import Arrow
from Memo import Memo
from main import memo_list

from pretty_time import str_time

DELETE = 1
HIDE = 2

refleak_bug_workaround = []


class EditBox(Gtk.Dialog):
    def __init__(self, memo=None):
        Gtk.Dialog.__init__(self)
        #self.set_has_separator(False)

        self.add_button(Gtk.STOCK_HELP, Gtk.ResponseType.HELP)

        if memo:
            self.add_button(Gtk.STOCK_DELETE, DELETE)

            button = rox.ButtonMixed(Gtk.STOCK_ZOOM_OUT, _('_Hide'))
            button.set_can_default(True)
            self.add_action_widget(button, HIDE)

        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

        button = rox.ButtonMixed(Gtk.STOCK_YES, _('_Set'))
        button.set_can_default(True)
        self.add_action_widget(button, Gtk.ResponseType.YES)

        self.memo = memo
        if memo:
            self.set_title(_("Edit memo:"))
            t = time.localtime(memo.time)
        else:
            self.set_title(_("Create memo:"))
            t = time.localtime(time.time() + 5 * 60)

        year, month, day, hour, minute, second,	weekday, julian, dst = t
        self.hour = hour
        self.min = minute

        self.cal = Gtk.Calendar()
        self.cal.select_month(month - 1, year)
        self.cal.select_day(day)

        at_box = self.make_at_box()
        self.advanced_box = self.make_advanced_box()

        text_frame = self.make_text_view()

        # Time/Date on the left, Text on the right
        hbox = Gtk.HBox(False, 0)
        self.vbox.pack_start(hbox, True, True, 0)

        self.vbox.pack_start(self.advanced_box, False, True, 0)

        # Date above time
        vbox = Gtk.VBox(False, 0)
        hbox.pack_start(vbox, False, True, 0)
        vbox.set_border_width(4)
        vbox.pack_start(self.cal, False, True, 0)

        spacer = Gtk.Alignment()
        vbox.pack_start(spacer, False, True, 2)

        vbox.pack_start(at_box, False, True, 0)

        hbox.pack_start(text_frame, True, True, 0)

        self.vbox.show_all()

        if memo:
            buffer = self.text.get_buffer()
            try:
                buffer.insert_at_cursor(memo.message)
            except TypeError:
                buffer.insert_at_cursor(memo.message, -1)
        if memo and memo.at:
            self.at.set_active(True)
            self.at.set_label(_('At'))
            self.advanced_box.set_sensitive(True)
        if memo == None or memo.at == 0:
            self.at_box.hide()
            self.at.set_label(_('At') + "...")
            self.advanced_box.set_sensitive(False)
        if memo:
            if memo.nosound:
                self.sound_choice.set_active(2)
            elif memo.soundfile is not None and memo.soundfile != "":
                self.sound_choice.set_active(1)
                self.sound_entry.set_filename(memo.soundfile)
                self.sound_entry.set_sensitive(True)
            else:
                self.sound_choice.set_active(0)

        self.connect('response', self.response)
        self.text.grab_focus()
        self.set_default_response(Gtk.ResponseType.YES)

        self.connect('destroy', lambda w: refleak_bug_workaround.remove(self))
        refleak_bug_workaround.append(self)

    def make_text_view(self):
        # The TextView / time of day settings
        vbox = Gtk.VBox(False, 0)
        l = Gtk.Label(_('Message:'))
        l.set_alignment(0, 1)
        l.set_padding(0, 4)
        vbox.pack_start(l, False, True, 0)

        frame = Gtk.Frame()
        vbox.pack_start(frame, True, True, 0)
        frame.set_shadow_type(Gtk.ShadowType.IN)

        hbox = Gtk.HBox(False, 0)
        frame.add(hbox)

        text = Gtk.TextView()
        hbox.pack_start(text, True, True, 0)
        text.set_wrap_mode(Gtk.WrapMode.WORD)

        scrollbar = Gtk.VScrollbar()
        adj = scrollbar.get_adjustment()
        # FIXME
        #text.set_scroll_adjustments(None, adj)
        hbox.pack_start(scrollbar, False, True, 0)

        text.set_size_request(200, 200)

        self.text = text

        return vbox

    def make_at_box(self):
        # The time of day setting
        hbox = Gtk.HBox(False, 0)

        self.at = Gtk.CheckButton(_('At'))
        hbox.pack_start(self.at, False, True, 4)
        self.at.connect('toggled', self.at_toggled)

        at_box = Gtk.HBox(False, 0)
        self.at_box = at_box
        hbox.pack_start(at_box, False, True, 0)

        arrow = Arrow(Gtk.ArrowType.LEFT, self.adj_time, -60)
        at_box.pack_start(arrow, False, True, 0)
        arrow = Arrow(Gtk.ArrowType.RIGHT, self.adj_time, 60)
        at_box.pack_start(arrow, False, True, 0)

        self.time_display = Gtk.Label(str_time(self.hour, self.min))
        self.time_display.set_padding(4, 0)
        frame = Gtk.Frame()
        frame.add(self.time_display)
        at_box.pack_start(frame, False, True, 0)

        arrow = Arrow(Gtk.ArrowType.LEFT, self.adj_time, -1)
        at_box.pack_start(arrow, False, True, 0)
        arrow = Arrow(Gtk.ArrowType.RIGHT, self.adj_time, 1)
        at_box.pack_start(arrow, False, True, 0)

        return hbox

    def make_advanced_box(self):
        # The advanced settings
        expander = Gtk.Expander(label=_('Advanced Options'))
        expandvbox = Gtk.VBox(False, 4)
        expander.add(expandvbox)

        sound_frame = Gtk.Frame(label=_('Sound'))
        # sound_frame.set_shadow_type(Gtk.SHADOW_NONE)
        label_widget = sound_frame.get_label_widget()
        label_widget.set_markup('<b>' + _('Sound') + '</b>')

        expandvbox.pack_start(sound_frame, False, True, 0)

        sound_box = Gtk.HBox(False, 4)
        sound_box.set_border_width(8)
        sound_frame.add(sound_box)

        sound_choice = Gtk.ComboBoxText()
        self.sound_choice = sound_choice
        sound_choice.append_text(_('Use default sound'))
        sound_choice.append_text(_('Use custom sound'))
        sound_choice.append_text(_('Disabled'))
        sound_choice.set_active(0)
        sound_box.pack_start(sound_choice, False, False, 0)

        #sound_entry = Gtk.Entry()
        sound_entry = Gtk.FileChooserButton('Sound File')
        self.sound_entry = sound_entry
        sound_entry.set_sensitive(False)
        sound_box.pack_start(sound_entry, True, True, 0)

        sound_choice.connect('changed', self.sound_choice_changed)

        # TODO: More advanced options can be added to the 'expandbox' vbox, each
        # in its own frame.

        return expander

    def response(self, widget, response):
        try:
            if response == DELETE:
                memo_list.delete(self.memo)
            elif response == HIDE:
                self.add(hide=1)
            elif response == int(Gtk.ResponseType.YES):
                self.add()
            elif response == int(Gtk.ResponseType.HELP):
                from rox import filer
                filer.open_dir(rox.app_dir + '/Help')
                return
            elif response == int(Gtk.ResponseType.CANCEL):
                pass
            elif response == int(Gtk.ResponseType.DELETE_EVENT):
                return
            else:
                raise Exception("Unknown response: %d" % response)
        except:
            rox.report_exception()
        self.destroy()

    def add(self, hide=0):
        (y, m, d) = self.cal.get_date()
        t = time.mktime((y, m + 1, d, self.hour, self.min,
                         0, -1, -1, -1))
        at = self.at_box.is_visible()
        buffer = self.text.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        message = buffer.get_text(start, end, True)
        soundval = self.sound_choice.get_active()
        if soundval == 2:  # Sound disabled
            sfile = None
            senabled = True
        elif soundval == 1:  # Custom sound
            sfile = self.sound_entry.get_filename()
            senabled = False
        else:  # Default sound
            sfile = None
            senabled = False
        memo = Memo(t, message, at=at != 0, hidden=hide,
                    soundfile=sfile, nosound=senabled)
        if self.memo:
            memo_list.delete(self.memo, update=0)
        memo_list.add(memo)
        memo_list.warn_if_not_visible(memo)

    def adj_time(self, increment):
        min = self.min + increment
        if min < 0 and self.hour == 0:
            return
        if min > 59 and self.hour == 23:
            return
        if min < 0:
            min = min + 60
            self.hour = self.hour - 1
        if min > 59:
            min = min - 60
            self.hour = self.hour + 1
        self.min = min
        self.time_display.set_text(str_time(self.hour, self.min))

    def at_toggled(self, at):
        if at.get_active():
            self.at_box.show()
            self.at.set_label(_('At'))
            self.advanced_box.set_sensitive(True)
        else:
            self.at_box.hide()
            self.at.set_label(_('At') + "...")
            self.advanced_box.set_sensitive(False)

    def sound_choice_changed(self, choice):
        value = choice.get_active()
        self.sound_entry.set_sensitive(value == 1)
