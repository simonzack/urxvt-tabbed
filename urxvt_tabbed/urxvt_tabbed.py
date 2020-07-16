import signal
import subprocess

import Xlib.display
from gi.repository import Gdk, Gtk, Pango

from urxvt_tabbed.config import KeyPress
from urxvt_tabbed.gdk_events import GdkEvents
from urxvt_tabbed.tab_label import ClosableTabLabel

gdk_events = GdkEvents()


class UrxvtTabbedWindow(Gtk.Window):
    '''
    Wrapper around urxvt which adds tabs.
    '''

    def __init__(self, config):
        super().__init__(title='urxvt')

        # Config
        self.config = config
        self.close_last_tab_strategy = self.config['general']['close_last_tab']

        vbox = Gtk.VBox()
        self.add(vbox)

        # Tabs container
        notebook = Gtk.Notebook(name='notebook')
        notebook.set_can_focus(False)
        notebook.set_scrollable(True)
        vbox.pack_start(notebook, True, True, 0)
        self.notebook = notebook
        self.notebook.connect('page-removed', self.on_page_removed)
        self.notebook.connect('page-reordered', self.on_page_reordered)
        self.tabs = []

        css = b'''
        #notebook {
            border-width: 0px;
        }
        '''
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        context = Gtk.StyleContext()
        context.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # New tab button
        new_tab_button = Gtk.Button()
        new_tab_button.set_relief(Gtk.ReliefStyle.NONE)
        new_tab_button.add(Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU))
        new_tab_button.connect('clicked', self.on_new_tab_click)
        new_tab_button.show_all()
        notebook.set_action_widget(new_tab_button, Gtk.PackType.END)
        self.connect('delete_event', self.on_delete_event)
        signal.signal(signal.SIGINT, lambda signum, frame: self.on_delete_event(None, None))

        # Add new tab (otherwise the notebook won't appear)
        self.add_terminal()

        # Set window icon
        icon_info = Gtk.IconTheme.get_default().lookup_icon('utilities-terminal', 48, 0)
        if icon_info:
            self.set_icon(icon_info.load_icon())

        # Keyboard shortcuts
        self.connect('key-press-event', self.on_key_press)

        # Set default size for window
        self.config['ui']['default_size'](self)

    def add_terminal(self):
        font = Pango.FontDescription(self.config['ui']['font'])
        notebook = self.notebook
        urxvt_tab = UrxvtTab()
        urxvt_tab.label.label.modify_font(font)
        urxvt_tab.label.label_entry.modify_font(font)
        notebook.append_page(urxvt_tab.rxvt_socket, urxvt_tab.label)
        notebook.set_tab_reorderable(urxvt_tab.rxvt_socket, 1)
        urxvt_tab.rxvt_socket.show_all()
        notebook.set_current_page(notebook.page_num(urxvt_tab.rxvt_socket))
        self.tabs.append(urxvt_tab)

    def close_terminal(self, i):
        self.tabs[i].close()

    def on_new_tab_click(self, widget):
        self.add_terminal()

    def on_delete_event(self, widget, data):
        children = self.notebook.get_children()
        num_tabs = len(children)
        if num_tabs <= 1:
            # Close window if there's only a single tab
            self.close_last_tab_strategy = 'close'
            Gtk.main_quit()
        else:
            # Ask the user to close all tabs or not
            dialog = Gtk.MessageDialog(
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.QUESTION,
                message_format=f'You are about to close {num_tabs} tabs. Are you sure you want to continue?'
            )
            dialog.add_button('Close window', Gtk.ResponseType.OK)
            dialog.add_button('Cancel', Gtk.ResponseType.CANCEL)
            response_code = dialog.run()
            if response_code == Gtk.ResponseType.OK:
                self.close_last_tab_strategy = 'close'
                Gtk.main_quit()
            else:
                dialog.destroy()
                return True

    def on_key_press(self, label_entry, event):
        is_processed = True
        keymap = self.config['keymap']
        event_key = KeyPress.parse_event(event)
        if event_key == keymap['new_tab']:
            self.add_terminal()
        elif event_key == keymap['close_tab']:
            self.close_terminal(self.notebook.get_current_page())
        elif event_key == keymap['prev_tab']:
            # prev_page() doens't switch to the last tab on the first tab
            self.notebook.set_current_page((self.notebook.get_current_page()-1)%len(self.tabs))
        elif event_key == keymap['next_tab']:
            self.notebook.set_current_page((self.notebook.get_current_page()+1)%len(self.tabs))
        elif event_key == keymap['move_tab_prev']:
            old_page_num = self.notebook.get_current_page()
            new_page_num = (old_page_num-1)%len(self.tabs)
            self.notebook.reorder_child(self.tabs[old_page_num].rxvt_socket, new_page_num)
        elif event_key == keymap['move_tab_next']:
            old_page_num = self.notebook.get_current_page()
            new_page_num = (old_page_num+1)%len(self.tabs)
            self.notebook.reorder_child(self.tabs[old_page_num].rxvt_socket, new_page_num)
        elif event_key == keymap['edit_tab']:
            self.tabs[self.notebook.get_current_page()].label.label_edit_focus()
        else:
            for tab_index in range(10):
                if event_key == keymap[f'switch_to_tab_{tab_index + 1}']:
                    if len(self.tabs) > tab_index:
                        self.notebook.set_current_page(tab_index)
                    return is_processed
            is_processed = False

        return is_processed

    def on_page_removed(self, notebook, tab_widget, page_num):
        self.tabs.pop(page_num)
        # Check if there are any more terminals left
        if not self.tabs:
            if self.close_last_tab_strategy == 'blank':
                pass
            elif self.close_last_tab_strategy == 'new':
                self.add_terminal()
            elif self.close_last_tab_strategy == 'close':
                try:
                    # From gtk 3.10
                    self.close()
                except AttributeError:
                    self.emit('delete-event', Gdk.Event(Gdk.EventType.DELETE))

    def on_page_reordered(self, notebook, tab_widget, new_page_num):
        # gtk doesn't provide a way to get the old page num
        tabs = self.tabs
        old_page_num = next(i for i, tab in enumerate(tabs) if tab.rxvt_socket == tab_widget)
        tab = tabs.pop(old_page_num)
        tabs.insert(new_page_num, tab)


