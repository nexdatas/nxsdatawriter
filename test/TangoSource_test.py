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
# \file TangoSourceTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time
import json

try:
    import tango
except Exception:
    import PyTango as tango

try:
    import SimpleServerSetUp
except Exception:
    from . import SimpleServerSetUp

try:
    from ProxyHelper import ProxyHelper
except Exception:
    from .ProxyHelper import ProxyHelper


from nxswriter.TangoSource import DataSource
from nxswriter.TangoSource import TangoSource
from nxswriter.TangoSource import TgMember
from nxswriter.TangoSource import TgGroup
from nxswriter.TangoSource import TgDevice
from nxswriter.DecoderPool import DecoderPool
from nxswriter.Element import Element
from nxswriter.EField import EField
from nxswriter.DataSourceFactory import DataSourceFactory
from nxswriter.Errors import DataSourceSetupError
from nxswriter.DataSourcePool import DataSourcePool
from nxswriter.Types import Converters

import threading

import _thread as thread

#: (:obj:`bool`) tango bug #213 flag related to EncodedAttributes in python3
PYTG_BUG_213 = False
try:
    PYTGMAJOR, PYTGMINOR, PYTGPATCH = list(
        map(int, tango.__version__.split(".")[:3]))
    if PYTGMAJOR <= 9:
        if PYTGMAJOR == 9:
            if PYTGMINOR < 2:
                PYTG_BUG_213 = True
            elif PYTGMINOR == 2 and PYTGPATCH <= 4:
                PYTG_BUG_213 = True
        else:
            PYTG_BUG_213 = True
except Exception:
    pass


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test pool
class pool(object):

    def __init__(self):
        self.common = {}
        self.lock = threading.Lock()
        self.counter = 0

# test fixture


class TangoSourceTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._simps = SimpleServerSetUp.SimpleServerSetUp()
        self._simps2 = SimpleServerSetUp.SimpleServerSetUp(
            "stestp09/testss/s2r228", "S2")

        self._tfname = "doc"
        self._fname = "test.h5"
        self._nxDoc = None
        self._eDoc = None
        self._fattrs = {"short_name": "test", "units": "m"}
        self._gname = "testDoc"
        self._gtype = "NXentry"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

        self._dbhost = None
        self._dbport = None

    # test starter
    # \brief Common set up
    def setUp(self):
        self._simps.setUp()
        self._simps2.setUp()
        self._dbhost = self._simps.dp.get_db_host()
        self._dbport = self._simps.dp.get_db_port()
        # file handle
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        self._simps2.tearDown()
        self._simps.tearDown()

    # Exception tester
    # \param exception expected exception
    # \param method called method
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error = False
            method(*args, **kwargs)
        except Exception:
            error = True
        self.assertEqual(error, True)

    # constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        ds = TangoSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertTrue(isinstance(ds.member, TgMember))
        self.assertEqual(ds.member.name, None)
        self.assertEqual(ds.member.memberType, 'attribute')
        self.assertEqual(ds.member.encoding, None)
        self.assertEqual(ds.device, None)
        self.assertEqual(ds.group, None)

    # __str__ test
    # \brief It tests default settings
    def test_str_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dname = 'writer'
        device = 'p09/tdw/r228'
        mtype = 'attribute'
        ds = TangoSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), " TANGO Device %s : %s (%s)" %
                         (None, None, "attribute"))

        ds.device = device
        ds.member.name = None
        ds.memberType = None
        self.assertEqual(ds.__str__(), " TANGO Device %s : %s (%s)" %
                         (device, None, "attribute"))

        ds.device = None
        ds.member.name = dname
        ds.memberType = None
        self.assertEqual(ds.__str__(), " TANGO Device %s : %s (%s)" %
                         (None, dname, "attribute"))

        ds.device = None
        ds.member.name = None
        ds.memberType = mtype
        self.assertEqual(
            ds.__str__(), " TANGO Device %s : %s (%s)" % (None, None, mtype))

        ds.device = device
        ds.member.name = dname
        ds.memberType = mtype
        self.assertEqual(ds.__str__(), " TANGO Device %s : %s (%s)" %
                         (device, dname, mtype))

    # Data check
    # \brief It check the source Data
    # \param data  tested data
    # \param format data format
    # \param value data value
    # \param ttype data Tango type
    # \param shape data shape
    # \param shape data shape
    # \param encoding data encoding
    # \param encoding data encoding
    # \param decoders data decoders
    # \param error data error
    def checkData(self, data, format, value, ttype, shape, encoding=None,
                  decoders=None, error=0):
        self.assertEqual(data["rank"], format)
        self.assertEqual(data["tangoDType"], ttype)
        self.assertEqual(data["shape"], shape)
        if encoding is not None:
            self.assertEqual(data["encoding"], encoding)
        if decoders is not None:
            self.assertEqual(data["decoders"], decoders)
        if format == 'SCALAR':
            if error:
                self.assertTrue(abs(data["value"] - value) <= error)
            else:
                self.assertEqual(data["value"], value)
        elif format == 'SPECTRUM':
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                if error:
                    self.assertTrue(abs(data["value"][i] - value[i]) <= error)
                else:
                    self.assertEqual(data["value"][i], value[i])
        else:
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                self.assertEqual(len(data["value"][i]), len(value[i]))
                for j in range(len(value[i])):
                    if error:
                        self.assertTrue(
                            abs(data["value"][i][j] - value[i][j]) <= error)
                    else:
                        self.assertEqual(data["value"][i][j], value[i][j])

    # setup test
    # \brief It tests default settings
    def test_setup_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dname = 'writer'
        device = 'stestp09/testss/s1r228'
        ctype = 'command'
        atype = 'attribute'
        host = self._dbhost
        port = '10000'
        encoding = 'UTF8'
        group = 'common_motors'

        ds = TangoSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.setup, "<datasource/>")

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource> <device name='%s'/> </datasource>" % device)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource> <record name='%s'/> </datasource>" % dname)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource> <record/>  <device/> </datasource>")
        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        ds.setup(
            "<datasource> <record name='%s'/> <device name='%s'/> "
            "</datasource>" %
            (dname, device))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        ds.setup(
            "<datasource> <record name='%s'/> "
            "<device name='%s' member ='%s'/> </datasource>" %
            (dname, device, ctype))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.member.memberType, ctype)
        self.assertEqual(ds.member.encoding, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.setup("<datasource> <record name='%s'/> "
                 "<device name='%s' member ='%s'/> </datasource>" %
                 (dname, device, 'strange'))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        ds.setup("<datasource> <record name='%s'/> "
                 "<device name='%s' hostname='%s'/> </datasource>" %
                 (dname, device, host))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None

        ds.setup("<datasource> <record name='%s'/> "
                 "<device name='%s' hostname='%s' port='%s'/> </datasource>" %
                 (dname, device, host, port))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, "%s:%s/%s" % (host, port, device))
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.member.encoding, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.member.encoding = None
        ds.group = None
        ds.setup("<datasource> <record name='%s'/> "
                 "<device name='%s' encoding='%s'/> </datasource>" %
                 (dname, device, encoding))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, encoding)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.member.encoding = None
        ds.setup("<datasource> <record name='%s'/> "
                 "<device name='%s' encoding='%s' group= '%s'/> "
                 "</datasource>" %
                 (dname, device, encoding, group))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.group, group)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, encoding)

    # setup test
    # \brief It tests default settings
    def test_setup_client_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dname = 'Writer'
        device = 'stestp09/testss/s1r228'
        wdevice = 'wtestp09/testss/s1r228'
        ctype = 'command'
        atype = 'attribute'
        host = self._dbhost
        port = '10000'
        encoding = 'UTF8'
        # group = 'common_motors'

        ds = TangoSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.setup, "<datasource/>")

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource> <device name='%s' group='__CLIENT__'/> "
            "</datasource>" % device)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource> <record name='%s' group='__CLIENT__'/> "
            "</datasource>" % dname)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource> <record/>  <device group='__CLIENT__'/> "
            "</datasource>")
        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        ds.setup(
            "<datasource> <record name='%s'/> <device name='%s' "
            "group='__CLIENT__'/> </datasource>" %
            (dname, device))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        ds.setup(
            "<datasource> <record name='%s'/> <device name='%s' "
            "member ='%s' group='__CLIENT__'/> </datasource>" %
            (dname, device, ctype))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.member.memberType, ctype)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.member.encoding, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.setup(
            "<datasource> <record name='%s'/> <device name='%s' "
            "member ='%s' group='__CLIENT__'/> </datasource>" %
            (dname, device, 'strange'))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.client, None)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.group = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' "
                 "hostname='%s' group='__CLIENT__'/> </datasource>" %
                 (dname, device, host))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None

        ds.setup("<datasource> <record name='%s'/> <device name='%s' "
                 "hostname='%s' port='%s' group='__CLIENT__'/> </datasource>" %
                 (dname, device, host, port))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, "%s:%s/%s" % (host, port, device))
        try:
            self.assertEqual(
                ds.client, "%s:%s/%s/%s" %
                (host, port, device, dname.lower()))
        except Exception:
            self.assertEqual(
                ds.client, "%s:%s/%s/%s" % (
                    host.split(".")[0], port, device, dname.lower()))

        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None

        ds.setup("<datasource> <record name='%s'/> <device name='%s' "
                 "hostname='%s' port='%s' group='__CLIENT__'/> </datasource>" %
                 (dname, device, host, port))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, "%s:%s/%s" % (host, port, device))
        try:
            self.assertEqual(ds.client, "%s:%s/%s/%s" %
                             (host, port, device, dname.lower()))
        except Exception:
            self.assertEqual(ds.client, "%s:%s/%s/%s" %
                             (host.split(".")[0], port, device, dname.lower()))
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, None)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.member.encoding = None
        ds.group = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' "
                 "encoding='%s' group='__CLIENT__'/> </datasource>" %
                 (dname, device, encoding))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        try:
            self.assertEqual(ds.client, "%s:%s/%s/%s" %
                             (host, port, device, dname.lower()))
        except Exception:
            self.assertEqual(ds.client, "%s:%s/%s/%s" %
                             (host.split('.')[0], port, device, dname.lower()))
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, encoding)
        self.assertEqual(ds.group, None)

        ds.device = None
        ds.member.name = None
        ds.member.memberType = None
        ds.member.encoding = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' "
                 "encoding='%s' group='__CLIENT__'/> </datasource>" %
                 (dname, device, encoding))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, device)
        try:
            self.assertEqual(ds.client, "%s:%s/%s/%s" %
                             (host, port, device, dname.lower()))
        except Exception:
            self.assertEqual(ds.client, "%s:%s/%s/%s" %
                             (host.split('.')[0], port, device, dname.lower()))

        self.assertEqual(ds.group, None)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, encoding)

        ds.device = None
        ds.client = None
        ds.member.name = None
        ds.member.memberType = None
        ds.member.encoding = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' "
                 "encoding='%s' group='__CLIENT__'/> </datasource>" %
                 (dname, wdevice, encoding))
        self.assertEqual(ds.member.name, dname)
        self.assertEqual(ds.device, wdevice)
        try:
            self.assertEqual(ds.client, None)
        except Exception:
            self.assertEqual(ds.client, None)

        self.assertEqual(ds.group, None)
        self.assertEqual(ds.member.memberType, atype)
        self.assertEqual(ds.member.encoding, encoding)

    # getData test
    # \brief It tests default settings
    def test_getData_client_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = TangoSource()
        el.device = 'stestp09/testss/s1r228'
        el.memberType = 'attribute'
        el.member.name = 'ScalarString'
        el.client = 'stestp09/testss/s1r228/scalarstring'
        self.assertTrue(isinstance(el, object))
        dt = el.getData()
        self.checkData(dt, "SCALAR", "Hello!", "DevString", [1, 0], None, None)

        el = TangoSource()
        el.group = 'bleble'
        el.device = 'stestp09/testss/s1r228'
        el.memberType = 'attribute'
        el.client = 'stestp09/testss/s1r228/scalarstring'
        el.member.name = 'ScalarString'
        self.assertTrue(isinstance(el, object))
        self.myAssertRaise(DataSourceSetupError, el.getData)

    # getData test
    # \brief It tests default settings
    def test_getData_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = TangoSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.getData(), None)

        el = TangoSource()
        el.device = 'stestp09/testss/s1r228'
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.getData(), None)

        el = TangoSource()
        el.device = 'stestp09/testss/s1r228'
        el.memberType = 'attribute'
        el.member.name = 'ScalarString'
        self.assertTrue(isinstance(el, object))
        dt = el.getData()
        self.checkData(dt, "SCALAR", "Hello!", "DevString", [1, 0], None, None)

        el = TangoSource()
        el.group = 'bleble'
        el.device = 'stestp09/testss/s1r228'
        el.memberType = 'attribute'
        el.member.name = 'ScalarString'
        self.assertTrue(isinstance(el, object))
        self.myAssertRaise(DataSourceSetupError, el.getData)

    # getData test
    # \brief It tests default settings
    def test_setDataSources_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = TangoSource()
        self.assertTrue(isinstance(el, object))
        pl = pool()
        self.assertTrue('TANGO' not in pl.common.keys())

        self.assertEqual(el.setDataSources(pl), None)
        self.assertTrue('TANGO' in pl.common.keys())
        self.assertEqual(pl.common['TANGO'], {})

        el = TangoSource()
        el.device = 'stestp09/testss/s1r228'
        self.assertTrue(isinstance(el, object))
        self.assertTrue('TANGO' in pl.common.keys())
        self.assertEqual(el.setDataSources(pl), None)
        self.assertTrue('TANGO' in pl.common.keys())
        self.assertEqual(pl.common['TANGO'], {})

        el = TangoSource()
        el.group = 'bleble'
        el.device = 'stestp09/testss/s1r228'
        el.memberType = 'attribute'
        el.member.name = 'ScalarString'
        self.assertTrue(isinstance(el, object))
        self.assertTrue('TANGO' in pl.common.keys())
        self.assertEqual(el.setDataSources(pl), None)
        self.assertTrue('TANGO' in pl.common.keys())
        cm = pl.common['TANGO']
        self.assertEqual(len(cm), 1)
        gr = cm['bleble']
        self.assertTrue(isinstance(gr, TgGroup))
