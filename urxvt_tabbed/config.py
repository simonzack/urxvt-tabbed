
import os
import configparser

config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.urxvt_tabbed/urxvt_tabbed.conf'))
config['general'] = {
	'close_last_tab': 'blank',
}
config['keymap'] = {
	'prev_tab': 'Control + Page_Up',
	'next_tab': 'Control + Page_Down',
	'new_tab': 'Control + Shift + T',
	'close_tab': 'Control + F4',
}
