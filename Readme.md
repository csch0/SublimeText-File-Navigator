# File Navigator for Sublime Text 2/3

This plugin lets You quickly navigate through your project and perform basic file operations just using your keyboard (something that many of us missed when moving from VIM).

Things you can do with this plugin are:

	- create new files and directories
	- copy/move/paste existing files/directories
	- rename existing files
	- delete existing files

All of the operations above are done using the excellent sublime quick panel window. This means you get all the usual benefits of that including fuzzy name matching.

## Usage

* `super+shift+o` on OSX or `ctrl+shift+o` on Windows/Linux shows a quick panel with directories related to the current open files or window.

* `tab` shows the directory actions for the current selected folder

* `super+.` on OSX or `ctrl+.` on Windows/Linux hide/shows the hidden files temporary, just can adjust this in the settings.

## Screenshots

![Navigator](https://raw.github.com/wiki/Chris---/SublimeText-File-Navigator/navigator.jpg)

![Navigator - File Actions](https://raw.github.com/wiki/Chris---/SublimeText-File-Navigator/file.jpg)

![Navigator - Directory Actions](https://raw.github.com/wiki/Chris---/SublimeText-File-Navigator/directory.jpg)

![Navigator - Paste](https://raw.github.com/wiki/Chris---/SublimeText-File-Navigator/paste.jpg)

## Installation

### Using Package Control:

* Bring up the Command Palette (Command+Shift+P on OS X, Control+Shift+P on Linux/Windows).
* Select Package Control: Install Package.
* Select File Navigator to install.

### Not using Package Control:

* Save files to the `Packages/File Navigator` directory, then relaunch Sublime:
  * Linux: `~/.config/sublime-text-2|3/Packages/File Navigator`
  * Mac: `~/Library/Application Support/Sublime Text 2|3/Packages/File Navigator`
  * Windows: `%APPDATA%/Sublime Text 2|3/Packages/File Navigator`

## Donating

Support this project via [gittip][] or [paypal][].

[![Support via Gittip](https://rawgithub.com/chris---/Donation-Badges/master/gittip.jpeg)][gittip] [![Support via PayPal](https://rawgithub.com/chris---/Donation-Badges/master/paypal.jpeg)][paypal]

[gittip]: https://www.gittip.com/Chris---
[paypal]: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZWZCJPFSZNXEW

## Code base
The initial idea of this package came from by Tomasz Grabowski. Thanks for that :)

## License

All files in this package is licensed under the MIT license.

Copyright (c) 2013 Chris <chris@latexing.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.