# TODO proxy [setup] and ..

        el = TangoSource()
        el.group = 'bleble2'
        el.device = 'stestp09/testss/s2r228'
        el.memberType = 'attribute'
        el.member.name = 'ScalarString'
        self.assertTrue(isinstance(el, object))
        self.assertTrue('TANGO' in pl.common.keys())
        self.assertEqual(el.setDataSources(pl), None)
        self.assertTrue('TANGO' in pl.common.keys())
        cm = pl.common['TANGO']
        self.assertEqual(len(cm), 2)
        self.assertTrue(isinstance(cm['bleble'], TgGroup))
        self.assertTrue(isinstance(cm['bleble2'], TgGroup))

        gr = cm['bleble2']

        self.assertEqual(type(gr.lock), thread.LockType)
        self.assertEqual(gr.counter, 0)
        self.assertEqual(len(gr.devices), 1)
        dv = gr.devices[el.device]
        self.assertTrue(isinstance(dv, TgDevice))
        self.assertEqual(dv.device, el.device)
        self.assertEqual(dv.device, el.device)
        self.assertEqual(dv.proxy, None)
        self.assertEqual(dv.attributes, [el.member.name])
        self.assertEqual(dv.commands, [])
        self.assertEqual(dv.properties, [])

        mbs = dv.members
        self.assertEqual(len(mbs), 1)
        self.assertTrue(isinstance(mbs[el.member.name], TgMember))
        self.assertEqual(mbs[el.member.name].name, el.member.name)
        self.assertEqual(mbs[el.member.name].memberType, el.member.memberType)
        self.assertEqual(mbs[el.member.name].encoding, el.member.encoding)

    # getData test
    # \brief It tests default settings
    def test_getData_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])

        arr = dict(arr1, **(arr2))

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [1, 0], None, None,
                arr[k][3] if len(arr[k]) > 3
                else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                el = TangoSource()
                el.device = 'stestp09/testss/s1r228'
                el.member.memberType = 'attribute'
                el.member.name = k
                el.member.encoding = arr3[k][2][0]
                dp = DecoderPool()
                dt = el.setDecoders(dp)
                dt = el.getData()
                self.checkData(dt, "SCALAR", arr3[k][2], arr3[k][1], [1, 0],
                               arr3[k][2][0], dp)

    # getData test
    # \brief It tests default settings
    def test_getData_client_scalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True, "DevBoolean", False],
            "ScalarUChar": ["uint8", "DevUChar", 23, "DevLong64", 443],
            "ScalarShort": ["int16", "DevShort", -123, "DevLong64", 234],
            "ScalarUShort": ["uint16", "DevUShort", 1234, "DevLong64", 23],
            "ScalarLong": ["int64", "DevLong", -124, "DevLong64", -23],
            "ScalarULong": ["uint64", "DevULong", 234, "DevLong64", 23],
            "ScalarLong64": ["int64", "DevLong64", 234, "DevLong64", -13],
            "ScalarULong64": ["uint64", "DevULong64", 23, "DevLong64", 223],
            "ScalarFloat": ["float32", "DevFloat", 12.234, "DevDouble",
                            -12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02,
                             "DevDouble", +2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue", "DevString",
                             "MyFaTrue"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON,
                      "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded", (
                    "UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])

        arr = dict(arr1, **(arr2))

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [1, 0], None, None,
                arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                gjson = '{"data":{"%s":"%s"}}' % (sclient, arr[k][4])
            elif k == "ScalarBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][4]).lower())
            else:
                gjson = '{"data":{"%s":%s}}' % (sclient, arr[k][4])
            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()
            self.checkData(dt, "SCALAR", arr[k][4],
                           arr[k][3], [], None, None,
                           arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "ScalarString":
                ljson = '{"data":{"%s":"%s"}}' % (sclient, arr[k][4])
            elif k == "ScalarBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][4]).lower())
            else:
                ljson = '{"data":{"%s":%s}}' % (sclient, arr[k][4])
            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(dt, "SCALAR", arr[k][4],
                           arr[k][3], [], None, None,
                           arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "ScalarString":
                ljson = '{"data":{"%s":"%s"}}' % (sclient, arr[k][4])
            elif k == "ScalarBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][4]).lower())
            else:
                ljson = '{"data":{"%s":%s}}' % (sclient, arr[k][4])
            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(dt, "SCALAR", arr[k][4],
                           arr[k][3], [], None, None,
                           arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "ScalarString":
                gjson = '{"data":{"%s":"%s"}}' % (sclient, arr[k][2])
                ljson = '{"data":{"%s":"%s"}}' % (sclient, arr[k][4])
            elif k == "ScalarBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][2]).lower())
                ljson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][4]).lower())
            else:
                gjson = '{"data":{"%s":%s}}' % (sclient, arr[k][2])
                ljson = '{"data":{"%s":%s}}' % (sclient, arr[k][4])
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(dt, "SCALAR", arr[k][4],
                           arr[k][3], [], None, None,
                           arr[k][5] if len(arr[k]) > 5 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                el = TangoSource()
                el.device = 'stestp09/testss/s1r228'
                el.member.memberType = 'attribute'
                el.member.name = k
                el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
                sclient = 'stestp09/testss/s1r228/'
                el.member.encoding = arr3[k][2][0]
                dp = DecoderPool()
                dt = el.setDecoders(dp)
                dt = el.getData()
                self.checkData(dt, "SCALAR", arr3[k][
                               2], arr3[k][1], [1, 0], arr3[k][2][0], dp)

    # getData test
    # \brief It tests default settings
    def test_getData_client_scalar_sar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True, "DevBoolean", False],
            "ScalarUChar": ["uint8", "DevUChar", 23, "DevLong64", 443],
            "ScalarShort": ["int16", "DevShort", -123, "DevLong64", 234],
            "ScalarUShort": ["uint16", "DevUShort", 1234, "DevLong64", 23],
            "ScalarLong": ["int64", "DevLong", -124, "DevLong64", -23],
            "ScalarULong": ["uint64", "DevULong", 234, "DevLong64", 23],
            "ScalarLong64": ["int64", "DevLong64", 234, "DevLong64", -13],
            "ScalarULong64": ["uint64", "DevULong64", 23, "DevLong64", 223],
            "ScalarFloat": ["float32", "DevFloat", 12.234, "DevDouble",
                            -12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02,
                             "DevDouble", +2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue", "DevString",
                             "MyFaTrue"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON,
                      "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])

        arr = dict(arr1, **(arr2))

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [1, 0], None, None,
                arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                gjson = '{"data":{"%s":"%s"}}' % (el.client, arr[k][4])
            elif k == "ScalarBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][4]).lower())
            else:
                gjson = '{"data":{"%s":%s}}' % (el.client, arr[k][4])
            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][4],
                arr[k][3], [], None, None, arr[k][5]
                if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                ljson = '{"data":{"%s":"%s"}}' % (el.client, arr[k][4])
            elif k == "ScalarBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][4]).lower())
            else:
                ljson = '{"data":{"%s":%s}}' % (el.client, arr[k][4])
            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][4],
                arr[k][3], [], None, None, arr[k][5]
                if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                ljson = '{"data":{"%s":"%s"}}' % (el.client, arr[k][4])
            elif k == "ScalarBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][4]).lower())
            else:
                ljson = '{"data":{"%s":%s}}' % (el.client, arr[k][4])
            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][4],
                arr[k][3], [], None, None, arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                gjson = '{"data":{"%s":"%s"}}' % (el.client, arr[k][2])
                ljson = '{"data":{"%s":"%s"}}' % (el.client, arr[k][4])
            elif k == "ScalarBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][2]).lower())
                ljson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][4]).lower())
            else:
                gjson = '{"data":{"%s":%s}}' % (el.client, arr[k][2])
                ljson = '{"data":{"%s":%s}}' % (el.client, arr[k][4])
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][4],
                arr[k][3], [], None, None, arr[k][5] if len(arr[k]) > 5 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                el = TangoSource()
                el.device = 'stestp09/testss/s1r228'
                el.member.memberType = 'attribute'
                el.member.name = k
                el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
                el.member.encoding = arr3[k][2][0]
                dp = DecoderPool()
                dt = el.setDecoders(dp)
                dt = el.getData()
                self.checkData(dt, "SCALAR", arr3[k][
                               2], arr3[k][1], [1, 0], arr3[k][2][0], dp)

    # getData test
    # \brief It tests default settings
    def test_getData_client_scalar_tango(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True, "DevBoolean", False],
            "ScalarUChar": ["uint8", "DevUChar", 23, "DevLong64", 443],
            "ScalarShort": ["int16", "DevShort", -123, "DevLong64", 234],
            "ScalarUShort": ["uint16", "DevUShort", 1234, "DevLong64", 23],
            "ScalarLong": ["int64", "DevLong", -124, "DevLong64", -23],
            "ScalarULong": ["uint64", "DevULong", 234, "DevLong64", 23],
            "ScalarLong64": ["int64", "DevLong64", 234, "DevLong64", -13],
            "ScalarULong64": ["uint64", "DevULong64", 23, "DevLong64", 223],
            "ScalarFloat": ["float32", "DevFloat", 12.234, "DevDouble",
                            -12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02,
                             "DevDouble", +2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue", "DevString",
                             "MyFaTrue"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON,
                      "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])

        arr = dict(arr1, **(arr2))

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [1, 0], None, None,
                arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                gjson = '{"data":{"tango://%s":"%s"}}' % (el.client, arr[k][4])
            elif k == "ScalarBoolean":
                gjson = '{"data":{"tango://%s":%s}}' % (
                    el.client, str(arr[k][4]).lower())
            else:
                gjson = '{"data":{"tango://%s":%s}}' % (el.client, arr[k][4])
            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][4],
                arr[k][3], [], None, None, arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                ljson = '{"data":{"tango://%s":"%s"}}' % (el.client, arr[k][4])
            elif k == "ScalarBoolean":
                ljson = '{"data":{"tango://%s":%s}}' % (
                    el.client, str(arr[k][4]).lower())
            else:
                ljson = '{"data":{"tango://%s":%s}}' % (el.client, arr[k][4])
            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][4],
                arr[k][3], [], None, None, arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                ljson = '{"data":{"tango://%s":"%s"}}' % (el.client, arr[k][4])
            elif k == "ScalarBoolean":
                ljson = '{"data":{"tango://%s":%s}}' % (
                    el.client, str(arr[k][4]).lower())
            else:
                ljson = '{"data":{"tango://%s":%s}}' % (el.client, arr[k][4])
            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][4],
                arr[k][3], [], None, None, arr[k][5] if len(arr[k]) > 5 else 0)

        for k in arr1:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            if k == "ScalarString":
                gjson = '{"data":{"tango://%s":"%s"}}' % (el.client, arr[k][2])
                ljson = '{"data":{"tango://%s":"%s"}}' % (el.client, arr[k][4])
            elif k == "ScalarBoolean":
                gjson = '{"data":{"tango://%s":%s}}' % (
                    el.client, str(arr[k][2]).lower())
                ljson = '{"data":{"tango://%s":%s}}' % (
                    el.client, str(arr[k][4]).lower())
            else:
                gjson = '{"data":{"tango://%s":%s}}' % (el.client, arr[k][2])
                ljson = '{"data":{"tango://%s":%s}}' % (el.client, arr[k][4])
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][4],
                arr[k][3], [], None, None, arr[k][5] if len(arr[k]) > 5 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                el = TangoSource()
                el.device = 'stestp09/testss/s1r228'
                el.member.memberType = 'attribute'
                el.member.name = k
                el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
                el.member.encoding = arr3[k][2][0]
                dp = DecoderPool()
                dt = el.setDecoders(dp)
                dt = el.getData()
                self.checkData(dt, "SCALAR", arr3[k][
                               2], arr3[k][1], [1, 0], arr3[k][2][0], dp)

    # getData test
    # \brief It tests default settings
    def test_getData_scalar_tl(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])

        arr = dict(arr1, **(arr2))

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k.lower()
            dt = el.getData()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [1, 0], None, None,
                arr[k][3] if len(arr[k]) > 3 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                el = TangoSource()
                el.device = 'stestp09/testss/s1r228'
                el.member.memberType = 'attribute'
                el.member.name = k.lower()
                el.member.encoding = arr3[k][2][0]
                dp = DecoderPool()
                dt = el.setDecoders(dp)
                dt = el.getData()
                self.checkData(dt, "SCALAR", arr3[k][
                               2], arr3[k][1], [1, 0], arr3[k][2][0], dp)

    # getData test
    # \brief It tests default settings
    def test_getData_scalar_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
        }

        arr1b = {
            "ScalarBoolean": ["bool", "DevBoolean", False],
            "ScalarUChar": ["uint8", "DevUChar", 13],
            "ScalarShort": ["int16", "DevShort", -233],
            "ScalarUShort": ["uint16", "DevUShort", 3114],
            "ScalarLong": ["int64", "DevLong", -144],
            "ScalarULong": ["uint64", "DevULong", 134],
            "ScalarLong64": ["int64", "DevLong64", 214],
            "ScalarULong64": ["uint64", "DevULong64", 14],
            "ScalarFloat": ["float32", "DevFloat", 11.133, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.111173e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTsdf"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        # counter = self.__rnd.randint(-2, 10)

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])
        for k in arr1b:
            self._simps2.dp.write_attribute(k, arr1b[k][2])

        arr = dict(arr1, **(arr2))
        arrb = dict(arr1b, **(arr2))

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'attribute'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'attribute'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)

        dt = el[k].getData()
        dt = el2[k].getData()
        for k in arr1b:
            self._simps.dp.write_attribute(k, arr1b[k][2])
        for k in arr1:
            self._simps2.dp.write_attribute(k, arr1[k][2])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arr[k][2], arr[k][1],
                           [1, 0], None, None,
                           arr[k][3] if len(arr[k]) > 3 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(
                dt, "SCALAR", arrb[k][2], arrb[k][1], [1, 0], None, None,
                arrb[k][3] if len(arrb[k]) > 3 else 0)

        pl.counter = 2

        for k in arr:
            dt = el[k].getData()
            self.checkData(
                dt, "SCALAR", arrb[k][2], arrb[k][1], [1, 0], None, None,
                arrb[k][3] if len(arrb[k]) > 3 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [1, 0], None, None,
                arr[k][3] if len(arr[k]) > 3 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                print(k)
                el = TangoSource()
                el.device = 'stestp09/testss/s1r228'
                el.member.memberType = 'attribute'
                el.member.name = k
                el.member.encoding = arr3[k][2][0]
                dp = DecoderPool()
                dt = el.setDecoders(dp)
                dt = el.getData()
                self.checkData(
                    dt, "SCALAR", arr3[k][2], arr3[k][1], [1, 0],
                    arr3[k][2][0],
                    dp)

    # getData test
    # \brief It tests default settings
    def test_getData_scalar_group_tl(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
        }

        arr1b = {
            "ScalarBoolean": ["bool", "DevBoolean", False],
            "ScalarUChar": ["uint8", "DevUChar", 13],
            "ScalarShort": ["int16", "DevShort", -233],
            "ScalarUShort": ["uint16", "DevUShort", 3114],
            "ScalarLong": ["int64", "DevLong", -144],
            "ScalarULong": ["uint64", "DevULong", 134],
            "ScalarLong64": ["int64", "DevLong64", 214],
            "ScalarULong64": ["uint64", "DevULong64", 14],
            "ScalarFloat": ["float32", "DevFloat", 11.133, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.111173e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTsdf"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        # counter = self.__rnd.randint(-2, 10)

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])
        for k in arr1b:
            self._simps2.dp.write_attribute(k, arr1b[k][2])

        arr = dict(arr1, **(arr2))
        arrb = dict(arr1b, **(arr2))

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'attribute'
            el[k].member.name = k.lower()
            self.assertEqual(el[k].setDataSources(pl), None)

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'attribute'
            el2[k].member.name = k.lower()
            self.assertEqual(el2[k].setDataSources(pl), None)

        dt = el[k].getData()
        dt = el2[k].getData()
        for k in arr1b:
            self._simps.dp.write_attribute(k, arr1b[k][2])
        for k in arr1:
            self._simps2.dp.write_attribute(k, arr1[k][2])

        for k in arr:
            dt = el[k].getData()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [
                    1, 0], None, None, arr[k][3] if len(arr[k]) > 3 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(
                dt, "SCALAR", arrb[k][2], arrb[k][1], [
                    1, 0], None, None, arrb[k][3] if len(arrb[k]) > 3 else 0)

        pl.counter = 2

        for k in arr:
            dt = el[k].getData()
            self.checkData(
                dt, "SCALAR", arrb[k][2], arrb[k][1], [
                    1, 0], None, None, arrb[k][3] if len(arrb[k]) > 3 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(
                dt, "SCALAR", arr[k][2], arr[k][1], [1, 0],
                None, None, arr[k][3] if len(arr[k]) > 3 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                el = TangoSource()
                el.device = 'stestp09/testss/s1r228'
                el.member.memberType = 'attribute'
                el.member.name = k
                el.member.encoding = arr3[k][2][0]
                dp = DecoderPool()
                dt = el.setDecoders(dp)
                dt = el.getData()
                self.checkData(dt, "SCALAR", arr3[k][
                               2], arr3[k][1], [1, 0], arr3[k][2][0], dp)

    # getData test
    # \brief It tests default settings
    def test_getData_scalar_group_noorder(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr1 = {
            "ScalarBoolean": ["bool", "DevBoolean", True],
            "ScalarUChar": ["uint8", "DevUChar", 23],
            "ScalarShort": ["int16", "DevShort", -123],
            "ScalarUShort": ["uint16", "DevUShort", 1234],
            "ScalarLong": ["int64", "DevLong", -124],
            "ScalarULong": ["uint64", "DevULong", 234],
            "ScalarLong64": ["int64", "DevLong64", 234],
            "ScalarULong64": ["uint64", "DevULong64", 23],
            "ScalarFloat": ["float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.456673e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTrue"],
        }

        arr1b = {
            "ScalarBoolean": ["bool", "DevBoolean", False],
            "ScalarUChar": ["uint8", "DevUChar", 13],
            "ScalarShort": ["int16", "DevShort", -233],
            "ScalarUShort": ["uint16", "DevUShort", 3114],
            "ScalarLong": ["int64", "DevLong", -144],
            "ScalarULong": ["uint64", "DevULong", 134],
            "ScalarLong64": ["int64", "DevLong64", 214],
            "ScalarULong64": ["uint64", "DevULong64", 14],
            "ScalarFloat": ["float32", "DevFloat", 11.133, 1e-5],
            "ScalarDouble": ["float64", "DevDouble", -2.111173e+02, 1e-14],
            "ScalarString": ["string", "DevString", "MyTsdf"],
        }

        arr2 = {
            "State": ["string", "DevState", tango._tango.DevState.ON],
        }

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        # counter = self.__rnd.randint(-2, 10)

        for k in arr1:
            self._simps.dp.write_attribute(k, arr1[k][2])
        for k in arr1b:
            self._simps2.dp.write_attribute(k, arr1b[k][2])

        arr = dict(arr1, **(arr2))
        arrb = dict(arr1b, **(arr2))

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'attribute'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)
            dt = el[k].getData()

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'attribute'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)
            dt = el2[k].getData()

        dt = el[k].getData()
        dt = el2[k].getData()
        for k in arr1b:
            self._simps.dp.write_attribute(k, arr1b[k][2])
        for k in arr1:
            self._simps2.dp.write_attribute(k, arr1[k][2])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arr[k][2], arr[k][1], [
                           1, 0], None, None, arr[k][3]
                           if len(arr[k]) > 3 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", arrb[k][2], arrb[k][1], [
                           1, 0], None, None, arrb[k][3]
                           if len(arrb[k]) > 3 else 0)

        pl.counter = 2

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arrb[k][2], arrb[k][1], [
                           1, 0], None, None, arrb[k][3]
                           if len(arrb[k]) > 3 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", arr[k][2], arr[k][1], [
                           1, 0], None, None, arr[k][3]
                           if len(arr[k]) > 3 else 0)

        if not PYTG_BUG_213:
            for k in arr3:
                el = TangoSource()
                el.device = 'stestp09/testss/s1r228'
                el.member.memberType = 'attribute'
                el.member.name = k
                el.member.encoding = arr3[k][2][0]
                dp = DecoderPool()
                dt = el.setDecoders(dp)
                dt = el.getData()
                self.checkData(dt, "SCALAR", arr3[k][
                               2], arr3[k][1], [1, 0], arr3[k][2][0], dp)

    # getData test
    # \brief It tests default settings
    def test_getData_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0]],
            "SpectrumUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "SpectrumShort": ["int16", "DevShort", -123, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1234, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -124, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 234, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 234, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 23, [1, 0]],
            "SpectrumFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", -2.456673e+02,
                               [1, 0], 1e-14],
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
        }

        for k in arr:

            if arr[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arr[k][2] = [arr[k][2] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0], 0]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            dt = el.getData()
            self.checkData(dt, "SPECTRUM", arr[k][2], arr[k][1], arr[
                           k][3], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_client_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0],
                                "DevBoolean", False],
            "SpectrumUChar": ["uint8", "DevUChar", 23, [1, 0],
                              "DevLong64", 2],
            "SpectrumShort": ["int16", "DevShort", -123, [1, 0],
                              "DevLong64", -13],
            "SpectrumUShort": ["uint16", "DevUShort", 1234, [1, 0],
                               "DevLong64", 134],
            "SpectrumLong": ["int64", "DevLong", -124, [1, 0],
                             "DevLong64", -1213],
            "SpectrumULong": ["uint64", "DevULong", 234, [1, 0],
                              "DevLong64", 23],
            "SpectrumLong64": ["int64", "DevLong64", 234, [1, 0],
                               "DevLong64", 24],
            "SpectrumULong64": ["uint64", "DevULong64", 23, [1, 0],
                                "DevLong64", 2],
            "SpectrumFloat": ["float32", "DevFloat", 12.23, [1, 0],
                              "DevDouble", 1.234, 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", -2.456673e+02,
                               [1, 0], "DevDouble", -2.4563e+02, 1e-14],
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0],
                               "DevString", "MyTsfdrue"],
        }

        for k in arr:
            if arr[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arr[k][2] = [arr[k][2] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
                arr[k][5] = [arr[k][5] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                             for c in range(mlen[0])]
                arr[k][5] = [("true" if self.__rnd.randint(0, 1) else "false")
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0], 0]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            dt = el.getData()
            self.checkData(dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "SpectrumString":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][5]).replace("'", "\""))
            elif k == "SpectrumBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + ''.join([a + ',' for a in arr[k][5]])[:-1] + "]")
            else:
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + ''.join([str(a) + ','
                                   for a in arr[k][5]])[:-1] + "]")

            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()
            if arr[k][1] == "DevBoolean":
                self.checkData(
                    dt, "SPECTRUM", [Converters.toBool(a) for a in arr[k][5]],
                    arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(
                    dt, "SPECTRUM", arr[k][5], arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "SpectrumString":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][5]).replace("'", "\""))
            elif k == "SpectrumBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + ''.join([a + ',' for a in arr[k][5]])[:-1] + "]")
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + ''.join([str(a) + ','
                                   for a in arr[k][5]])[:-1] + "]")

            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            if arr[k][1] == "DevBoolean":
                self.checkData(
                    dt, "SPECTRUM", [Converters.toBool(a) for a in arr[k][5]],
                    arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(
                    dt, "SPECTRUM", arr[k][5], arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "SpectrumString":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][2]).replace("'", "\""))
                ljson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][5]).replace("'", "\""))
            elif k == "SpectrumBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + ''.join([a + ',' for a in arr[k][5]])[:-1] + "]")
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + ''.join([str(a).lower() + ','
                                   for a in arr[k][2]])[:-1] + "]")
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + ''.join([str(a) + ','
                                   for a in arr[k][5]])[:-1] + "]")
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + ''.join([str(a) + ','
                                   for a in arr[k][2]])[:-1] + "]")

            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            if arr[k][1] == "DevBoolean":
                self.checkData(
                    dt, "SPECTRUM", [Converters.toBool(a) for a in arr[k][5]],
                    arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(
                    dt, "SPECTRUM", arr[k][5], arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_client_spectrum_sar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0],
                                "DevBoolean", False],
            "SpectrumUChar": ["uint8", "DevUChar", 23, [1, 0],
                              "DevLong64", 2],
            "SpectrumShort": ["int16", "DevShort", -123, [1, 0],
                              "DevLong64", -13],
            "SpectrumUShort": ["uint16", "DevUShort", 1234, [1, 0],
                               "DevLong64", 134],
            "SpectrumLong": ["int64", "DevLong", -124, [1, 0],
                             "DevLong64", -1213],
            "SpectrumULong": ["uint64", "DevULong", 234, [1, 0],
                              "DevLong64", 23],
            "SpectrumLong64": ["int64", "DevLong64", 234, [1, 0],
                               "DevLong64", 24],
            "SpectrumULong64": ["uint64", "DevULong64", 23, [1, 0],
                                "DevLong64", 2],
            "SpectrumFloat": ["float32", "DevFloat", 12.23, [1, 0],
                              "DevDouble", 1.234, 1e-5],
            "SpectrumDouble": ["float64", "DevDouble", -2.456673e+02,
                               [1, 0], "DevDouble", -2.4563e+02, 1e-14],
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0],
                               "DevString", "MyTsfdrue"],
        }

        for k in arr:
            if arr[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arr[k][2] = [arr[k][2] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
                arr[k][5] = [arr[k][5] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                             for c in range(mlen[0])]
                arr[k][5] = [("true" if self.__rnd.randint(0, 1) else "false")
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0], 0]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            dt = el.getData()
            self.checkData(dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            # sclient = 'stestp09/testss/s1r228'
            if k == "SpectrumString":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][5]).replace("'", "\""))
            elif k == "SpectrumBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + ''.join([a + ',' for a in arr[k][5]])[:-1] + "]")
            else:
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + ''.join([str(a) + ','
                                   for a in arr[k][5]])[:-1] + "]")

            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()
            if arr[k][1] == "DevBoolean":
                self.checkData(
                    dt, "SPECTRUM", [Converters.toBool(a) for a in arr[k][5]],
                    arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(
                    dt, "SPECTRUM", arr[k][5], arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            # sclient = 'stestp09/testss/s1r228'
            if k == "SpectrumString":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][5]).replace("'", "\""))
            elif k == "SpectrumBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + ''.join([a + ',' for a in arr[k][5]])[:-1] + "]")
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + ''.join([str(a) + ','
                                   for a in arr[k][5]])[:-1] + "]")

            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            if arr[k][1] == "DevBoolean":
                self.checkData(
                    dt, "SPECTRUM", [Converters.toBool(a) for a in arr[k][5]],
                    arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(
                    dt, "SPECTRUM", arr[k][5], arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            # sclient = 'stestp09/testss/s1r228'
            if k == "SpectrumString":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][2]).replace("'", "\""))
                ljson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][5]).replace("'", "\""))
            elif k == "SpectrumBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + ''.join([a + ',' for a in arr[k][5]])[:-1] + "]")
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + ''.join([str(a).lower() + ','
                                   for a in arr[k][2]])[:-1] + "]")
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + ''.join([str(a) + ','
                                   for a in arr[k][5]])[:-1] + "]")
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + ''.join([str(a) + ','
                                   for a in arr[k][2]])[:-1] + "]")

            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()
            if arr[k][1] == "DevBoolean":
                self.checkData(
                    dt, "SPECTRUM", [Converters.toBool(a) for a in arr[k][5]],
                    arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(
                    dt, "SPECTRUM", arr[k][5], arr[k][4], [arr[k][3][0]],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_spectrum_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0]],
            "SpectrumUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "SpectrumShort": ["int16", "DevShort", -123, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1234, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -124, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 234, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 234, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 23, [1, 0]],
            "SpectrumFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble",
                               -2.456673e+02, [1, 0], 1e-14],
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
        }

        arrb = {
            "SpectrumBoolean": ["bool", "DevBoolean", False, [1, 0]],
            "SpectrumUChar": ["uint8", "DevUChar", 12, [1, 0]],
            "SpectrumShort": ["int16", "DevShort", -113, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1114, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -114, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 211, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 211, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 13, [1, 0]],
            "SpectrumFloat": ["float32", "DevFloat", 11.114, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble",
                               -1.416673e+02, [1, 0], 1e-14],
            "SpectrumString": ["string", "DevString", "My123e", [1, 0]],
        }

        for k in arr:
            if arr[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arr[k][2] = [arr[k][2] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0], 0]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arrb:
            if arrb[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arrb[k][2] = [arrb[k][2] * self.__rnd.randint(0, 3)
                              for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arrb[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                              for c in range(mlen[0])]

            arrb[k][3] = [mlen[0], 0]
            self._simps2.dp.write_attribute(k, arrb[k][2])

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'attribute'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'attribute'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)

        dt = el[k].getData()
        dt = el2[k].getData()

        for k in arrb:
            self._simps.dp.write_attribute(k, arrb[k][2])
        for k in arr:
            self._simps2.dp.write_attribute(k, arr[k][2])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SPECTRUM", arrb[k][2], arrb[k][1], arrb[k][3],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "SPECTRUM", arrb[k][2], arrb[k][1], arrb[k][3],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_spectrum_group_noorder(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "SpectrumBoolean": ["bool", "DevBoolean", True, [1, 0]],
            "SpectrumUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "SpectrumShort": ["int16", "DevShort", -123, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1234, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -124, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 234, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 234, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 23, [1, 0]],
            "SpectrumFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble",
                               -2.456673e+02, [1, 0], 1e-14],
            "SpectrumString": ["string", "DevString", "MyTrue", [1, 0]],
        }

        arrb = {
            "SpectrumBoolean": ["bool", "DevBoolean", False, [1, 0]],
            "SpectrumUChar": ["uint8", "DevUChar", 12, [1, 0]],
            "SpectrumShort": ["int16", "DevShort", -113, [1, 0]],
            "SpectrumUShort": ["uint16", "DevUShort", 1114, [1, 0]],
            "SpectrumLong": ["int64", "DevLong", -114, [1, 0]],
            "SpectrumULong": ["uint64", "DevULong", 211, [1, 0]],
            "SpectrumLong64": ["int64", "DevLong64", 211, [1, 0]],
            "SpectrumULong64": ["uint64", "DevULong64", 13, [1, 0]],
            "SpectrumFloat": ["float32", "DevFloat", 11.114, [1, 0], 1e-5],
            "SpectrumDouble": ["float64", "DevDouble",
                               -1.416673e+02, [1, 0], 1e-14],
            "SpectrumString": ["string", "DevString", "My123e", [1, 0]],
        }

        for k in arr:
            if arr[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arr[k][2] = [arr[k][2] * self.__rnd.randint(0, 3)
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                             for c in range(mlen[0])]

            arr[k][3] = [mlen[0], 0]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arrb:
            if arrb[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                arrb[k][2] = [arrb[k][2] * self.__rnd.randint(0, 3)
                              for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                arrb[k][2] = [(True if self.__rnd.randint(0, 1) else False)
                              for c in range(mlen[0])]

            arrb[k][3] = [mlen[0], 0]
            self._simps2.dp.write_attribute(k, arrb[k][2])

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'attribute'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)
            dt = el[k].getData()

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'attribute'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)
            dt = el2[k].getData()

        dt = el[k].getData()
        dt = el2[k].getData()

        for k in arrb:
            self._simps.dp.write_attribute(k, arrb[k][2])
        for k in arr:
            self._simps2.dp.write_attribute(k, arr[k][2])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SPECTRUM", arrb[k][2], arrb[k][1], arrb[k][3],
                           None, None, arrb[k][4]
                           if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "SPECTRUM", arrb[k][2], arrb[k][1], arrb[k][3],
                           None, None, arrb[k][4]
                           if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "SPECTRUM", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "ImageBoolean": ["bool", "DevBoolean", True, [1, 0]],
            "ImageUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "ImageShort": ["int16", "DevShort", -123, [1, 0]],
            "ImageUShort": ["uint16", "DevUShort", 1234, [1, 0]],
            "ImageLong": ["int64", "DevLong", -124, [1, 0]],
            "ImageULong": ["uint64", "DevULong", 234, [1, 0]],
            "ImageLong64": ["int64", "DevLong64", 234, [1, 0]],
            "ImageULong64": ["uint64", "DevULong64", 23, [1, 0]],
            "ImageFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "ImageDouble": ["float64", "DevDouble", -2.456673e+02,
                            [1, 0], 1e-14],
            "ImageString": ["string", "DevString", "MyTrue", [1, 0]],
        }

        for k in arr:

            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[arr[k][2] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])]
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [[(True if self.__rnd.randint(0, 1) else False)
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            dt = el.getData()
            self.checkData(dt, "IMAGE", arr[k][2], arr[k][1], arr[
                           k][3], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_client_image(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "ImageBoolean": ["bool", "DevBoolean", True, [1, 0],
                             "DevBoolean", False],
            "ImageUChar": ["uint8", "DevUChar", 23, [1, 0],
                           "DevLong64", 2],
            "ImageShort": ["int16", "DevShort", -123, [1, 0],
                           "DevLong64", -13],
            "ImageUShort": ["uint16", "DevUShort", 1234, [1, 0],
                            "DevLong64", 134],
            "ImageLong": ["int64", "DevLong", -124, [1, 0],
                          "DevLong64", -1213],
            "ImageULong": ["uint64", "DevULong", 234, [1, 0],
                           "DevLong64", 23],
            "ImageLong64": ["int64", "DevLong64", 234, [1, 0],
                            "DevLong64", 24],
            "ImageULong64": ["uint64", "DevULong64", 23, [1, 0],
                             "DevLong64", 2],
            "ImageFloat": ["float32", "DevFloat", 12.23, [1, 0],
                           "DevDouble", 1.234, 1e-5],
            "ImageDouble": ["float64", "DevDouble", -2.456673e+02, [1, 0],
                            "DevDouble", -2.4563e+02, 1e-14],
            "ImageString": ["string", "DevString", "MyTrue", [1, 0],
                            "DevString", "MyTsfdrue"],
        }

        for k in arr:

            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[arr[k][2] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])] for c in range(mlen[0])]
                arr[k][5] = [[arr[k][5] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [[(True if self.__rnd.randint(0, 1) else False)
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]
                    arr[k][5] = [[("true" if self.__rnd.randint(0, 1)
                                   else "false")
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            dt = el.getData()
            self.checkData(dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "ImageString":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][5]).replace("'", "\""))
            elif k == "ImageBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([a + ','
                                                  for a in row])[:-1] + "],"
                                  for row in arr[k][5]])[:-1] + ']')
            else:
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([str(a) + ','
                                                  for a in row])[:-1] + "],"
                                  for row in arr[k][5]])[:-1] + ']')

            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()

            if arr[k][1] == "DevBoolean":
                self.checkData(dt, "IMAGE",
                               [[Converters.toBool(a) for a in row]
                                for row in arr[k][5]],
                               arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(dt, "IMAGE", arr[k][5], arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "ImageString":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][5]).replace("'", "\""))
            elif k == "ImageBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([a + ','
                                                  for a in row])[:-1] + "],"
                                  for row in arr[k][5]])[:-1] + ']')
            else:
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([str(a) + ','
                                                  for a in row])[:-1] + "],"
                                  for row in arr[k][5]])[:-1] + ']')

            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()

            if arr[k][1] == "DevBoolean":
                self.checkData(dt, "IMAGE",
                               [[Converters.toBool(a) for a in row]
                                for row in arr[k][5]],
                               arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(dt, "IMAGE", arr[k][5], arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "ImageString":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][5]).replace("'", "\""))
            elif k == "ImageBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([a + ','
                                                  for a in row])[:-1] + "],"
                                  for row in arr[k][5]])[:-1] + ']')
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([str(a) + ','
                                                  for a in row])[:-1] + "],"
                                  for row in arr[k][5]])[:-1] + ']')

            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()

            if arr[k][1] == "DevBoolean":
                self.checkData(dt, "IMAGE",
                               [[Converters.toBool(a) for a in row]
                                for row in arr[k][5]],
                               arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(dt, "IMAGE", arr[k][5], arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            sclient = 'stestp09/testss/s1r228'
            if k == "ImageString":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][5]).replace("'", "\""))
                gjson = '{"data":{"%s":%s}}' % (
                    sclient, str(arr[k][2]).replace("'", "\""))
            elif k == "ImageBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join(
                        [a + ',' for a in row])[:-1] + "],"
                        for row in arr[k][5]])[:-1] + ']')
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([str(a).lower() + ','
                                                  for a in row])[:-1] + "],"
                                   for row in arr[k][2]])[:-1] + ']')
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([str(a) + ','
                                                  for a in row])[:-1] + "],"
                                   for row in arr[k][5]])[:-1] + ']')
                gjson = '{"data":{"%s":%s}}' % (
                    sclient,
                    '[' + "".join(['[' + ''.join([str(a) + ','
                                                  for a in row])[:-1] + "],"
                                   for row in arr[k][2]])[:-1] + ']')

            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()

            if arr[k][1] == "DevBoolean":
                self.checkData(dt, "IMAGE",
                               [[Converters.toBool(a) for a in row]
                                for row in arr[k][5]],
                               arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(dt, "IMAGE", arr[k][5], arr[k][4], arr[k][3],
                               None, None, arr[k][6]
                               if len(arr[k]) > 6 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_client_image_sar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "ImageBoolean": ["bool", "DevBoolean", True, [1, 0],
                             "DevBoolean", False],
            "ImageUChar": ["uint8", "DevUChar", 23, [1, 0], "DevLong64", 2],
            "ImageShort": ["int16", "DevShort", -123, [1, 0], "DevLong64",
                           -13],
            "ImageUShort": ["uint16", "DevUShort", 1234, [1, 0], "DevLong64",
                            134],
            "ImageLong": ["int64", "DevLong", -124, [1, 0], "DevLong64",
                          -1213],
            "ImageULong": ["uint64", "DevULong", 234, [1, 0], "DevLong64", 23],
            "ImageLong64": ["int64", "DevLong64", 234, [1, 0], "DevLong64",
                            24],
            "ImageULong64": ["uint64", "DevULong64", 23, [1, 0], "DevLong64",
                             2],
            "ImageFloat": ["float32", "DevFloat", 12.23, [1, 0], "DevDouble",
                           1.234, 1e-5],
            "ImageDouble": ["float64", "DevDouble", -2.456673e+02, [1, 0],
                            "DevDouble", -2.4563e+02, 1e-14],
            "ImageString": ["string", "DevString", "MyTrue", [1, 0],
                            "DevString", "MyTsfdrue"],
        }

        for k in arr:

            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[arr[k][2] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])] for c in range(mlen[0])]
                arr[k][5] = [[arr[k][5] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [[(True if self.__rnd.randint(0, 1) else False)
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]
                    arr[k][5] = [[("true" if self.__rnd.randint(0, 1)
                                   else "false")
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            dt = el.getData()
            self.checkData(dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            # sclient = 'stestp09/testss/s1r228'
            if k == "ImageString":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][5]).replace("'", "\""))
            elif k == "ImageBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(
                        ['[' + ''.join([a + ',' for a in row])[:-1] + "],"
                         for row in arr[k][5]])[:-1] + ']')
            else:
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(
                        ['[' + ''.join([str(a) + ',' for a in row])[:-1] + "],"
                         for row in arr[k][5]])[:-1] + ']')

            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()

            if arr[k][1] == "DevBoolean":
                self.checkData(
                    dt, "IMAGE",
                    [[Converters.toBool(a) for a in row]
                     for row in arr[k][5]],
                    arr[k][4], arr[k][3],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(
                    dt, "IMAGE", arr[k][5], arr[k][4], arr[k][3],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            # sclient = 'stestp09/testss/s1r228'
            if k == "ImageString":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][5]).replace("'", "\""))
            elif k == "ImageBoolean":
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(['[' + ''.join(
                        [a + ',' for a in row])[:-1] + "],"
                        for row in arr[k][5]])[:-1] + ']')
            else:
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(['[' + ''.join(
                        [str(a) + ',' for a in row])[:-1] + "],"
                        for row in arr[k][5]])[:-1] + ']')

            self.assertEqual(el.setJSON(json.loads(gjson)), None)
            dt = el.getData()

            if arr[k][1] == "DevBoolean":
                self.checkData(
                    dt, "IMAGE",
                    [[Converters.toBool(a) for a in row]
                     for row in arr[k][5]],
                    arr[k][4], arr[k][3],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(
                    dt, "IMAGE", arr[k][5], arr[k][4], arr[k][3],
                    None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            # sclient = 'stestp09/testss/s1r228'
            if k == "ImageString":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][5]).replace("'", "\""))
            elif k == "ImageBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(['[' + ''.join(
                        [a + ',' for a in row])[:-1] + "],"
                        for row in arr[k][5]])[:-1] + ']')
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(['[' + ''.join(
                        [str(a) + ',' for a in row])[:-1] + "],"
                        for row in arr[k][5]])[:-1] + ']')

            gjson = '{}'
            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()

            if arr[k][1] == "DevBoolean":
                self.checkData(dt, "IMAGE",
                               [[Converters.toBool(a) for a in row]
                                for row in arr[k][5]],
                               arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(dt, "IMAGE", arr[k][5], arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'attribute'
            el.member.name = k
            el.client = 'stestp09/testss/s1r228/%s' % (k.lower())
            # sclient = 'stestp09/testss/s1r228'
            if k == "ImageString":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][5]).replace("'", "\""))
                gjson = '{"data":{"%s":%s}}' % (
                    el.client, str(arr[k][2]).replace("'", "\""))
            elif k == "ImageBoolean":
                ljson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(['[' + ''.join(
                        [a + ',' for a in row])[:-1] + "],"
                        for row in arr[k][5]])[:-1] + ']')
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(['[' + ''.join(
                        [str(a).lower() + ',' for a in row])[:-1] + "],"
                        for row in arr[k][2]])[:-1] + ']')
            else:
                ljson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(['[' + ''.join(
                        [str(a) + ',' for a in row])[:-1] + "],"
                        for row in arr[k][5]])[:-1] + ']')
                gjson = '{"data":{"%s":%s}}' % (
                    el.client,
                    '[' + "".join(['[' + ''.join(
                        [str(a) + ',' for a in row])[:-1] + "],"
                        for row in arr[k][2]])[:-1] + ']')

            self.assertEqual(
                el.setJSON(json.loads(gjson), json.loads(ljson)), None)
            dt = el.getData()

            if arr[k][1] == "DevBoolean":
                self.checkData(dt, "IMAGE",
                               [[Converters.toBool(a) for a in row]
                                for row in arr[k][5]],
                               arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

            else:
                self.checkData(dt, "IMAGE", arr[k][5], arr[k][4], arr[k][3],
                               None, None, arr[k][6] if len(arr[k]) > 6 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_image_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "ImageBoolean": ["bool", "DevBoolean", True, [1, 0]],
            "ImageUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "ImageShort": ["int16", "DevShort", -123, [1, 0]],
            "ImageUShort": ["uint16", "DevUShort", 1234, [1, 0]],
            "ImageLong": ["int64", "DevLong", -124, [1, 0]],
            "ImageULong": ["uint64", "DevULong", 234, [1, 0]],
            "ImageLong64": ["int64", "DevLong64", 234, [1, 0]],
            "ImageULong64": ["uint64", "DevULong64", 23, [1, 0]],
            "ImageFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "ImageDouble": ["float64", "DevDouble", -2.456673e+02,
                            [1, 0], 1e-14],
            "ImageString": ["string", "DevString", "MyTrue", [1, 0]],
        }

        arrb = {
            "ImageBoolean": ["bool", "DevBoolean", False, [1, 0]],
            "ImageUChar": ["uint8", "DevUChar", 13, [1, 0]],
            "ImageShort": ["int16", "DevShort", -113, [1, 0]],
            "ImageUShort": ["uint16", "DevUShort", 1114, [1, 0]],
            "ImageLong": ["int64", "DevLong", -121, [1, 0]],
            "ImageULong": ["uint64", "DevULong", 214, [1, 0]],
            "ImageLong64": ["int64", "DevLong64", 214, [1, 0]],
            "ImageULong64": ["uint64", "DevULong64", 13, [1, 0]],
            "ImageFloat": ["float32", "DevFloat", 11.214, [1, 0], 1e-5],
            "ImageDouble": ["float64", "DevDouble", -1.416673e+02,
                            [1, 0], 1e-14],
            "ImageString": ["string", "DevString", "M11rue", [1, 0]],
        }

        for k in arr:

            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[arr[k][2] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])]
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [[(True if self.__rnd.randint(0, 1) else False)
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arrb:

            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arrb[k][1] != "DevBoolean":
                arrb[k][2] = [[arrb[k][2] * self.__rnd.randint(0, 3)
                               for r in range(mlen[1])]
                              for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arrb[k][1] == 'DevBoolean':
                    arrb[k][2] = [[(True if self.__rnd.randint(0, 1)
                                    else False)
                                   for c in range(mlen[1])]
                                  for r in range(mlen[0])]

            arrb[k][3] = [mlen[0], mlen[1]]
            self._simps2.dp.write_attribute(k, arrb[k][2])

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'attribute'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'attribute'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)

        dt = el[k].getData()
        dt = el2[k].getData()

        for k in arrb:
            self._simps.dp.write_attribute(k, arrb[k][2])
        for k in arr:
            self._simps2.dp.write_attribute(k, arr[k][2])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "IMAGE", arrb[k][2], arrb[k][1], arrb[k][3],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "IMAGE", arrb[k][2], arrb[k][1], arrb[k][3],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_image_group_noorder(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "ImageBoolean": ["bool", "DevBoolean", True, [1, 0]],
            "ImageUChar": ["uint8", "DevUChar", 23, [1, 0]],
            "ImageShort": ["int16", "DevShort", -123, [1, 0]],
            "ImageUShort": ["uint16", "DevUShort", 1234, [1, 0]],
            "ImageLong": ["int64", "DevLong", -124, [1, 0]],
            "ImageULong": ["uint64", "DevULong", 234, [1, 0]],
            "ImageLong64": ["int64", "DevLong64", 234, [1, 0]],
            "ImageULong64": ["uint64", "DevULong64", 23, [1, 0]],
            "ImageFloat": ["float32", "DevFloat", 12.234, [1, 0], 1e-5],
            "ImageDouble": ["float64", "DevDouble", -2.456673e+02, [1, 0],
                            1e-14],
            "ImageString": ["string", "DevString", "MyTrue", [1, 0]],
        }

        arrb = {
            "ImageBoolean": ["bool", "DevBoolean", False, [1, 0]],
            "ImageUChar": ["uint8", "DevUChar", 13, [1, 0]],
            "ImageShort": ["int16", "DevShort", -113, [1, 0]],
            "ImageUShort": ["uint16", "DevUShort", 1114, [1, 0]],
            "ImageLong": ["int64", "DevLong", -121, [1, 0]],
            "ImageULong": ["uint64", "DevULong", 214, [1, 0]],
            "ImageLong64": ["int64", "DevLong64", 214, [1, 0]],
            "ImageULong64": ["uint64", "DevULong64", 13, [1, 0]],
            "ImageFloat": ["float32", "DevFloat", 11.214, [1, 0], 1e-5],
            "ImageDouble": ["float64", "DevDouble", -1.416673e+02, [1, 0],
                            1e-14],
            "ImageString": ["string", "DevString", "M11rue", [1, 0]],
        }

        for k in arr:

            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] = [[arr[k][2] * self.__rnd.randint(0, 3)
                              for r in range(mlen[1])]
                             for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] = [[(True if self.__rnd.randint(0, 1) else False)
                                  for c in range(mlen[1])]
                                 for r in range(mlen[0])]

            arr[k][3] = [mlen[0], mlen[1]]
            self._simps.dp.write_attribute(k, arr[k][2])

        for k in arrb:

            mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                1, 10), self.__rnd.randint(0, 3)]
            if arrb[k][1] != "DevBoolean":
                arrb[k][2] = [[arrb[k][2] * self.__rnd.randint(0, 3)
                               for r in range(mlen[1])]
                              for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if arrb[k][1] == 'DevBoolean':
                    arrb[k][2] = [[(True if self.__rnd.randint(0, 1)
                                    else False)
                                   for c in range(mlen[1])]
                                  for r in range(mlen[0])]

            arrb[k][3] = [mlen[0], mlen[1]]
            self._simps2.dp.write_attribute(k, arrb[k][2])

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'attribute'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)
            dt = el[k].getData()

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'attribute'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)
            dt = el2[k].getData()

        dt = el[k].getData()
        dt = el2[k].getData()

        for k in arrb:
            self._simps.dp.write_attribute(k, arrb[k][2])
        for k in arr:
            self._simps2.dp.write_attribute(k, arr[k][2])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "IMAGE", arrb[k][2], arrb[k][1], arrb[k][3],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "IMAGE", arrb[k][2], arrb[k][1], arrb[k][3],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "IMAGE", arr[k][2], arr[k][1], arr[k][3],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_command(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "GetShort": ["ScalarShort", "int16", "DevShort", -123],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "GetLong": ["ScalarLong", "int64", "DevLong", -124],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 234],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 234],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 23],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 12.234, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -2.456673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        for k in arr:
            print(k)
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])
        print("ww")
        for k in arr:
            print(k)
            print("K1")
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'command'
            el.member.name = k
            print("K2")
            dt = el.getData()
            print("K3")
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [
                           1, 0], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)
            print("K4")

    # getData test
    # \brief It tests default settings
    def test_getData_command_lt(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "GetShort": ["ScalarShort", "int16", "DevShort", -123],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "GetLong": ["ScalarLong", "int64", "DevLong", -124],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 234],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 234],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 23],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 12.234, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -2.456673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        for k in arr:
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'command'
            el.member.name = k.lower()
            dt = el.getData()
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [
                           1, 0], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_command_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "GetShort": ["ScalarShort", "int16", "DevShort", -123],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "GetLong": ["ScalarLong", "int64", "DevLong", -124],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 234],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 234],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 23],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 12.234, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -2.456673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        arrb = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 3],
            "GetShort": ["ScalarShort", "int16", "DevShort", -113],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1114],
            "GetLong": ["ScalarLong", "int64", "DevLong", -121],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 211],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 211],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 13],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 11.134, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -1.116673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyT11e"],
        }

        for k in arr:
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arrb[k][0], arrb[k][3])

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'command'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'command'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)

        dt = el[k].getData()
        dt = el2[k].getData()

        for k in arr:
            self._simps.dp.write_attribute(arrb[k][0], arrb[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [1, 0],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [1, 0],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_command_group_lt(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "GetShort": ["ScalarShort", "int16", "DevShort", -123],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "GetLong": ["ScalarLong", "int64", "DevLong", -124],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 234],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 234],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 23],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 12.234, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -2.456673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        arrb = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 3],
            "GetShort": ["ScalarShort", "int16", "DevShort", -113],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1114],
            "GetLong": ["ScalarLong", "int64", "DevLong", -121],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 211],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 211],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 13],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 11.134, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -1.116673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyT11e"],
        }

        for k in arr:
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arrb[k][0], arrb[k][3])

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'command'
            el[k].member.name = k.lower()
            self.assertEqual(el[k].setDataSources(pl), None)

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'command'
            el2[k].member.name = k.lower()
            self.assertEqual(el2[k].setDataSources(pl), None)

        dt = el[k].getData()
        dt = el2[k].getData()

        for k in arr:
            self._simps.dp.write_attribute(arrb[k][0], arrb[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [1, 0],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [1, 0],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_command_group_noorder(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "GetShort": ["ScalarShort", "int16", "DevShort", -123],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "GetLong": ["ScalarLong", "int64", "DevLong", -124],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 234],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 234],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 23],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 12.234, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -2.456673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        arrb = {
            "GetBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 3],
            "GetShort": ["ScalarShort", "int16", "DevShort", -113],
            "GetUShort": ["ScalarUShort", "uint16", "DevUShort", 1114],
            "GetLong": ["ScalarLong", "int64", "DevLong", -121],
            "GetULong": ["ScalarULong", "uint64", "DevULong", 211],
            "GetLong64": ["ScalarLong64", "int64", "DevLong64", 211],
            "GetULong64": ["ScalarULong64", "uint64", "DevULong64", 13],
            "GetFloat": ["ScalarFloat", "float32", "DevFloat", 11.134, 1e-5],
            "GetDouble": ["ScalarDouble", "float64", "DevDouble",
                          -1.116673e+02, 1e-14],
            "GetString": ["ScalarString", "string", "DevString", "MyT11e"],
        }

        for k in arr:
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arrb[k][0], arrb[k][3])

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'command'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)
            dt = el[k].getData()

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'command'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)
            dt = el2[k].getData()

        dt = el[k].getData()
        dt = el2[k].getData()

        for k in arr:
            self._simps.dp.write_attribute(arrb[k][0], arrb[k][3])

        for k in arrb:
            self._simps2.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [1, 0],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", arrb[k][3], arrb[k][2], [1, 0],
                           None, None, arrb[k][4] if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", arr[k][3], arr[k][2], [1, 0],
                           None, None, arr[k][4] if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_dev_prop_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #         "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -113],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1134],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -111],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 1134],
            #            "DeviceLong64":["ScalarLong64", "int64",
            #       "DevLong64", 234],
            #            "DeviceULong64":["ScalarULong64", "uint64",
            #                   "DevULong64", 23],
            #            "DeviceFloat":["ScalarFloat", "float32", "DevFloat",
            #             12.234, 1e-07],
            #            "DeviceDouble":["ScalarDouble", "float64",
            # "DevDouble", -1.456673e+02, 1e-14],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 12.234],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -1.45e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        arrb = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", False],
            #       "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 11],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -11],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 114],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -121],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 214],
            #    "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 214],
            #  "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 21],
            #  "DeviceFloat":["ScalarFloat", "float32", "DevFloat", 11.134,
            # 1e-07],
            #   "DeviceDouble":["ScalarDouble", "float64", "DevDouble",
            # -1.416673e+02, 1e-14],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 11.134],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -1.41e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "M11rue"],
        }

        prop = self._simps.dp.get_property(list(arr.keys()))
        for k in prop.keys():
            prop[k] = [arr[k][3]]
        self._simps.dp.put_property(prop)

        prop = self._simps2.dp.get_property(list(arrb.keys()))
        for k in prop.keys():
            prop[k] = [arrb[k][3]]
        self._simps2.dp.put_property(prop)

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'property'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'property'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)

        dt = el[k].getData()
        dt = el2[k].getData()

        prop = self._simps.dp.get_property(list(arrb.keys()))
        for k in prop.keys():
            prop[k] = [arrb[k][3]]
        self._simps.dp.put_property(prop)

        prop = self._simps2.dp.get_property(list(arr.keys()))
        for k in prop.keys():
            prop[k] = [arr[k][3]]
        self._simps2.dp.put_property(prop)

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", str(arr[k][3]),
                           'DevString', [1, 0], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", str(arrb[k][3]),
                           'DevString', [1, 0], None, None, arrb[k][4]
                           if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", str(arrb[k][3]),
                           'DevString', [1, 0], None, None, arrb[k][4]
                           if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", str(arr[k][3]),
                           'DevString', [1, 0], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_dev_prop_group_lt(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #         "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -113],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1134],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -111],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 1134],
            # "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 234],
            #  "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 23],
            # "DeviceFloat":["ScalarFloat", "float32", "DevFloat", 12.234,
            # 1e-07],
            #  "DeviceDouble":["ScalarDouble", "float64", "DevDouble",
            # -1.456673e+02, 1e-14],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 12.234],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -1.45e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        arrb = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", False],
            #         "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 11],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -11],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 114],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -121],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 214],
            #  "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 214],
            #  "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 21],
            #  "DeviceFloat":["ScalarFloat", "float32", "DevFloat", 11.134,
            #  1e-07],
            #  "DeviceDouble":["ScalarDouble", "float64", "DevDouble",
            # -1.416673e+02, 1e-14],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 11.134],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -1.41e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "M11rue"],
        }

        prop = self._simps.dp.get_property(list(arr.keys()))
        for k in prop.keys():
            prop[k] = [arr[k][3]]
        self._simps.dp.put_property(prop)

        prop = self._simps2.dp.get_property(list(arrb.keys()))
        for k in prop.keys():
            prop[k] = [arrb[k][3]]
        self._simps2.dp.put_property(prop)

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'property'
            el[k].member.name = k.lower()
            self.assertEqual(el[k].setDataSources(pl), None)

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'property'
            el2[k].member.name = k.lower()
            self.assertEqual(el2[k].setDataSources(pl), None)

        dt = el[k].getData()
        dt = el2[k].getData()

        prop = self._simps.dp.get_property(list(arrb.keys()))
        for k in prop.keys():
            prop[k] = [arrb[k][3]]
        self._simps.dp.put_property(prop)

        prop = self._simps2.dp.get_property(list(arr.keys()))
        for k in prop.keys():
            prop[k] = [arr[k][3]]
        self._simps2.dp.put_property(prop)

        for k in arr:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", str(arr[k][3]),
                           'DevString', [1, 0], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", str(arrb[k][3]),
                           'DevString', [1, 0], None, None, arrb[k][4]
                           if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", str(arrb[k][3]),
                           'DevString', [1, 0], None, None, arrb[k][4]
                           if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", str(arr[k][3]),
                           'DevString', [1, 0], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_dev_prop_group_noorder(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #     "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -113],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1134],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -111],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 1134],
            #     "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 234],
            #   "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 23],
            #   "DeviceFloat":["ScalarFloat", "float32", "DevFloat", 12.234,
            # 1e-07],
            #  "DeviceDouble":["ScalarDouble", "float64", "DevDouble",
            # -1.456673e+02, 1e-14],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 12.234],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -1.45e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        arrb = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", False],
            #    "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 11],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -11],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 114],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -121],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 214],
            #    "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 214],
            #   "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 21],
            #   "DeviceFloat":["ScalarFloat", "float32", "DevFloat", 11.134,
            # 1e-07],
            #   "DeviceDouble":["ScalarDouble", "float64", "DevDouble",
            # -1.416673e+02, 1e-14],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 11.134],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -1.41e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "M11rue"],
        }

        prop = self._simps.dp.get_property(list(arr.keys()))
        for k in prop.keys():
            prop[k] = [arr[k][3]]
        self._simps.dp.put_property(prop)

        prop = self._simps2.dp.get_property(list(arrb.keys()))
        for k in prop.keys():
            prop[k] = [arrb[k][3]]
        self._simps2.dp.put_property(prop)

        pl = pool()
        pl.counter = 1
        el = {}
        el2 = {}
        group = "CORE"
        group2 = "CORE2"
        for k in arr:
            el[k] = TangoSource()
            el[k].group = group
            el[k].device = 'stestp09/testss/s1r228'
            el[k].member.memberType = 'property'
            el[k].member.name = k
            self.assertEqual(el[k].setDataSources(pl), None)
            dt = el[k].getData()

        for k in arrb:
            el2[k] = TangoSource()
            el2[k].group = group2
            el2[k].device = 'stestp09/testss/s2r228'
            el2[k].member.memberType = 'property'
            el2[k].member.name = k
            self.assertEqual(el2[k].setDataSources(pl), None)
            dt = el2[k].getData()

        dt = el[k].getData()
        dt = el2[k].getData()

        prop = self._simps.dp.get_property(list(arrb.keys()))
        for k in prop.keys():
            prop[k] = [arrb[k][3]]
        self._simps.dp.put_property(prop)

        prop = self._simps2.dp.get_property(list(arr.keys()))
        for k in prop.keys():
            prop[k] = [arr[k][3]]
        self._simps2.dp.put_property(prop)

        for k in arr:
            dt = el[k].getData()
            self.checkData(
                dt, "SCALAR", str(arr[k][3]),
                'DevString', [1, 0], None, None, arr[k][4]
                if len(arr[k]) > 4 else 0)

        for k in arrb:
            dt = el2[k].getData()
            self.checkData(dt, "SCALAR", str(arrb[k][3]),
                           'DevString', [1, 0], None, None, arrb[k][4]
                           if len(arrb[k]) > 4 else 0)

        pl.counter = 2

        for k in arrb:
            dt = el[k].getData()
            self.checkData(dt, "SCALAR", str(arrb[k][3]),
                           'DevString', [1, 0], None, None, arrb[k][4]
                           if len(arrb[k]) > 4 else 0)

        for k in arr:
            dt = el2[k].getData()
            self.checkData(
                dt, "SCALAR", str(arr[k][3]),
                'DevString', [1, 0], None, None, arr[k][4] if len(arr[k]) > 4
                else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_dev_prop(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #           "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -123],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -124],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 234],
            #    "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 234],
            #    "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 23],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 12.234],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -2.456673e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'property'
            el.member.name = k
            dt = el.getData()
            dp = tango.DeviceProxy(el.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            self.checkData(
                dt, "SCALAR", dp.get_property([k])[k][0],
                'DevString', [1, 0], None, None, arr[k][4]
                if len(arr[k]) > 4 else 0)

    # getData test
    # \brief It tests default settings
    def test_getData_dev_prop_lt(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        arr = {
            "DeviceBoolean": ["ScalarBoolean", "bool", "DevBoolean", True],
            #           "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort": ["ScalarShort", "int16", "DevShort", -123],
            "DeviceUShort": ["ScalarUShort", "uint16", "DevUShort", 1234],
            "DeviceLong": ["ScalarLong", "int64", "DevLong", -124],
            "DeviceULong": ["ScalarULong", "uint64", "DevULong", 234],
            #    "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 234],
            #    "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 23],
            "DeviceFloat": ["ScalarFloat", "float32", "DevFloat", 12.234],
            "DeviceDouble": ["ScalarDouble", "float64", "DevDouble",
                             -2.456673e+02],
            "DeviceString": ["ScalarString", "string", "DevString", "MyTrue"],
        }

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.member.memberType = 'property'
            el.member.name = k.lower()
            dt = el.getData()
            dp = tango.DeviceProxy(el.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            self.checkData(dt, "SCALAR", dp.get_property([k])[k][0],
                           'DevString', [1, 0], None, None, arr[k][4]
                           if len(arr[k]) > 4 else 0)

    # isValid test
    # \brief It tests default settings
    def test_isValid(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = TangoSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.isValid(), True)

    # constructor test
    # \brief It tests default settings
    def test_setDecoders_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dname = 'writer'
        device = 'stestp09/testss/s1r228'
        # ctype = 'command'
        atype = 'attribute'
        # host = 'haso.desy.de'
        # port = '10000'
        encoding = 'UTF8'

        atts = {"type": "TANGO"}
        # name = "myRecord"
        # wjson = json.loads(
        #     '{"datasources":{"CL":"ClientSource.ClientSource"}}')
        gjson = json.loads('{"data":{"myRecord":"1"}}')

        el = EField(self._fattrs, None)
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()), None)
        self.assertEqual(ds.store(
            ["<datasource type='TANGO'>",
             "<record name='%s'/> <device name='%s' encoding='%s'/>" % (
                 dname, device, encoding),
             "</datasource>"], gjson), None)
        self.assertEqual(type(ds.last.source), TangoSource)
        self.assertEqual(ds.last.source.member.name, dname)
        self.assertEqual(ds.last.source.device, device)
        self.assertEqual(ds.last.source.member.encoding, encoding)
        self.assertEqual(
            ds.last.source.__str__(),
            " TANGO Device %s : %s (%s)" % (device, dname, atype))
        self.assertEqual(len(ds.last.tagAttributes), 1)
        self.assertEqual(
            ds.last.tagAttributes["nexdatas_source"],
            (
                'NX_CHAR',
                "<datasource type='TANGO'><record name='writer'/> "
                "<device name='stestp09/testss/s1r228' encoding='UTF8'/>"
                "</datasource>"
            )
        )


if __name__ == '__main__':
    unittest.main()