class UrxvtTab:
    RXVT_BASENAME = 'urxvt'

    def __init__(self, title='urxvt'):
        label = ClosableTabLabel(title)
        label.connect('close_clicked', self.on_new_tab_close_click)
        label.connect('label_edit_submit', self.on_label_edit_submit)
        label.connect('label_edit_blur', self.on_label_edit_blur)
        self.label = label
        # Embedded terminal
        rxvt_socket = Gtk.Socket()
        self.rxvt_socket = rxvt_socket
        rxvt_socket.set_can_focus(True)
        # pygobject has some strange bug where if self is directory used then self fields won't exist
        rxvt_socket.connect_after('realize', lambda *args, **kwargs: self.on_realize(*args, **kwargs))
        rxvt_socket.connect_after('plug_added', lambda *args, **kwargs: self.on_plug_added(*args, **kwargs))
        rxvt_socket.connect_after('map_event', lambda *args, **kwargs: self.on_map_event(*args, **kwargs))
        self.event_listener_id = None
        self.plugged = None
        self.terminal_process = None
        # Tab labels
        self.shell_title = title
        self.has_custom_title = False
        self.closed = False

    def update_tab_geometry_hints(self):
        '''
        Copy the WM_NORMAL_HINTS properties of rxvt window to the rxvt tab so it stays within the rxvt resizing
        requirements. Resizing might not be smooth anymore if this is called.
        '''
        rxvt_socket = self.rxvt_socket
        display = Xlib.display.Display()
        xlib_window = display.create_resource_object('window', self.plugged.get_xid())
        hints = xlib_window.get_wm_normal_hints()
        geometry = Gdk.Geometry()
        geometry.base_width = hints.base_width
        geometry.base_height = hints.base_height
        geometry.width_inc = hints.width_inc
        geometry.height_inc = hints.height_inc
        geom_mask = Gdk.WindowHints(0)
        geom_mask |= Gdk.WindowHints.BASE_SIZE
        geom_mask |= Gdk.WindowHints.RESIZE_INC
        rxvt_socket.get_toplevel().set_geometry_hints(rxvt_socket, geometry, geom_mask)

    def on_realize(self, rxvt_socket):
        '''
        Creates a urxvt instance and embed it in widget.
        '''
        xid = rxvt_socket.get_window().get_xid()
        self.terminal_process = subprocess.Popen([self.RXVT_BASENAME, '-embed', str(xid)])
        return False

    def on_map_event(self, rxvt_socket, event):
        rxvt_socket.grab_focus()
        return False

    def on_plug_added(self, rxvt_socket):
        '''
        Runs when the urxvt embedded process attaches a plug to the socket specified by the xid (passed to it as a
        command-line argument).
        '''
        plugged = rxvt_socket.get_plug_window()
        if plugged is None:
            return
        self.plugged = plugged
        self.update_tab_geometry_hints()
        # Listen to gdk property change events
        plugged.set_events(plugged.get_events()|Gdk.EventMask.PROPERTY_CHANGE_MASK)
        # urxvt only uses x.org, so only gdk events can be used
        self.event_listener_id = gdk_events.add_event_listener(self.on_gdk_event)
        return False

    def shell_set_title(self, title):
        if not self.has_custom_title:
            self.label.set_text(title)

    def user_set_title(self, title):
        # Only use the user specified label if it isn't empty
        if title:
            self.has_custom_title = True
            self.label.set_text(title)
        else:
            self.has_custom_title = False
            self.label.set_text(self.shell_title)

    def on_gdk_event(self, event):
        '''
        Events are also created when the urxvt plugged window closes, this handler disconnects itself when it
        recieves the event.
        '''
        try:
            if self.closed:
                return
            if event.type == Gdk.EventType.CONFIGURE:
                self.update_tab_geometry_hints()
            elif event.type == Gdk.EventType.PROPERTY_NOTIFY:
                if event.state == Gdk.PropertyState.NEW_VALUE:
                    if event.atom.name() == '_NET_WM_NAME':
                        # Window name change event, set tab title
                        display = Xlib.display.Display()
                        xlib_window = display.create_resource_object('window', self.plugged.get_xid())
                        title = xlib_window.get_wm_name()
                        self.shell_title = title
                        self.shell_set_title(title)
        except Xlib.error.BadWindow:
            # The plug window has now closed itself (there are no events indicating this, so catch the exception
            # instead)
            gdk_events.remove_event_listener(self.event_listener_id)
            self.close()

    def on_label_edit_blur(self, label):
        self.rxvt_socket.grab_focus()

    def on_label_edit_submit(self, label):
        self.user_set_title(self.label.get_text())

    def close(self):
        try:
            self.closed = True
            # This detaches the gdk event listener as well, see docs for on_gdk_event()
            self.terminal_process.send_signal(signal.SIGINT)
            # Call wait() so there's no defunct process
            self.terminal_process.wait()
        except OSError:
            pass

    def on_new_tab_close_click(self, widget):
        self.close()
