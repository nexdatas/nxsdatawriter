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
# \package test nexdatas
# \file conftest.py
# pytest configuration of the nxswriter tests
#
import os
import sys

import pytest


def pytest_sessionfinish(session, exitstatus):
    """ stores the exit status of the test session

    :param session: pytest session
    :type session: :class:`pytest.Session`
    :param exitstatus: exit status
    :type exitstatus: :obj:`int`
    """
    session.config._nxswriter_exitstatus = int(exitstatus)


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):
    """ exits the test process without the interpreter finalization

    After tests with tango servers and device proxies omniORB can abort
    in its finalization, i.e. ``SocketCollection.cc ... pd_refcount > 0``,
    so that the process fails although all tests passed.  The process
    exits with the status of the test session when pytest is done.
    Set ``NXSWRITER_NO_HARD_EXIT`` to disable it.

    :param config: pytest configuration
    :type config: :class:`pytest.Config`
    """
    status = getattr(config, "_nxswriter_exitstatus", None)
    if status is None or os.environ.get("NXSWRITER_NO_HARD_EXIT"):
        return
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.flush()
        except Exception:
            pass
    os._exit(status)
