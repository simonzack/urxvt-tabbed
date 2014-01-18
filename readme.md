# URxvt Tabbed

URxvt terminals with gtk 3 tabs.
Tabs are implemented by embedding URxvt in a gtk notebook container, using pygobject as an interface to gtk.
URxvt does provide a rudimentary default gtk tabs implementation using perl, but with few features (e.g. no tab dragging or tab closing).

##Features

- Tab name editing (double click).
- Tab closing, drag & drop.
- Inherits tab titles set by shells.
- Customizable tab keyboard shortcuts.

## Installation and Use

This project depends on `python-gobject` and `python3-xlib`.

### Dependencies

On Arch Linux:

- `sudo pacman -S python-gobject`
- `sudo yaourt -S python3-xlib`

On other Linux systems:

- Install `python-gobject` using your favorite package manager
- `pip3 install python3-xlib`

### URxvt Tabbed
- `git clone git@github.com:simonzack/urxvt-tabbed.git`
- `cd urxvt-tabbed`
- `./urxvt-tabbed`

## Screenshots

![Multiple tabs](https://raw2.github.com/simonzack/urxvt-tabbed/master/screenshots/screenshot.png)

## Contributing

If you find any bugs, please open an issue.
I'm happy to accept any pull requests.
