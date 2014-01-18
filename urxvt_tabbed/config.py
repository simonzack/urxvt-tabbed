
import os
import configparser
from collections import namedtuple
from gi.repository import Gtk, Gdk, GObject, GdkX11
from gi.overrides import keysyms

class KeyPress(namedtuple('KeyboardShortcut', ('modifier_flags', 'key'))):
	@classmethod
	def parse(cls, s):
		'''
		allows None values
		'''
		s_vals = list(map(str.strip, s.split('+')))
		modifier_flags = 0
		modifier_map = {
			'Shift': Gdk.ModifierType.SHIFT_MASK,
			'Control': Gdk.ModifierType.CONTROL_MASK,
			'Alt': Gdk.ModifierType.MOD1_MASK,
			'Super': Gdk.ModifierType.SUPER_MASK,
			'Hyper': Gdk.ModifierType.HYPER_MASK,
			'Meta': Gdk.ModifierType.META_MASK,
		}
		if s_vals:
			for modifier in s_vals[:-1]:
				try:
					modifier_flags |= modifier_map[modifier]
				except KeyError:
					raise ValueError('unknown modifier', modifier)
			try:
				key = getattr(keysyms, s_vals[-1])
			except AttributeError:
				raise ValueError('unknown key')
		else:
			key = None
		return cls(modifier_flags, key)


class Config(dict):
	def __init__(self, config):
		super().__init__(config)

	@classmethod
	def parse_path(cls, path=None):
		if path is None:
			path=os.path.expanduser('~/.urxvt_tabbed/urxvt_tabbed.conf')
			if not os.path.exists(path):
				raise IOError('path does not exist', path)
		config = configparser.ConfigParser()
		config.read(path)
		config_dict = {}
		for section_name, section in config.items():
			if section_name == 'DEFAULT':
				continue
			config_dict[section_name] = dict(section)
		return cls.parse_strings(config_dict)

	@classmethod
	def parse_strings(cls, config):
		'''
		args:
			config {string: string}
		'''
		try:
			keymap = config['keymap']
			for key, val in keymap.items():
				keymap[key] = KeyPress.parse(val)
		except KeyError:
			pass
		return cls(config)


class ConfigDefaults(Config):
	'''
	config with defaults
	'''
	def __init__(self, config):
		#merge values with default values
		defaults = self.defaults()
		for default_section_name, default_section in defaults.items():
			if default_section_name in config:
				config_section = config[default_section]
				for default_key, default_val in default_section.items():
					if default_key not in config_section:
						config_section[default_key] = default_val
			else:
				config[default_section_name] = default_section
		super().__init__(config)

	@classmethod
	def parse_path(cls, path=None):
		return cls(Config.parse_path(path))

	@classmethod
	def parse_strings(cls, config):
		return cls(Config.parse_strings(config))

	@classmethod
	def defaults(cls):
		config = {
			'general': {
				'close_last_tab': 'blank',
			},
			'keymap': {
				'prev_tab': 'Control + Page_Up',
				'next_tab': 'Control + Page_Down',
				'new_tab': 'Control + Shift + T',
				'close_tab': 'Control + F4',
			}
		}
		return Config.parse_strings(config)
