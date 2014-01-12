#!/usr/bin/env python2

import gtk
import ctypes
import subprocess

CARD32 = ctypes.c_uint32

class XSizeHints(ctypes.Structure):
	class Point(ctypes.Structure):
		_fields_ = [
			('x', ctypes.c_int),
			('y', ctypes.c_int),
		]

	_fields_ = [
		('flags', CARD32),
		('pad', CARD32*4),
		('min_width', ctypes.c_int),
		('min_height', ctypes.c_int),
		('max_width', ctypes.c_int),
		('max_height', ctypes.c_int),
		('width_inc', ctypes.c_int),
		('height_inc', ctypes.c_int),
		('min_aspect', Point),
		('max_aspect', Point),
		('base_width', ctypes.c_int),
		('base_height', ctypes.c_int),
		('win_gravity', ctypes.c_int),
	]


class UrxvtTabbedWindow:
	'''
	Wrapper around urxvt which adds tabs
	the Gtk2::URxvt perl module doesn't seem to be available yet
	'''

	def __init__(self):
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window = window

		vbox = gtk.VBox()
		window.add(vbox)

		#tabs container
		notebook = gtk.Notebook()
		notebook.set_can_focus(False)
		notebook.set_scrollable(True)
		vbox.pack_start(notebook)
		self.notebook = notebook

		#new tab button
		new_tab_button = gtk.Button('+')
		new_tab_button.connect('clicked', self.on_new_tab_click)
		new_tab_button.show()
		notebook.set_action_widget(new_tab_button, 'end')

		#add new tab (otherwise the notebook won't appear)
		self.add_new_terminal()

	def add_new_terminal(self):
		notebook = self.notebook
		urxvt_tab = UrxvtTab()
		notebook.append_page(urxvt_tab.rxvt, urxvt_tab.label)
		notebook.set_current_page(notebook.page_num(urxvt_tab.rxvt))
		notebook.set_tab_reorderable(urxvt_tab.rxvt, 1)
		urxvt_tab.rxvt.show_all()

	def on_new_tab_click(self, widget):
		urxvt_tab = UrxvtTab()
		self.add_new_terminal()
		return 0


class UrxvtTab:
	RXVT_BASENAME = 'urxvt'

	def __init__(self, title='urxvt'):
		label = gtk.Label(title)
		#embedded terminal
		rxvt = gtk.Socket()
		rxvt.set_can_focus(True)
		rxvt.connect_after('realize', self.on_realize)
		rxvt.connect_after('plug_added', self.on_plug_added)
		rxvt.connect_after('map_event', self.on_map_event)
		self.label = label
		self.rxvt = rxvt

	def update_tab_geometry_hints(self):
		'''
		copy the WM_NORMAL_HINTS properties of rxvt window to the rxvt tab so it stays within the rxvt resizing requirements
		resizing might not be smooth anymore if this is called
		'''
		rxvt = self.rxvt
		plugged = rxvt.get_plug_window()
		prop_type, prop_format, prop_data = plugged.property_get('WM_NORMAL_HINTS', 'WM_SIZE_HINTS')
		prop_data = ctypes.cast((ctypes.c_uint*len(prop_data))(*prop_data), ctypes.POINTER(XSizeHints)).contents
		rxvt.get_toplevel().set_geometry_hints(
			rxvt,
			base_width=prop_data.base_width,
			base_height=prop_data.base_height,
			width_inc=prop_data.width_inc,
			height_inc=prop_data.height_inc
		)

	def on_realize(self, widget):
		'''
		creates a urxvt instance and embed it in widget
		'''
		xid = widget.window.xid
		subprocess.Popen([self.RXVT_BASENAME, '-embed', str(xid)])
		return 0

	def on_map_event(self, widget, event):
		widget.grab_focus()
		return 0

	def on_plug_added(self, socket):
		'''
		runs when the urxvt embedded process attaches a plug to the socket specified by the xid
			(passed to it as a command-line argument)
		'''
		plugged = socket.get_plug_window()
		self.update_tab_geometry_hints()
		#listen to gdk property change events
		plugged.set_events(plugged.get_events()|gtk.gdk.PROPERTY_CHANGE_MASK)
		#add gdk event filters (urxvt only uses x.org, so only gdk can be used)
		plugged.add_filter(self.on_gdk_property_notify)
		return 0

	def on_gdk_property_notify(self, event):
		#due to a bug in pygtk only gtk.gdk.NOTHING is returned, so try to update the window regardless of the event
		#	https://bugzilla.gnome.org/show_bug.cgi?id=722027

		#if event.type == gtk.gdk.CONFIGURE:
		#	self.update_tab_geometry_hints()
		#elif event.type == gtk.gdk.PROPERTY_NOTIFY:
		#	if event.state == gtk.gdk.PROPERTY_NEW_VALUE:
		#		if event.atom.name == '_NET_WM_NAME':
		#			#window name change event
		#			prop_type, prop_format, prop_data = self.rxvt.get_plug_window().property_get(event.atom.name, 'UTF8_STRING')
		#			self.label.set_text(prop_data)

		self.update_tab_geometry_hints()
		prop_type, prop_format, prop_data = self.rxvt.get_plug_window().property_get('_NET_WM_NAME', 'UTF8_STRING')
		self.label.set_text(prop_data)
		return gtk.gdk.FILTER_CONTINUE

def main():
	tabbed_window = UrxvtTabbedWindow()
	tabbed_window.window.maximize()
	tabbed_window.window.show_all()
	gtk.mainloop()

if __name__=='__main__':
	main()
