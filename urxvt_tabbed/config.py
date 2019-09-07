import configparser
import os
from collections import namedtuple

from gi.repository import Gdk
from xdg.BaseDirectory import xdg_config_home


class KeyPress(namedtuple('KeyboardShortcut', ('modifier_flags', 'key'))):
	@classmethod
	def parse(cls, s):
		'''
		Allows None values.
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
				key = getattr(Gdk, 'KEY_{}'.format(s_vals[-1]))
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
			path = os.path.join(xdg_config_home, 'urxvt_tabbed/urxvt_tabbed.conf')
			if not os.path.exists(path):
				raise OSError('path does not exist', path)
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
        Parameters:
			config ({string: string})
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
	Config with defaults
	'''
	def __init__(self, config):
		# Merge values with default values
		defaults = self.defaults()
		for default_section_name, default_section in defaults.items():
			if default_section_name in config:
				config_section = config[default_section_name]
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
				'close_last_tab': 'new',
			},
			'keymap': {
				'prev_tab': 'Control + Page_Up',
				'next_tab': 'Control + Page_Down',
				'move_tab_prev': 'Control + Shift + Page_Up',
				'move_tab_next': 'Control + Shift + Page_Down',
				'new_tab': 'Control + Shift + T',
				'close_tab': 'Control + F4',
				'edit_tab': 'Control + Shift + E',
			},
			'ui': {
				'font': '',
			},
		}
		return Config.parse_strings(config)
