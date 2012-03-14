# File Navigator plugin for Sublime Text 2

This plugin lets You quickly navigate through your project and perform basic file operations
just using your keyboard (something that many of us missed when moving from VIM).

Things you can do with this plugin are:

- create new files and directories
- copy/move existing files
- rename existing files
- delete existing files

All of the operaions above are done using the excellent sublime quick panel window.
This means you get all the usual benifits of that including fuzzy name matching.

I would like to point out, that this is my first sublime plugin and my first encounter
with python, so please treat this as a very alpha version.

## How to install

### Package Control

The easiest and quickest way of installing is to use [Package Control](http://wbond.net/sublime_packages/package_control).
This method will allow you to keep the plugin up to date with the latest changes.

### Clone from GitHub

You can also just clone the repo to your packages directory if for some reason you do not wish to use package control:

    git clone git://github.com/belike81/Sublime-File-Navigator.git

## How to use it

Just open a project or a folder in sublime, and either invoke the quick panel and search for "File Navigator" or
just use the key bindings (or set your own):

  ### Mac OS X
  { "keys": ["super+shift+o"], "command": "file_navigator" }

  ### Windows and Linux
  { "keys": ["ctrl+shift+o"], "command": "file_navigator" }

## Excluded directories

You can exclude certain directories from appearing in the quick panel by setting them in your user settings file
or project file:

    ### User settings file:
    {
      "excluded_dir_patterns": [
        "tmp", "|.git", "|.svn"
      ]
    }

    ### Project file
    {
      "folders":
      [
        {
          "path": "/path/to/project"
        }
      ],
      "settings":
      {
        "SublimeFileNavigator":
          {
            "excluded_dir_patterns":
            [
              "tmp.*", "|.git", "|.svn", "|.hg"
            ]
          }
      }
    }

## Licence

All of SublimeFileNavigator is licensed under the MIT licence.

  Copyright (c) 2012 Tomasz Grabowski 

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

## Code base
When developing this plugin I used some code from the excellent [Sublime Quick File Creator](https://github.com/noklesta/SublimeQuickFileCreator)
plugin.