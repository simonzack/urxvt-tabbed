# URxvt Tabbed

URxvt terminals with GTK tabs.
Tabs are implemented by embedding URxvt in a GTK notebook container, using pygobject as an interface to GTK.
URxvt does provide a rudimentary default GTK tabs implementation using perl, but with limited features (e.g. no tab dragging or tab closing).

## Features

- Tab name editing (double click).
- Tab closing, drag & drop.
- Inherits tab titles set by shells.
- Customizable keyboard shortcuts.

## Installation and Use

Install the package via `pip` (either the pypi or github version), and run `urxvt-tabbed`.

## Configuration

The configuration is read from `~/.config/urxvt_tabbed/urxvt_tabbed.conf`, which uses the ini format:

```ini
[section]
foo = bar
```

### [ui]

- `font`: [font description][font-desc] used for UI, e.g. `Monospace`, `Inconsolata 12` or `Envy Code R italic 16`. Defaults come from GTK.
- `default_size`: Default window size, e.g. `maximize`, `800x600`. The default size is `800x600`.

[font-desc]: http://www.pygtk.org/docs/pygtk/class-pangofontdescription.html

### [general]

- `close_last_tab`: One of `open_new_tab`, `close_application`

### [keymap]

- `prev_tab`: Previous tab, defaults to `Control + Page_Up`
- `next_tab`: Next tab, defaults to `Control + Page_Down`
- `move_tab_prev`: Move tab left, defaults to `Control + Shift + Page_Up`
- `move_tab_next`: Move tab right, defaults to `Control + Shift + Page_Down`
- `new_tab`: New tab, defaults to `Control + Shift + T`
- `close_tab`: Close tab, defaults to `Control + F4`
- `edit_tab`: Edit tab label, defaults to `Control + Shift + E`
- `switch_to_tab_1`, `switch_to_tab_2`, ..., `switch_to_tab_10`: Switch to tab 1, 2, ..., 10, defaults to `Alt + 1`, `Alt + 2`, ..., `Alt + 0`

## Screenshots

![Multiple tabs](https://raw.githubusercontent.com/simonzack/urxvt-tabbed/master/screenshots/screenshot.png)

## Contributing

If you find any bugs or have any feature requests, please open an issue.
I'm happy to accept any pull requests.

## Contributors

Thanks to everybody who [contributed](https://github.com/simonzack/urxvt-tabbed/graphs/contributors)!

## License

Licensed under GPLv3.
