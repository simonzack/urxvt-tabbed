# URxvt Tabbed

URxvt terminals with gtk 3 tabs.
Tabs are implemented by embedding URxvt in a gtk notebook container, using pygobject as an interface to gtk.
URxvt does provide a rudimentary default gtk tabs implementation using perl, but with limited features (e.g. no tab dragging or tab closing).

##Features

- Tab name editing (double click).
- Tab closing, drag & drop.
- Inherits tab titles set by shells.
- Customizable keyboard shortcuts.

## Installation and Use

### Dependencies

- `python-gobject`
- `python3-xlib`

#### Installing Dependencies

Arch Linux:

- `sudo pacman -S python-gobject`
- `sudo yaourt -S python3-xlib`

Other Linux systems:

- Install `python-gobject` using your favorite package manager
- `pip3 install python3-xlib`

### Installing URxvt Tabbed
- `git clone git@github.com:simonzack/urxvt-tabbed.git`
- `cd urxvt-tabbed`
- `./bin/urxvt-tabbed`

## Configuration

The configuration is read from `~/.urxvt_tabbed/urxvt_tabbed.conf`, which uses the ini format:

```ini
[section]
foo = bar
```

### [ui]

- `font`: [font description][font-desc] used for UI, e.g. `Monospace`, `Inconsolata 12` or `Envy Code R italic 16`. Defaults come from gtk.

[font-desc]: http://www.pygtk.org/docs/pygtk/class-pangofontdescription.html

### [general]
- `close_last_tab`: One of `new`, `close`, `blank`

### [keymap]
- `prev_tab`: Previous tab, defaults to `Control + Page_Up`
- `next_tab`: Next tab, defaults to `Control + Page_Down`
- `move_tab_prev`: Move tab left, defaults to `Control + Shift + Page_Up`
- `move_tab_next`: Move tab right, defaults to `Control + Shift + Page_Down`
- `new_tab`: New tab, defaults to `Control + Shift + T`
- `close_tab`: Close tab, defaults to `Control + F4`
- `edit_tab`: Edit tab label, not bound by default

## Screenshots

![Multiple tabs](https://raw2.github.com/simonzack/urxvt-tabbed/master/screenshots/screenshot.png)

## Contributing

If you find any bugs or have any feature requests, please open an issue.
I'm happy to accept any pull requests.

## Contributors
Thanks to everybody who [contributed](https://github.com/simonzack/urxvt-tabbed/graphs/contributors)!

## License
Licensed under GPLv3.
