#!/usr/bin/env python

import ctypes
import subprocess

import Xlib
import Xlib.display
from gi.repository import Gtk, Gdk, GdkX11

##
#gdk helper functions
##

class GdkEvents:
	'''
	event filters are not used due to this bug:
		https://bugzilla.gnome.org/show_bug.cgi?id=687898
	'''
	def __init__(self):
		#use a dict instead of a list so that id's can be removed properly (list indices can change if a previous event listener is removed)
		self.event_listeners = {}
		Gdk.Event.handler_set(self.event_handler, None)

	def event_handler(self, event, data):
		#make a copy to avoid errors if the dict changes size
		for func, func_args, func_kwargs in list(self.event_listeners.values()):
			func(event, *func_args, **func_kwargs)
		Gtk.main_do_event(event)

	def add_event_listener(self, func, func_args=None, func_kwargs=None):
		if func_args is None:
			func_args = ()
		if func_kwargs is None:
			func_kwargs = {}
		listener_id = len(self.event_listeners)
		self.event_listeners[listener_id] = (func, func_args, func_kwargs)
		return listener_id

	def remove_event_listener(self, index):
		'''
		args:
			index:	functions are not used due to additional introduction of a map structure
		'''
		del self.event_listeners[index]

gdk_events = GdkEvents()

##
#urxvt tabs
##

class UrxvtTabbedWindow(Gtk.Window):
	'''
	Wrapper around urxvt which adds tabs
	the Gtk2::URxvt perl module doesn't seem to be available yet
	'''

	def __init__(self):
		super().__init__(title='urxvt')

		vbox = Gtk.VBox()
		self.add(vbox)

		#tabs container
		notebook = Gtk.Notebook()
		notebook.set_can_focus(False)
		notebook.set_scrollable(True)
		vbox.pack_start(notebook, True, True, 0)
		self.notebook = notebook

		#new tab button
		new_tab_button = Gtk.Button('+')
		new_tab_button.connect('clicked', self.on_new_tab_click)
		new_tab_button.show()
		notebook.set_action_widget(new_tab_button, Gtk.PackType.END)

		#add new tab (otherwise the notebook won't appear)
		self.add_new_terminal()

	def add_new_terminal(self):
		notebook = self.notebook
		urxvt_tab = UrxvtTab()
		notebook.append_page(urxvt_tab.rxvt_socket, urxvt_tab.label)
		notebook.set_tab_reorderable(urxvt_tab.rxvt_socket, 1)
		urxvt_tab.rxvt_socket.show_all()
		notebook.set_current_page(notebook.page_num(urxvt_tab.rxvt_socket))

	def on_new_tab_click(self, widget):
		self.add_new_terminal()
		return 0


class UrxvtTab:
	RXVT_BASENAME = 'urxvt'

	def __init__(self, title='urxvt'):
		label = Gtk.Label(title)
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
		subprocess.Popen([self.RXVT_BASENAME, '-embed', str(xid)])
		return 0

	def on_map_event(self, rxvt_socket, event):
		rxvt_socket.grab_focus()
		return 0

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
		return 0

	def on_gdk_event(self, event):
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
						self.label.set_text(title)
		except Xlib.error.BadWindow:
			#the plug window has now closed itself (there are no events indicating this, so catch the exception instead)
			gdk_events.remove_event_listener(self.event_listener_id)


def main():
	tabbed_window = UrxvtTabbedWindow()
	tabbed_window.maximize()
	tabbed_window.show_all()
	tabbed_window.connect('destroy', Gtk.main_quit)
	Gtk.main()

if __name__=='__main__':
	main()
