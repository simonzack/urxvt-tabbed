from gi.repository import Gdk, GObject, Gtk


class ClosableTabLabel(Gtk.Box):
	__gsignals__ = {
		"close_clicked": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
		"label_edit_focus": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
		"label_edit_blur": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
		"label_edit_submit": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
	}

	def __init__(self, label_text):
		super().__init__()
		self.set_orientation(Gtk.Orientation.HORIZONTAL)

		#label
		label_event_box = Gtk.EventBox()
		self.label = Gtk.Label(label_text)
		label_event_box.add(self.label)
		label_event_box.connect('button-press-event', self.on_label_button_press)
		self.pack_start(label_event_box, True, True, 0)

		self.label_entry = Gtk.Entry()
		self.label_entry.connect('key-press-event', self.on_label_entry_key_press)
		self.label_entry.connect('focus-out-event', self.on_label_entry_focus_out)
		self.label_entry.connect('changed', self.on_label_entry_changed)
		self.pack_start(self.label_entry, True, True, 0)

		#close button
		button = Gtk.Button()
		button.set_relief(Gtk.ReliefStyle.NONE)
		button.set_focus_on_click(False)
		button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
		button.connect('clicked', self.on_close_click)
		data =  \
			'.button {' \
				'padding: 0px;' \
			'}'
		provider = Gtk.CssProvider()
		provider.load_from_data(data.encode())
		#GTK_STYLE_PROVIDER_PRIORITY_APPLICATION = 600
		button.get_style_context().add_provider(provider, 600)
		self.button = button
		self.pack_start(button, False, False, 0)

		#show all
		self.show_all()
		self.label_entry.hide()

	def get_text(self):
		return self.label.get_text()

	def set_text(self, label_text):
		self.label.set_text(label_text)

	def on_close_click(self, button, data=None):
		self.emit('close_clicked')

	def label_edit_focus(self):
		self.label.hide()
		self.label_entry.show()
		self.label_entry.grab_focus()
		label_text = self.label.get_text()
		self.label_entry.set_width_chars(len(label_text))
		self.label_entry.set_text(label_text)
		#select all text
		self.label_entry.emit('move-cursor', 1, len(label_text), True)
		self.emit('label_edit_focus')

	def label_edit_submit(self):
		label_text = self.label_entry.get_text()
		self.label.set_text(label_text)
		self.emit('label_edit_submit')
		self.label_edit_blur()

	def label_edit_blur(self):
		self.label_entry.hide()
		self.label.show()
		self.emit('label_edit_blur')

	def on_label_button_press(self, event_box, event, data=None):
		'''
		edit label on double click
		'''
		if event.type==Gdk.EventType._2BUTTON_PRESS:
			self.label_edit_focus()

	def on_label_entry_key_press(self, label_entry, event, data=None):
		if event.keyval==Gdk.KEY_Return:
			#enter key press
			self.label_edit_submit()
		elif event.keyval==Gdk.KEY_Escape:
			#enter key press
			self.label_edit_blur()

	def on_label_entry_focus_out(self, label_entry, event, data=None):
		'''
		restore label after focus out
		'''
		self.label_edit_blur()

	def on_label_entry_changed(self, label_entry, data=None):
		'''
		adapt label size
		'''
		label_text = self.label_entry.get_text()
		self.label_entry.set_width_chars(len(label_text))
