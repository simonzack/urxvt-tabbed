from gi.repository import Gdk, Gtk

class GdkEvents:
	'''
	Event filters are not used due to [this bug](https://bugzilla.gnome.org/show_bug.cgi?id=687898).
	'''
	def __init__(self):
		# Use a dict instead of a list so that id's can be removed properly (list indices can change if a previous
        # event listener is removed)
		self.event_listeners = {}
		Gdk.Event.handler_set(self.event_handler, None)

	def event_handler(self, event, data):
		# Make a copy to avoid errors if the dict changes size
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
        Parameters:
			index: Functions are not used due to additional introduction of a map structure.
		'''
		del self.event_listeners[index]
