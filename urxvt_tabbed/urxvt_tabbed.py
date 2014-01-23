
import subprocess
import signal
import Xlib
import Xlib.display
from gi.repository import Gtk, Gdk, GObject, GdkX11, Pango

from .gdk_events import GdkEvents
from .tab_label import ClosableTabLabel
from .config import KeyPress

gdk_events = GdkEvents()

def is_key_pressed(key, event_key):
	#ignore num_lock (Gdk.ModifierType.MOD2_MASK)
	return event_key.key == key.key and event_key.modifier_flags&(~Gdk.ModifierType.MOD2_MASK) == key.modifier_flags

class UrxvtTabbedWindow(Gtk.Window):
	'''
	Wrapper around urxvt which adds tabs
	the Gtk2::URxvt perl module doesn't seem to be available yet
	'''

	def __init__(self, config):
		super().__init__(title='urxvt')

		#config
		self.config = config

		vbox = Gtk.VBox()
		self.add(vbox)

		#tabs container
		notebook = Gtk.Notebook()
		notebook.set_can_focus(False)
		notebook.set_scrollable(True)
		vbox.pack_start(notebook, True, True, 0)
		self.notebook = notebook
		self.notebook.connect('page-removed', self.on_page_removed)
		self.notebook.connect('page-reordered', self.on_page_reordered)
		self.tabs = []

		#new tab button
		new_tab_button = Gtk.Button()
		new_tab_button.set_relief(Gtk.ReliefStyle.NONE)
		new_tab_button.add(Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.MENU))
		new_tab_button.connect('clicked', self.on_new_tab_click)
		new_tab_button.show_all()
		notebook.set_action_widget(new_tab_button, Gtk.PackType.END)
		self.connect('delete_event', self.on_delete_event)

		#add new tab (otherwise the notebook won't appear)
		self.add_terminal()

		#set window icon
		icon_info = Gtk.IconTheme.get_default().lookup_icon('terminal', 48, 0)
		if icon_info:
			self.set_icon(icon_info.load_icon())

		#keyboard shortcuts
		self.connect('key-press-event', self.on_key_press)

	def add_terminal(self):
		config = self.config
		notebook = self.notebook
		urxvt_tab = UrxvtTab()
		urxvt_tab.label.label.modify_font(Pango.FontDescription(config['ui']['font']))
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
			#close window if there's only a single tab
			Gtk.main_quit()
		else:
			#ask the user to close all tabs or not
			dialog = Gtk.MessageDialog(
				flags=Gtk.DialogFlags.MODAL,
				type=Gtk.MessageType.QUESTION,
				message_format='You are about to close {} tabs. Are you sure you want to continue?'.format(num_tabs)
			)
			dialog.add_button('Close window', Gtk.ResponseType.OK)
			dialog.add_button('Cancel', Gtk.ResponseType.CANCEL)
			response_code = dialog.run()
			if response_code == Gtk.ResponseType.OK:
				Gtk.main_quit()
			else:
				dialog.destroy()
				return True

	def on_key_press(self, label_entry, event):
		keymap = self.config['keymap']
		event_key = KeyPress(event.state, event.keyval)
		if is_key_pressed(keymap['new_tab'], event_key):
			self.add_terminal()
		elif is_key_pressed(keymap['close_tab'], event_key):
			self.close_terminal(self.notebook.get_current_page())
		elif is_key_pressed(keymap['prev_tab'], event_key):
			#prev_page() doens't switch to the last tab on the first tab
			self.notebook.set_current_page((self.notebook.get_current_page()-1)%len(self.tabs))
		elif is_key_pressed(keymap['next_tab'], event_key):
			self.notebook.set_current_page((self.notebook.get_current_page()+1)%len(self.tabs))
		elif is_key_pressed(keymap['move_tab_prev'], event_key):
			old_page_num = self.notebook.get_current_page()
			new_page_num = (old_page_num-1)%len(self.tabs)
			self.notebook.reorder_child(self.tabs[old_page_num].rxvt_socket, new_page_num)
		elif is_key_pressed(keymap['move_tab_next'], event_key):
			old_page_num = self.notebook.get_current_page()
			new_page_num = (old_page_num+1)%len(self.tabs)
			self.notebook.reorder_child(self.tabs[old_page_num].rxvt_socket, new_page_num)

	def on_page_removed(self, notebook, tab_widget, page_num):
		self.tabs.pop(page_num)
		#check if there are any more terminals left
		if not self.tabs:
			config_close_last_tab = self.config['general']['close_last_tab']
			if config_close_last_tab == 'blank':
				pass
			elif config_close_last_tab == 'new':
				self.add_terminal()
			elif config_close_last_tab == 'close':
				try:
					#from gtk 3.10
					self.close()
				except AttributeError:
					self.emit('delete-event', Gdk.Event(Gdk.EventType.DELETE))

	def on_page_reordered(self, notebook, tab_widget, new_page_num):
		#gtk doesn't provide a way to get the old page num
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
		#embedded terminal
		rxvt_socket = Gtk.Socket()
		self.rxvt_socket = rxvt_socket
		rxvt_socket.set_can_focus(True)
		#pygobject has some strange bug where if self is directory used then self fields won't exist
		rxvt_socket.connect_after('realize', lambda *args, **kwargs: self.on_realize(*args, **kwargs))
		rxvt_socket.connect_after('plug_added', lambda *args, **kwargs: self.on_plug_added(*args, **kwargs))
		rxvt_socket.connect_after('map_event', lambda *args, **kwargs: self.on_map_event(*args, **kwargs))
		self.event_listener_id = None
		self.plugged = None
		self.terminal_process = None
		#tab labels
		self.shell_title = title
		self.has_custom_title = False

	def update_tab_geometry_hints(self):
		'''
		copy the WM_NORMAL_HINTS properties of rxvt window to the rxvt tab so it stays within the rxvt resizing requirements
		resizing might not be smooth anymore if this is called
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
		creates a urxvt instance and embed it in widget
		'''
		xid = rxvt_socket.get_window().get_xid()
		self.terminal_process = subprocess.Popen([self.RXVT_BASENAME, '-embed', str(xid)])
		return False

	def on_map_event(self, rxvt_socket, event):
		rxvt_socket.grab_focus()
		return False

	def on_plug_added(self, rxvt_socket):
		'''
		runs when the urxvt embedded process attaches a plug to the socket specified by the xid
			(passed to it as a command-line argument)
		'''
		plugged = rxvt_socket.get_plug_window()
		if plugged is None:
			return
		self.plugged = plugged
		self.update_tab_geometry_hints()
		#listen to gdk property change events
		plugged.set_events(plugged.get_events()|Gdk.EventMask.PROPERTY_CHANGE_MASK)
		#urxvt only uses x.org, so only gdk events can be used
		self.event_listener_id = gdk_events.add_event_listener(self.on_gdk_event)
		return False

	def shell_set_title(self, title):
		if not self.has_custom_title:
			self.label.set_text(title)

	def user_set_title(self, title):
		#only use the user specified label if it isn't empty
		if title:
			self.has_custom_title = True
			self.label.set_text(title)
		else:
			self.has_custom_title = False
			self.label.set_text(self.shell_title)

	def on_gdk_event(self, event):
		'''
		events are also created when the urxvt plugged window closes,
			this handler disconnects itself when it recieves the event
		'''
		try:
			if event.type == Gdk.EventType.CONFIGURE:
				self.update_tab_geometry_hints()
			elif event.type == Gdk.EventType.PROPERTY_NOTIFY:
				if event.state == Gdk.PropertyState.NEW_VALUE:
					if event.atom.name() == '_NET_WM_NAME':
						#window name change event, set tab title
						display = Xlib.display.Display()
						xlib_window = display.create_resource_object('window', self.plugged.get_xid())
						title = xlib_window.get_wm_name()
						self.shell_title = title
						self.shell_set_title(title)
		except Xlib.error.BadWindow:
			#the plug window has now closed itself (there are no events indicating this, so catch the exception instead)
			gdk_events.remove_event_listener(self.event_listener_id)
			self.close()

	def on_label_edit_blur(self, label):
		self.rxvt_socket.grab_focus()

	def on_label_edit_submit(self, label):
		self.user_set_title(self.label.get_text())

	def close(self):
		try:
			#this detaches the gdk event listener as well, see docs for on_gdk_event()
			self.terminal_process.send_signal(signal.SIGINT)
			#call wait() so there's no defunct process
			self.terminal_process.wait()
		except OSError:
			pass

	def on_new_tab_close_click(self, widget):
		self.close()
