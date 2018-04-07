from gi.repository import Gtk
import rox
from rox.Menu import Menu

actionsMenu = [
    (_('/Add Memo...'), 'new_memo', "<StockItem>", "", Gtk.STOCK_ADD),
    (_('/Show All...'), 'show_all_memos', '<StockItem>', "", Gtk.STOCK_EDIT),
]

mainMenu = [
    (_('/Options...'),  'show_options', "<StockItem>", "", Gtk.STOCK_PREFERENCES),
    (_('/Help'),        'show_help',	"<StockItem>", "", Gtk.STOCK_HELP),
    (_('/Quit'),        'quit', "<StockItem>", "", Gtk.STOCK_QUIT),
]

SEPARATOR = ('/', '', '<Separator>')


class MenuWindow(object):
    def __init__(self, attach=True, full=True, additions=None):
        """Initializes the menu for this window.
        'full' decides whether the whole menu (actions and main) or just the
        actions menu is shown.
        'additions' is an optional dictionary as follows:
          { 'topActions':    [ Menu items to attach before the 'actions' menu ],
            'bottomActions': [ Menu items to attach after the 'actions' menu ],
                 'topMain':       [ Menu items to attach before the 'main' menu ],
                 'bottomMain':    [ Menu items to attach after the 'main' menu ] }
        """
        self.additions = {'topActions': [],
                          'bottomActions': [],
                          'topMain': [],
                          'bottomMain': []}
        self.menu = None
        self.show_all_box = None
        self.attach = attach
        self.full = full
        if additions is not None:
            self.addAdditions(additions)
        else:
            self.set_menu()

    def addAdditions(self, additions):
        changed = False
        for (key, lst) in list(self.additions.items()):
            if key in additions:
                changed = True
                lst.extend(additions[key])
        if changed:
            self.set_menu()

    def removeAdditions(self, additions):
        changed = False
        for (key, items) in list(self.additions.items()):
            if key in additions:
                toRemove = additions[key]
                for item in toRemove:
                    try:
                        items.remove(item)
                        changed = True
                    except ValueError:
                        # If they're not already in the list, that's okay
                        pass
        if changed:
            self.set_menu()

    def popup_menu(self, event, position=None):
        self.menu.popup(self, event, position)

    def set_menu(self, attach=None, full=None):
        if attach is not None:
            self.attach = attach

        if full is not None:
            self.full = full

        menuList = []
        menuName = 'actions'
        menuList.extend(self.additions['topActions'])
        menuList.extend(actionsMenu)
        menuList.extend(self.additions['bottomActions'])
        if self.full:
            menuName = 'main'
            menuList.append(SEPARATOR)
            menuList.extend(self.additions['topMain'])
            menuList.extend(mainMenu)
            menuList.extend(self.additions['bottomMain'])
        self.menu = Menu(menuName, menuList)
        if attach:
            self.menu.attach(self, self)

    def new_memo(self, widget=None):
        from EditBox import EditBox
        EditBox().show()

    def show_all_memos(self, widget=None):
        if self.show_all_box:
            self.show_all_box.present()
            return

        def destroyed(widget): self.show_all_box = None
        from ShowAll import ShowAll
        self.show_all_box = ShowAll()
        self.show_all_box.connect('destroy', destroyed)
        self.show_all_box.show()

    def show_options(self, widget=None):
        rox.edit_options()

    def show_help(self, widget=None):
        from rox import filer
        filer.open_dir(rox.app_dir + '/Help')

    def quit(self, widget=None):
        self.destroy()
