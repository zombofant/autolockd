
from distutils.core import setup

authors = (
    'Jonas Wielicki <j.wielicki@sotecware.net>, '
    'Sebastian Riese <sebastian.riese.mail@web.de>, '
    'Leon Weber <leon@leonweber.de>'
)

desc = (
    'dbus aware autolocker.'
)

long_desc = """
autolockd
---------

``autolockd`` is a simple, dbus aware autolocker. ``autolock-daemon``
is run as a daemon and should be autostarted from the X
session. ``autolock-cmd`` allows control of a running ``autolockd``.

``autolockd`` is primary targetted at minimal desktop environments
like awesome and xmonad.
"""


classifiers = [
    'Development Status :: 3',
    'Environment :: X11 Applications',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3',
    'Topic :: Desktop Environment :: Screen Savers'
]

setup(name='autolockd',
      version='0.1beta',
      author=authors,
      author_email='sebastian.riese.mail@web.de',
      requires=['dbus', 'gi'],
      packages=['autolockd'],
      scripts=['autolock-daemon', 'autolock-cmd'],
      license='GPLv3+',
      url='https://zombofant.net/hacking/autolockd',
      description=desc,
      long_description=long_desc,
      classifiers=classifiers
)
