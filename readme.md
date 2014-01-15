# URxvt Tabbed

URxvt terminals with gtk 3 tabs.
Tabs are implemented by embedding URxvt in a gtk notebook container, using pygobject as an interface to gtk.
URxvt does provide a rudimentary default gtk tabs implementation using perl, but with few features (e.g. no tab dragging or tab closing).

##Features

- Tab name editing (double click).
- Tab closing, drag & drop.
- Inherits tab titles set by shells.

## Installation and Use

On arch:
- `sudo pacman -S python-gobject`
- `sudo yaourt -S python3-xlib`
- `git clone git@github.com:simonzack/urxvt-tabbed.git`
- `cd urxvt-tabbed`
- `./urxvt-tabbed`

## Screenshots

![Multiple tabs](https://raw2.github.com/simonzack/urxvt-tabbed/master/screenshots/screenshot.png)

## Contributing

If you find any bugs, please open an issue.
I'm happy to accept any pull requests.
