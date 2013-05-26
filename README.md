autolockd
=========

``autolockd`` is a simple, dbus aware autolocker. ``autolock-daemon``
is run as a daemon and should be autostarted from the X
session. ``autolock-cmd`` allows control of a running ``autolockd``.

``autolockd`` is primary targetted at minimal desktop environments
like awesome and xmonad.

Description
-----------

It uses DBUS as system interface, especially the
``org.freedesktop.UPower`` interface. The idle time is retrieved using
ctypes bindings for the MIT screen saver X extension.

It can be configured to lock on lid close, prior to suspend or
hibernate and after a specified idle time. Additionally it can be
locked manually by ``autolock-cmd lock``.

There is a simple lock-inhibition mechanism (the ``autolock-cmd
disable``, ``autolock-cmd enable`` commands) for direct user
interaction.

It is planned to implement the ``org.gnome.ScreenSaver``,
``org.freedesktop.ScreenSaver`` interfaces additionally to the
``net.zombofant.autolockd`` interface, and therefore lock inhibition
for programs.

The screen locker to be invoked can be configured to be any
command. Currently it must not return until the lock ends. By default
``pyxtrlock`` is used. These restrictions shall be lifted in future
versions.

Installation
------------

Clone and install ``autolockd``:

    $ git clone git://github.com/zombofant/autolockd.git
    $ cd autolockd
    $ sudo python3 setup.py install

This installs the ``autolockd`` python package and the two scripts
``autolock-daemon`` and ``autolock-cmd``.

For the default locking mechanism to work you shoudl also install
``pyxtrlock``.

Configuration
-------------

See ``default.conf`` for the available options and their default
values. By default ``~/.autolockd`` is used as config file. The
``--config-file`` option lets you use another config file.

Invocation
----------

Server:

    usage: autolock-daemon [-h] [--version] [-c CONFIG] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -c CONFIG, --config CONFIG
                            Set alternative config file [default ~/.autolockd]
      -v, --verbose         Increase verbosity level

Client:

    usage: autolock-cmd [-h] [--version] {lock,unlock,disable,enable} ...

    positional arguments:
      {lock,unlock,disable,enable}

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit

Bugs
----

Currently there is no support for the ``org.freedesktop.ScreenSaver``
dbus interface.

The locking command must not exit before the screen is unlocked (the
state of the screen locking program process is used for state
control).

Please report bugs you may find to our [github bug
tracker](https://github.com/zombofant/autolockd/issues).

Requirements
------------

* python3-dbus
* python3-gobject (gi)
* libX11, libXss (interfaced via ctypes)
* a provider of the DBUS interface ``org.freedesktop.UPower``
* X server with MIT screen saver extension
* screenlocker for default configuration:
  [pyxtrlock](git://github.com/leonnnn/pyxtrlock.git)

Authors
-------
* Jonas Wielicki <j.wielicki@sotecware.net>
* Sebastian Riese <s.riese@zombofant.net>
* Leon Weber <leon@leonweber.de>

``autolockd`` was partially inspired by ``xautolock``.

License
-------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
