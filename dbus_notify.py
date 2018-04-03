# Copyright (C) 2006, Thomas Leonard

from gi.repository import Gtk
import sys
import rox
from Memo import Memo
from rox import options
from os import path

memo_soundfile = options.Option('memo_sound', "")
timer_soundfile = options.Option('timer_sound', "")

# See http://www.galago-project.org/specs/notification/

_avail = None  # Unknown
notification_service = None

_nid_to_memo = {}

LOW = 0
NORMAL = 1
CRITICAL = 2


def _NotificationClosed(nid, *unused):
    if nid in _nid_to_memo:
        del _nid_to_memo[nid]
        # print "Closed"


def _ActionInvoked(nid, action):
    try:
        memo = _nid_to_memo.get(nid, None)
        if memo:
            if action == 'edit':
                from EditBox import EditBox
                EditBox(memo).show()
            elif action == 'delete':
                from main import memo_list
                memo_list.delete(memo)
            elif action == 'hide':
                from main import memo_list
                memo_list.set_hidden(memo, 1)
            elif action in ('ok', 'default'):
                pass
            else:
                raise Exception('Unknown action "%s"' % action)
    except Exception:
        rox.report_exception()


def is_available():
    global _avail, notification_service
    if _avail is not None:
        return _avail

    try:
        import dbus
        import dbus.glib

        session_bus = dbus.SessionBus()

        remote_object = session_bus.get_object('org.freedesktop.Notifications',
                                               '/org/freedesktop/Notifications')

        notification_service = dbus.Interface(remote_object,
                                              'org.freedesktop.Notifications')

        # The Python bindings insist on printing a pointless introspection
        # warning to stderr if the service is missing. Force it to be done
        # now so we can skip it
        old_stderr = sys.stderr
        sys.stderr = None
        try:
            notification_service.GetCapabilities()
        finally:
            sys.stderr = old_stderr

        notification_service.connect_to_signal(
            'NotificationClosed', _NotificationClosed)
        notification_service.connect_to_signal('ActionInvoked', _ActionInvoked)

        _avail = True
    except:
        _avail = False
    return _avail


def close(memo):
    # Used when the memo has been deleted (or changed)
    for nid in _nid_to_memo:
        if _nid_to_memo[nid] is memo:
            notification_service.CloseNotification(nid)


def close_all():
    for nid in _nid_to_memo:
        notification_service.CloseNotification(nid)


def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')


def notify(memo):
    import time
    import dbus.types
    assert _avail

    close(memo)

    now = time.time()
    delay = memo.time - now
    earlyAlert = delay > 0

    parts = memo.message.split('\n', 1)
    summary = escape(parts[0])
    body = '<i>' + (_('Alarm set for %s') % time.ctime(memo.time)) + '</i>'
    if len(parts) == 2:
        body += '\n' + escape(parts[1])

    hints = {}
    if earlyAlert:
        okText = "Later"
        hints['urgency'] = dbus.types.Byte(NORMAL)
    else:
        okText = "Ok"
        hints['urgency'] = dbus.types.Byte(CRITICAL)

    if memo.nosound:
        hints['suppress-sound'] = dbus.types.Boolean(True)
    elif memo.soundfile is not None and memo.soundfile != "":
        hints['suppress-sound'] = dbus.types.Boolean(False)
        hints['sound-file'] = dbus.types.String(memo.soundfile)
    elif memo_soundfile.value != "":
        hints['suppress-sound'] = dbus.types.Boolean(False)
        hints['sound-file'] = dbus.types.String(memo_soundfile.value)
    id = notification_service.Notify('Memo',
                                     0,		# replaces_id,
                                     path.join(
                                         rox.app_dir, ".DirIcon"),		# icon
                                     summary,
                                     body,
                                     [
                                         'hide', 'Hide memo',
                                         'delete', 'Delete',
                                         'edit', 'Edit',
                                         'ok', okText,
                                     ],
                                     hints,
                                     0)		# timeout

    _nid_to_memo[id] = memo

    if earlyAlert:
        memo.state = Memo.EARLY
    else:
        memo.state = Memo.DONE
    from main import memo_list
    memo_list.notify_changed()


def timer():
    import dbus.types
    assert _avail

    hints = {}
    hints['urgency'] = dbus.types.Byte(CRITICAL)
    if timer_soundfile.value != "":
        hints['sound-file'] = timer_soundfile.value

    notification_service.Notify('Memo',
                                0,		# replaces_id,
                                path.join(rox.app_dir, ".DirIcon"),		# icon
                                'Time is up!',
                                'The Memo timer you set has expired.',
                                [],
                                hints,
                                0)		# timeout


if __name__ == '__main__':
    __builtins__._ = lambda x: x
    assert is_available()
    notify(Memo(0, 'This is a <message>.\nMore <details> go <here>.', True))
    Gtk.main()
