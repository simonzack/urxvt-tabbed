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

## Keys
- `Control + Page_Up` - Previous tab
- `Control + Page_Down` - Next tab
- `Control + Shift + Page_Up` - Move current tab before previous tab
- `Control + Shift + Page_Down` - Move current tab after next tab
- `Control + Shift + T` - New tab
- `Control + F4` - Close tab

## Configuration

The configuration is read from `~/.urxvt_tabbed/urxvt_tabbed.conf` with the following format:

```ini
[section]
foo = bar
```

### `ui` section

* `font`: [font description][font-desc] used for UI, default is `monospace`.

    You can try something like `Inconsolata 12` or `Envy Code R italic 16`.

[font-desc]: http://www.pygtk.org/docs/pygtk/class-pangofontdescription.html

## Screenshots

![Multiple tabs](https://raw2.github.com/simonzack/urxvt-tabbed/master/screenshots/screenshot.png)

## Contributing

If you find any bugs or have any feature requests, please open an issue.
I'm happy to accept any pull requests.

## License
Licensed under GPLv3.
