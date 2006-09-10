# Copyright (C) 2006, Thomas Leonard

import sys

# See http://www.galago-project.org/specs/notification/

_avail = None	# Unknown
notification_service = None

_nid_to_memo = {}

CRITICAL = 2

def _NotificationClosed(nid, *unused):
	if nid in _nid_to_memo:
		del _nid_to_memo[nid]
		#print "Closed"

def _ActionInvoked(nid, action):
	memo = _nid_to_memo.get(nid, None)
	if memo:
		if action == 'edit':
			from EditBox import EditBox
			EditBox(memo).show()
		elif action == 'hide':
			from __main__ import memo_list
			memo_list.set_hidden(memo, 1)
		elif action == 'ok':
			pass
		else:
			raise Exception('Unknown action "%s"' % action)

def is_available():
	global _avail, notification_service
	if _avail is not None: return _avail

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

		notification_service.connect_to_signal('NotificationClosed', _NotificationClosed)
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

def notify(memo):
	import time
	import dbus.types
	assert _avail

	close(memo)

	id = notification_service.Notify('Memo',
		0,		# replaces_id,
		'',		# icon
		memo.message.split('\n', 1)[0].strip(),	# summary
		_('Alarm set for %s:\n%s') % (time.ctime(memo.time), memo.message),
		[
			'hide', 'Hide memo',
			'edit', 'Edit',
			'ok', 'OK',
		],
		{'urgency': dbus.types.Byte(CRITICAL)},
		0)		# timeout
	
	_nid_to_memo[id] = memo

if __name__ == '__main__':
	__builtins__._ = lambda x: x
	from Memo import Memo
	assert is_available()
	notify(Memo(0, 'This is a message.\nMore details go here.', True))
	from rox import g
	g.main()
