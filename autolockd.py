#!/usr/bin/python2
from __future__ import division, print_function

import argparse

import autolockd

ap = argparse.ArgumentParser()
ap.add_argument('--version', action='version', version=autolockd.__version__)
ap.add_argument('-f', '--config-file', default=None,
                help='Set alternative config file [default ~/.autolockd]')

args = ap.parse_args()

autolockd.setup_mainloop()
lockd = autolockd.Autolockd(args.config_file)
lockd.run()
