import configparser
import os
import re
from collections import namedtuple

from gi.repository import Gdk, Gtk
from xdg.BaseDirectory import xdg_config_home


class KeyPress(namedtuple('KeyboardShortcut', ('modifier_flags', 'key'))):
    @classmethod
    def parse_string(cls, s):
        '''
        Allows None values.
        '''
        key = None
        modifier_flags = 0
        s_vals = list(map(str.strip, s.split('+')))
        if s_vals:
            accelerator = ''.join([f'<{modifier}>' for modifier in s_vals[:-1]] + s_vals[-1:])
            key, modifier_flags = Gtk.accelerator_parse(accelerator)
            if key == 0 and modifier_flags == 0:
                raise ValueError(f'failed parsing shortcut: {s}')
        return cls(modifier_flags, key)

    @classmethod
    def parse_event(cls, event):
        # Ignore num_lock (Gdk.ModifierType.MOD2_MASK)
        return cls(event.state & (~Gdk.ModifierType.MOD2_MASK), Gdk.keyval_to_lower(event.keyval))


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
                keymap[key] = KeyPress.parse_string(val)
        except KeyError:
            pass

        try:
            default_size_str = config['ui']['default_size'].strip().lower()
            default_size = lambda window: window.set_default_size(800, 600)
            if default_size_str == 'maximize':
                default_size = lambda window: window.maximize()
            else:
                match = re.match(r'(\d+)x(\d+)', default_size_str)
                if match is not None:
                    default_size = lambda window: window.set_default_size(int(match.group(1)), int(match.group(2)))
            config['ui']['default_size'] = default_size
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
                'switch_to_tab_1': 'Alt + 1',
                'switch_to_tab_2': 'Alt + 2',
                'switch_to_tab_3': 'Alt + 3',
                'switch_to_tab_4': 'Alt + 4',
                'switch_to_tab_5': 'Alt + 5',
                'switch_to_tab_6': 'Alt + 6',
                'switch_to_tab_7': 'Alt + 7',
                'switch_to_tab_8': 'Alt + 8',
                'switch_to_tab_9': 'Alt + 9',
                'switch_to_tab_10': 'Alt + 0',
            },
            'ui': {
                'font': '',
                'default_size': '800x600',
            },
        }
        return Config.parse_strings(config)
