#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
#

""" Tango Data Writer """

import threading

#: (:obj:`str`) package version
from .Release import __version__

#: (:class:`threading.Lock`) global lock
globallock = threading.Lock()

__all__ = ["__version__", "run", "globallock", "main"]


def run(argv):
    """ launches the TANGO server

    :param argv: command-line arguments
    :type argv: :obj:`list` <:obj:`str`>
    """

    try:
        import tango
    except Exception:
        import PyTango as tango
    from .NXSWriter import NXSDataWriter as NXSWriter
    from .NXSWriter import NXSDataWriterClass as NXSWriterClass
    try:
        py = tango.Util(argv)
        py.add_class(NXSWriterClass, NXSWriter)

        U = tango.Util.instance()
        U.server_init()
        U.server_run()

    except tango.DevFailed as e:
        print('-------> Received a DevFailed exception: %s' % e)
    except Exception as e:
        print('-------> An unforeseen exception occured.... %s' % e)


def main():
    import sys
    run(sys.argv)
