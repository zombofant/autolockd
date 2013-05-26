"""
autolockd, a dbus aware autolocker
"""
__version__ = '0.1beta'
__all__ = ['setup_mainloop', 'Autolockd']

import subprocess
import configparser
import os
import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service
from gi.repository import GObject

import autolockd.xscreensaver as xscreensaver

logger = logging.getLogger(__name__)


def setup_mainloop():
    global loop_
    loop_ = DBusGMainLoop(set_as_default=True)


class Locker(metaclass=ABCMeta):
    """Interface for screen lockers

    This abstracts away the interface by which the screen lock
    child process is controlled.
    """
    @abstractmethod
    def ensure_lock(self):
        pass

    @abstractmethod
    def ensure_unlock(self):
        pass

    @abstractproperty
    def is_locked(self):
        pass


class BlockingLocker(Locker):
    """Interface to locking programs which do not exit until the lock
    is cleared.
    """

    def __init__(self, locker):
        super().__init__()
        self._locker = locker
        self._current_lock = None

    def _check_returncode(self):
        if self._current_lock.returncode != 0:
            logger.error("Locker returned non-zero")

    def ensure_lock(self):
        if not self.is_locked:
            logger.info('Starting locker {}'.format(self._locker))
            self._current_lock = subprocess.Popen(self._locker, shell=True)

    def ensure_unlock(self):
        logger.info('Unlocking')
        if self._current_lock is not None:
            self._current_lock.terminate()
            self._current_lock.wait()
            self._check_returncode()
        self._current_lock = None

    @property
    def is_locked(self):
        if self._current_lock is not None:
            if self._current_lock.poll() is not None:
                self._check_returncode()
                self._current_lock = None
            else:
                # the screen locker is running
                return True
        return False


# TODO: implement the freedesktop, gnome and kde screensaver interfaces
class Autolockd(dbus.service.Object):

    def __init__(self, config_file=None):
        session_bus = dbus.SessionBus()
        busname = dbus.service.BusName("net.zombofant.autolockd", session_bus)
        super(Autolockd, self).__init__(bus_name=busname,
                                        object_path="/net/zombofant/autolockd")
        self._active = True
        self._load_config(config_file)
        self._locker = BlockingLocker(self._config.get("lock", "cmd"))
        self._inhibit_counter = 0
        self._inhibit = set()
        self._setup()

    def _load_config(self, config_file):
        # load the default config
        self._config = configparser.SafeConfigParser()
        self._config.add_section("lock")
        self._config.set("lock", "cmd", "pyxtrlock")
        self._config.set("lock", "onidle", "true")
        self._config.set("lock", "idletime", "5")
        self._config.set("lock", "idleunit", "min")
        self._config.set("lock", "onlidclose", "true")
        self._config.set("lock", "onsleep", "true")

        self._config.add_section("unlock")
        self._config.set("unlock", "allow", "true")

        self._config.add_section("interfaces")

        if config_file is None:
            self._config.read([os.path.expanduser("~/.autolockd")])
        else:
            self._config.readfp(open(config_file), config_file)

        # TODO check config values for sanity!!

    def _get_idle_unit(self):
        UNITS = {"hour": 1000 * 60 * 60,
                 "min": 1000 * 60,
                 "sec": 1000}

        # we assure this is correct in load config
        return UNITS[self._config.get("lock", "idleunit")]

    def _query_idle(self, dummy):
        idle_time = self._screen_saver.get_idle_time()
        unit = self._get_idle_unit()

        if idle_time > self._config.getint("lock", "idletime") * unit:
            self._lock_filtered()

        return True

    def _setup(self):
        self._loop = GObject.MainLoop()
        system_bus = dbus.SystemBus()

        upower_proxy = system_bus.get_object("org.freedesktop.UPower",
                                             "/org/freedesktop/UPower")

        self.upower = dbus.Interface(upower_proxy, "org.freedesktop.UPower")
        self.upower_properties = dbus.Interface(
            upower_proxy,
            "org.freedesktop.DBus.Properties")

        if self._config.getboolean("lock", "onsleep"):
            self.upower.connect_to_signal("Sleeping", self._on_sleep)

        if self._config.getboolean("lock", "onlidclose"):
            self.upower.connect_to_signal("Changed", self._on_change)

        if self._config.getboolean("lock", "onidle"):
            self._screen_saver = xscreensaver.ScreenSaver()
            GObject.timeout_add(1000, self._query_idle, None)

    def _on_sleep(self):
        logger.info('Locking: system is going to sleep.')
        self._lock_filtered()

    def _on_change(self):
        if self.upower_properties.Get("org.freedesktop.UPower", "LidIsClosed"):
            logger.info('Locking: lid is closed.')
            self._lock_filtered()

    def _lock_filtered(self):
        if self._active and not self._inhibit:
            self._lock()

    def _lock(self):
        self._locker.ensure_lock()

    def _unlock(self):
        if not self._config.get("unlock", "allow"):
            logger.info('Unlocking not allowed by config.')
            return

        self._locker.ensure_unlock()

    def run(self):
        logger.debug('Daemon started.')
        self._loop.run()

    def inhibit(self):
        cookie = self._inhibit_counter
        self._inhibit_counter += 1
        self._inhibit.add(cookie)
        return cookie

    def uninhibit(self, cookie):
        self._inhibit.remove(cookie)

    ###################################################################
    # DBUS interface "net.zombofant.autolockd"
    @dbus.service.method(dbus_interface="net.zombofant.autolockd",
                         in_signature='',
                         out_signature='')
    def Lock(self):
        logger.info('Received lock command.')
        self._lock()

    @dbus.service.method(dbus_interface="net.zombofant.autolockd",
                         in_signature='',
                         out_signature='')
    def Unlock(self):
        logger.info('Received unlock command.')
        self._unlock()

    @dbus.service.method(dbus_interface="net.zombofant.autolockd",
                         in_signature='',
                         out_signature='')
    def Enable(self):
        logger.info('Received enable command, enabling.')
        self._active = True

    @dbus.service.method(dbus_interface="net.zombofant.autolockd",
                         in_signature='',
                         out_signature='')
    def Disable(self):
        logger.info('Received enable command, disabling.')
        self._active = False

    #################################################################
    # DBUS interface "org.freedesktop.DBus.Properties"
    @dbus.service.method(dbus_interface="org.freedesktop.DBus.Properties",
                         in_signature='ss',
                         out_signature='v')
    def Get(self, interface, prop):
        try:
            return self.GetAll()[prop]
        except KeyError:
            dbus.exceptions.DBusException(
                'net.zombofant.autolockd',
                'Interface %s does not supply the property %s'
                % (prop, interface))


    @dbus.service.method(dbus_interface="org.freedesktop.DBus.Properties",
                         in_signature='ssv',
                         out_signature='')
    def Set(self, interface, prop, value):
        if interface != "net.zombofant.autolockd":
            raise dbus.exceptions.DBusException(
                'net.zombofant.autolockd',
                'The object does not implement the %s interface'
                % interface)

        raise dbus.exceptions.DBusException(
            'net.zombofant.autolockd',
            'The property %s on interface %s is readonly'
            % (prop, interface))


    @dbus.service.method(dbus_interface="org.freedesktop.DBus.Properties",
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != "net.zombofant.autolockd":
            raise dbus.exceptions.DBusException(
                'net.zombofant.autolockd',
                'The object does not implement the %s interface'
                % interface)
        return {"AllowUnlock": self._config.getboolean("unlock", "allow"),
                "Locked": self._locker.is_locked,
                "Enabled": self._active and not self._inhibit}
