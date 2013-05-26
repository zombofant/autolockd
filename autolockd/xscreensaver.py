from ctypes import *
from ctypes.util import find_library


class XScreenSaverException(Exception):
    pass

libx = cdll.LoadLibrary(find_library("X11"))
libx_screen_saver = cdll.LoadLibrary(find_library("Xss"))


Time = c_ulong
Bool = c_int
Window = c_ulong
Drawable = c_ulong


class Display(Structure):
    pass


class ScreenSaverInfo(Structure):
    _fields_ = [
        ("window", Window),
        ("state", c_int),
        ("kind", c_int),
        ("til_or_since", c_ulong),
        ("idle", c_ulong),
        ("eventMask", c_ulong)]

open_display = libx.XOpenDisplay
open_display.argtypes = [c_char_p]
open_display.restype = POINTER(Display)

close_display = libx.XCloseDisplay
close_display.argtypes = [POINTER(Display)]
close_display.restype = c_int

xfree = libx.XFree
xfree.argtypes = [c_void_p]
xfree.restype = None

default_root_window = libx.XDefaultRootWindow
default_root_window.argtypes = [POINTER(Display)]
default_root_window.restype = Window

screen_saver_query_extension = libx_screen_saver.XScreenSaverQueryExtension
screen_saver_query_extension.argtypes = [POINTER(Display), POINTER(c_int),
                                         POINTER(c_int)]
screen_saver_query_extension.restype = c_int

screen_saver_alloc_info = libx_screen_saver.XScreenSaverAllocInfo
screen_saver_alloc_info.argtypes = []
screen_saver_alloc_info.restype = POINTER(ScreenSaverInfo)

screen_saver_query_info = libx_screen_saver.XScreenSaverQueryInfo
screen_saver_query_info.argtypes = [POINTER(Display), Drawable,
                                    POINTER(ScreenSaverInfo)]
screen_saver_query_info.restype = c_int


class ScreenSaver(object):

    def __init__(self, display=None):
        if display is None:
            self.display = open_display(None)
            self.close_display = True
        else:
            self.display = display
            self.close_display = False
        if not self.display:
            raise XScreenSaverException("Could not open display")
        if not screen_saver_query_extension(self.display,
                                            POINTER(c_int)(c_int(0)),
                                            POINTER(c_int)(c_int(0))):
            raise XScreenSaverException("XScrnSaver extension not supported")
        self.info = screen_saver_alloc_info()
        if self.info is None:
            raise XScreenSaverException("Could not alloc screen saver info")

    def __del__(self):
        xfree(self.info)
        if self.close_display:
            close_display(self.display)

    def get_idle_time(self):
        screen_saver_query_info(self.display,
                                default_root_window(self.display),
                                self.info)
        return self.info.contents.idle

if __name__ == '__main__':
    print(ScreenSaver().get_idle_time())
