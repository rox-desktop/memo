from gi.repository import GObject
import time

from pretty_time import month_name, str_time


def memo_from_node(node):
    assert node.localName == 'memo'

    def flag(attr):
        v = node.getAttribute(attr)
        if v == 'True':
            return True
        if v == 'False':
            return False
        try:
            return bool(int(v))
        except:
            return 0

    state = node.getAttribute('state')
    if state is None or state == "":
        if flag('silent'):
            state = Memo.DONE
        else:
            state = Memo.READY
    time, = node.getElementsByTagName('time')
    message, = node.getElementsByTagName('message')
    nosound = False
    soundfile = None
    soundnode = node.getElementsByTagName('sound')
    if len(soundnode) == 1:
        if len(soundnode[0].childNodes) == 1:
            soundfile = soundnode[0].childNodes[0].nodeValue
        if soundnode[0].hasAttribute('disabled'):
            nosound = True

    message = ''.join([n.nodeValue for n in message.childNodes])

    return Memo(float(time.childNodes[0].nodeValue),
                message, flag('at'), state, flag('hidden'), soundfile, nosound)


class Memo(GObject.GObject):

    # Constants for memo 'state' attribute:
    READY = 'ready'
    EARLY = 'early'
    DONE = 'done'

    # 'time' is seconds since epoch
    # 'at' is TRUE if the time of day matters
    def __init__(self, time, message, at, state=READY, hidden=0,
                 soundfile=None, nosound=False):
        super().__init__()

        assert at == 0 or at == 1
        assert state == Memo.READY or state == Memo.EARLY or state == Memo.DONE
        assert hidden == 0 or hidden == 1

        self.time = int(time)
        self.message = message.strip()
        self.at = at
        self.state = state
        self.hidden = hidden
        self.brief = self.message.split('\n', 1)[0]
        self.soundfile = soundfile
        self.nosound = nosound

    def str_when(self):
        now_y, now_m, now_d = time.localtime(time.time() + 5 * 60)[:3]
        now_m = now_m - 1

        year, month, day, hour, min = time.localtime(self.time)[:5]
        month = month - 1

        if year != now_y:
            return '%s-%d' % (month_name[month][:3], year)

        if month != now_m or day != now_d:
            return '%02d-%s' % (day, month_name[month][:3])

        if self.at:
            return str_time(hour, min)

        return _('Today')

    def comes_after(self, other):
        return self.time > other.time

    def save(self, parent):
        doc = parent.ownerDocument

        node = doc.createElement('memo')
        node.setAttribute('at', str(self.at))
        node.setAttribute('state', self.state)
        node.setAttribute('hidden', str(self.hidden))
        parent.appendChild(node)

        time = doc.createElement('time')
        time.appendChild(doc.createTextNode(str(self.time)))
        node.appendChild(time)

        message = doc.createElement('message')
        message.appendChild(doc.createTextNode(self.message))
        node.appendChild(message)

        if self.nosound or (self.soundfile is not None and self.soundfile != ""):
            sound = doc.createElement('sound')
            if self.nosound:
                sound.setAttribute('disabled', "True")
            else:
                sound.appendChild(doc.createTextNode(self.soundfile))
            node.appendChild(sound)

    def set_hidden(self, hidden):
        assert hidden == 0 or hidden == 1

        self.hidden = hidden
