# Most of the common code needed by ROX applications is in ROX-Lib3.
# Except this code, which is needed to find ROX-Lib3 in the first place!

# Just make sure you run findrox.version() before importing anything inside
# ROX-Lib3...

import os
import sys
from os.path import exists
import string


def version(major, minor, micro):
    """Find ROX-Lib3, with a version >= (major, minor, micro), and
    add it to sys.path. If version is missing or too old, either
    prompt the user, or (if possible) upgrade it automatically.
    If 'rox' is already in PYTHONPATH, just use that (assume the injector
    is being used)."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rox-lib', 'ROX-Lib3', 'python'))
    try:
        import rox
    except ImportError:
        pass
    else:
        # print "Using ROX-Lib in PYTHONPATH"
        if (major, minor, micro) > rox.roxlib_version:
            print("WARNING: ROX-Lib version "
                  "%d.%d.%d requested, but using version "
                  "%d.%d.%d from %s" %
                  (major, minor, micro,
                   rox.roxlib_version[0],
                   rox.roxlib_version[1],
                   rox.roxlib_version[2],
                   rox.__file__), file=sys.stderr)
        return

    if not os.getenv('ROXLIB_DISABLE_ZEROINSTALL') and os.path.exists('/uri/0install/rox.sourceforge.net'):
        # We're using ZeroInstall. Good :-)
        zpath = '/uri/0install/rox.sourceforge.net/lib/ROX-Lib3/' \
                'latest-2'
        if not os.path.exists(zpath):
            os.system('0refresh rox.sourceforge.net')
            assert os.path.exists(zpath)
        vs = os.readlink(zpath).split('-')[-1]
        v = tuple(map(int, vs.split('.')))
        if v < (major, minor, micro):
            if os.system('0refresh rox.sourceforge.net'):
                report_error(
                    'Using ROX-Lib in Zero Install, but cached version (%s) is too old (need %d.%d.%d) and updating failed (is zero-install running?)' % (vs, major, minor, micro))
        sys.path.append(zpath + '/python')
        return
    try:
        path = os.environ['LIBDIRPATH']
        paths = string.split(path, ':')
    except KeyError:
        paths = [os.environ['HOME'] + '/lib',
                 '/usr/local/lib', '/usr/lib']

    for p in paths:
        p = os.path.join(p, 'ROX-Lib3')
        if exists(p):
            # TODO: check version is new enough
            sys.path.append(os.path.join(p, 'python'))
            import rox
            if major == 1 and minor == 9 and micro < 10:
                return  # Can't check version
            if not hasattr(rox, 'roxlib_version'):
                break
            if (major, minor, micro) <= rox.roxlib_version:
                return  # OK
    report_error("This program needs ROX-Lib3 (version %d.%d.%d) " %
                 (major, minor, micro) + "to run.\n" +
                 "I tried all of these places:\n\n" +
                 string.join(paths, '\n') + '\n\n' +
                 "ROX-Lib3 is available from:\n" +
                 "http://rox.sourceforge.net")


def report_error(err):
    "Write 'error' to stderr and, if possible, display a dialog box too."
    try:
        sys.stderr.write('*** ' + err + '\n')
    except:
        pass
    try:
        import pygtk
        pygtk.require('2.0')
        import gtk
        g = gtk
    except:
        import gtk
        win = gtk.GtkDialog()
        message = gtk.GtkLabel(err +
                               '\n\nAlso, pygtk2 needs to be present')
        win.set_title('Missing ROX-Lib3')
        win.set_position(gtk.WIN_POS_CENTER)
        message.set_padding(20, 20)
        win.vbox.pack_start(message)

        ok = gtk.GtkButton("OK")
        ok.set_flags(gtk.CAN_DEFAULT)
        win.action_area.pack_start(ok)
        ok.connect('clicked', gtk.mainquit)
        ok.grab_default()

        win.connect('destroy', gtk.mainquit)
        win.show_all()
        gtk.mainloop()
    else:
        box = g.MessageDialog(None, g.MESSAGE_ERROR, 0,
                              g.BUTTONS_OK, err)
        box.set_title('Missing ROX-Lib3')
        box.set_position(g.WIN_POS_CENTER)
        box.set_default_response(g.RESPONSE_OK)
        box.run()
    sys.exit(1)
