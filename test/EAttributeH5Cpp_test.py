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
# \file EAttributeTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct
import random
import numpy
import binascii
import time


from nxswriter.FElement import FElement
from nxswriter.EAttribute import EAttribute
from nxswriter.EField import EField
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile
from nxswriter.Types import NTP, Converters

try:
    from TstDataSource import TstDataSource
except Exception:
    from .TstDataSource import TstDataSource

try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker

from nxstools import filewriter as FileWriter
from nxstools import h5cppwriter as H5CppWriter

# from  xml.sax import SAXParseException

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class EAttributeH5CppTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"name": "testField", "units": "m"}
        self._fattrs2 = {"name": "testField", "type": "NX_INT", "units": "m"}
        self._gattrs = {"name": "testGroup", "type": "NXentry"}
        self._gname = "testGroup"
        self._gtype = "NXentry"
        self._fdname = "testField"
        self._fdtype = "int64"

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self._sc = Checker(self)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)
        print("CHECKER SEED = %s" % self._sc.seed)
        FileWriter.writer = H5CppWriter

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

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

    # default constructor test
    # \brief It tests default settings
    def test_default_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        EFile({}, None, self._nxFile)
        at = EAttribute({}, None)
        self.assertTrue(isinstance(at, Element))
        self.assertTrue(isinstance(at, FElement))
        self.assertEqual(at.tagName, "attribute")
        self.assertEqual(at.content, [])
        self.assertEqual(at.name, "")
        self.assertEqual(at.rank, "0")
        self.assertEqual(at.lengths, {})
        self.assertEqual(at.strategy, 'INIT')
        self.assertEqual(at.trigger, None)

        self.assertEqual(at.h5Object, None)

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_default_constructor_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        EFile({}, None, self._nxFile)
        at = EAttribute({}, None)
        self.assertTrue(isinstance(at, Element))
        self.assertTrue(isinstance(at, FElement))
        self.assertEqual(at.tagName, "attribute")
        self.assertEqual(at.content, [])
        self.assertEqual(at.name, "")
        self.assertEqual(at.rank, "0")
        self.assertEqual(at.lengths, {})
        self.assertEqual(at.strategy, 'INIT')
        self.assertEqual(at.trigger, None)

        self.assertEqual(at.h5Object, None)

        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField({"name": "test"}, eFile)
        at = EAttribute({}, el)
        self.assertEqual(at.h5Object, None)
        self.assertEqual(at.store(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_simple(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField({"name": "test"}, eFile)
        at = EAttribute({"name": "mystring"}, el)
        self.assertEqual(at.h5Object, None)
        self.assertEqual(at.store(), None)
        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_ds(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField({"name": "test"}, eFile)
        at = EAttribute({"name": "mystring"}, el)
        ds = TstDataSource()
        at.source = ds
        self.assertEqual(at.h5Object, None)
        self.assertEqual(at.store(), ('INIT', None))
        self.assertEqual(at.store(), ('INIT', None))
        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_strategy(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField({"name": "test"}, eFile)
        at = EAttribute({"name": "mystring", "type": "NX_INT"}, el)
        ds = TstDataSource()
        at.source = ds
        at.strategy = "INIT"
        self.assertEqual(at.h5Object, None)
        self.assertEqual(at.store(), ('INIT', None))
        self.assertEqual(el.tagAttributes["mystring"], ('NX_INT', ''))

        at2 = EAttribute({"name": "mystring", "type": "NX_CHAR"}, el)
        at2.source = ds
        at2.strategy = "INIT"
        self.assertEqual(at2.h5Object, None)
        self.assertEqual(at2.store(), ('INIT', None))
        self.assertEqual(el.tagAttributes["mystring"], ('NX_CHAR', ''))
        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_trigger(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField({"name": "test"}, eFile)
        at = EAttribute({"name": "mystring"}, el)
        ds = TstDataSource()
        at.source = ds
        at.strategy = "INIT"
        at.trigger = "myTrigger"
        self.assertEqual(at.h5Object, None)
        self.assertEqual(at.store(), ('INIT', "myTrigger"))
        self.assertEqual(el.tagAttributes["mystring"], ('NX_CHAR', ''))
        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_Attributes_0d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-123, "NX_INT", "int64"],
            "int8": [12, "NX_INT8", "int8"],
            "int16": [-123, "NX_INT16", "int16"],
            "int32": [12345, "NX_INT32", "int32"],
            "int64": [-12345, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [12, "NX_UINT8", "uint8"],
            "uint16": [123, "NX_UINT16", "uint16"],
            "uint32": [12345, "NX_UINT32", "uint32"],
            "uint64": [12345, "NX_UINT64", "uint64"],
            "float": [-12.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool"],
            "bool3": ["false", "NX_BOOLEAN", "bool"],
            "bool4": ["true", "NX_BOOLEAN", "bool"]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField({"name": "test"}, eFile)

        el = {}
        for k in attrs.keys():

            el[k] = EAttribute({"name": k, "type": attrs[k][1]}, fi)
            ds = TstDataSource()
            el[k].source = ds
            el[k].strategy = "INIT"
            self.assertEqual(el[k].h5Object, None)
            self.assertEqual(el[k].store(), ('INIT', None))
            self.assertEqual(fi.tagAttributes[k], (attrs[k][1], ''))

        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_Attributes_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField({"name": "test"}, eFile)

        el = {}
        for k in attrs.keys():

            el[k] = EAttribute({"name": k, "type": attrs[k][1]}, fi)
            el[k].rank = "1"
            el[k].lengths = {"1": str(attrs[k][3][0])}
            el[k].strategy = "INIT"
            el[k].content = [str(attrs[k][0])]
            self.assertEqual(el[k].h5Object, None)
            self.assertEqual(el[k].store(), None)
            self.assertEqual(fi.tagAttributes[k], (
                attrs[k][1], str(attrs[k][0]), (1,)))

        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_Attributes_1d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField({"name": "test"}, eFile)

        el = {}
        quin = 0
        for k in attrs.keys():
            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for c in range(mlen[0])
                ]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] = [bool(self.__rnd.randint(0, 1))
                                   for c in range(mlen[0])]
                else:
                    attrs[k][0] = [
                        ("true" if self.__rnd.randint(0, 1) else "false")
                        for c in range(mlen[0])
                    ]

            attrs[k][3] = (mlen[0],)

            el[k] = EAttribute({"name": k, "type": attrs[k][1]}, fi)
            el[k].rank = "1"
            el[k].lengths = {"1": str(attrs[k][3][0])}
            el[k].strategy = stt
            el[k].content = [str(attrs[k][0])]
            self.assertEqual(el[k].h5Object, None)
            self.assertEqual(el[k].store(), None)
            self.assertEqual(fi.tagAttributes[k], (
                attrs[k][1], str(attrs[k][0]), attrs[k][3]))

        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_Attributes_2d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField({"name": "test"}, eFile)

        el = {}
        quin = 0
        for k in attrs.keys():
            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] == "string":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(1, 3)]]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(0, 3)]]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [[bool(self.__rnd.randint(0, 1))]]
                else:
                    attrs[k][0] = [
                        [
                            ("true" if self.__rnd.randint(0, 1) else "false")
                        ]
                    ]

            attrs[k][3] = (1, 1)

            el[k] = EAttribute({"name": k, "type": attrs[k][1]}, fi)
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].strategy = stt
            el[k].content = [str(attrs[k][0])]
            self.assertEqual(el[k].h5Object, None)
            self.assertEqual(el[k].store(), None)
            self.assertEqual(fi.tagAttributes[k], (
                attrs[k][1], str(attrs[k][0]), attrs[k][3]))

        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_Attributes_2d_double(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField({"name": "test"}, eFile)

        el = {}
        quin = 0
        for k in attrs.keys():
            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] == "string":
                attrs[k][0] = [
                    [attrs[k][0] * self.__rnd.randint(1, 3)
                     for c in range(self.__rnd.randint(2, 10))]]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [
                    [attrs[k][0] * self.__rnd.randint(0, 3)
                     for c in range(self.__rnd.randint(2, 10))]]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [
                        [
                            bool(self.__rnd.randint(0, 1))
                            for c in range(self.__rnd.randint(2, 10))
                        ]
                    ]
                else:
                    attrs[k][0] = [
                        [
                            ("true" if self.__rnd.randint(0, 1) else "false")
                            for c in range(self.__rnd.randint(2, 10))
                        ]
                    ]

            attrs[k][3] = (1, len(attrs[k][0][0]))

            el[k] = EAttribute({"name": k, "type": attrs[k][1]}, fi)
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].strategy = stt
            el[k].content = [str(attrs[k][0])]
            self.assertEqual(el[k].h5Object, None)
            self.assertEqual(el[k].store(), None)
            self.assertEqual(fi.tagAttributes[k], (
                attrs[k][1], str(attrs[k][0]), attrs[k][3]))

        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_Attributes_2d_double_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField({"name": "test"}, eFile)

        el = {}
        quin = 0
        for k in attrs.keys():
            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] == "string":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(1, 3)]
                               for c in range(self.__rnd.randint(2, 10))]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(0, 3)]
                               for c in range(self.__rnd.randint(2, 10))]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [
                        [
                            bool(self.__rnd.randint(0, 1))
                        ]
                        for c in range(self.__rnd.randint(2, 10))
                    ]
                else:
                    attrs[k][0] = [
                        [
                            ("true" if self.__rnd.randint(0, 1)
                             else "false")]
                        for c in range(self.__rnd.randint(2, 10))
                    ]

            attrs[k][3] = (len(attrs[k][0]), 1)

            el[k] = EAttribute({"name": k, "type": attrs[k][1]}, fi)
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].strategy = stt
            el[k].content = [str(attrs[k][0])]
            self.assertEqual(el[k].h5Object, None)
            self.assertEqual(el[k].store(), None)
            self.assertEqual(fi.tagAttributes[k], (
                attrs[k][1], str(attrs[k][0]), attrs[k][3]))

        self._nxFile.close()
        os.remove(self._fname)

    # store default
    # \brief It tests default settings
    def test_store_Attributes_2d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField({"name": "test"}, eFile)

        el = {}
        quin = 0
        for k in attrs.keys():
            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            mlen = self.__rnd.randint(2, 10)
            if attrs[k][2] == "string":

                attrs[k][0] = [
                    [
                        attrs[k][0] * self.__rnd.randint(1, 3)
                        for c in range(mlen)]
                    for c2 in range(self.__rnd.randint(2, 10))
                ]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [
                    [
                        attrs[k][0] * self.__rnd.randint(0, 3)
                        for c in range(mlen)]
                    for c2 in range(self.__rnd.randint(2, 10))
                ]
            else:
                if k == 'bool':
                    attrs[k][0] = [
                        [
                            bool(self.__rnd.randint(0, 1))
                            for c in range(mlen)]
                        for c2 in range(self.__rnd.randint(2, 10))
                    ]
                else:
                    attrs[k][0] = [
                        [
                            ("true" if self.__rnd.randint(0, 1) else "false")
                            for c in range(mlen)]
                        for c2 in range(self.__rnd.randint(2, 10))
                    ]

            attrs[k][3] = (len(attrs[k][0]), len(attrs[k][0][0]))

            el[k] = EAttribute({"name": k, "type": attrs[k][1]}, fi)
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].strategy = stt
            el[k].content = [str(attrs[k][0])]
            self.assertEqual(el[k].h5Object, None)
            self.assertEqual(el[k].store(), None)
            self.assertEqual(fi.tagAttributes[k], (
                attrs[k][1], str(attrs[k][0]), attrs[k][3]))

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_no(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My_string", "NX_CHAR", "string"],
            #            "string":["My_string","NX_CHAR", "string"],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-123, "NX_INT", "int64"],
            "int8": [12, "NX_INT8", "int8"],
            "int16": [-123, "NX_INT16", "int16"],
            "int32": [12345, "NX_INT32", "int32"],
            "int64": [-12345, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [12, "NX_UINT8", "uint8"],
            "uint16": [123, "NX_UINT16", "uint16"],
            "uint32": [12345, "NX_UINT32", "uint32"],
            "uint64": [12345, "NX_UINT64", "uint64"],
            "float": [-12.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool"],
            "bool3": ["false", "NX_BOOLEAN", "bool"],
            "bool4": ["true", "NX_BOOLEAN", "bool"]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        for k in attrs.keys():
            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '')
            ds = TstDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(0)), at[...])

            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at[...]) <= attrs[k][3])
            else:
                self.assertEqual(at[...], '' if attrs[k][2] == 'string' else 0)

        for k in attrs.keys():
            el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]), [])
            el[k]._createAttributes()
            at = el[k].h5Object.attributes[k]
            self._sc.checkScalarAttribute(
                el[k].h5Object, k, attrs[k][2] or 'string', attrs[k][0],
                attrs[k][3] if len(attrs[k]) > 3 else 0)

        for k in attrs.keys():
            el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]), [1])
            el[k]._createAttributes()
            at = el[k].h5Object.attributes[k]
            self._sc.checkScalarAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][3] if len(attrs[k]) > 3 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_no_string_shape_reduction(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "datetime": ["12 34 34", "NX_DATE_TIME", "string"],
            "iso8601": ["12 3434", "ISO8601", "string"],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        for k in attrs.keys():
            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '')
            ds = TstDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(0)), at[...])

            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at[...]) <= attrs[k][3])
            else:
                self.assertEqual(at[...], '' if attrs[k][2] == 'string' else 0)

        for k in attrs.keys():
            el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]), [1])
            el[k]._createAttributes()
            at = el[k].h5Object.attributes[k]
            self._sc.checkScalarAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][3] if len(attrs[k]) > 3 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_noname(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-123, "NX_INT", "int64"],
            "int8": [12, "NX_INT8", "int8"],
            "int16": [-123, "NX_INT16", "int16"],
            "int32": [12345, "NX_INT32", "int32"],
            "int64": [-12345, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [12, "NX_UINT8", "uint8"],
            "uint16": [123, "NX_UINT16", "uint16"],
            "uint32": [12345, "NX_UINT32", "uint32"],
            "uint64": [12345, "NX_UINT64", "uint64"],
            "float": [-12.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool"],
            "bool3": ["false", "NX_BOOLEAN", "bool"],
            "bool4": ["true", "NX_BOOLEAN", "bool"]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        for k in attrs.keys():
            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '')
            ds = TstDataSource()
            ds.valid = True
            ds.value = {
                "rank": NTP.rTf[0], "value": attrs[k][0],
                "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                      else "string"], "shape": [0, 0]}
            el[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(0)), at[...])

            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at[...]) <= attrs[k][3])
            else:
                self.assertEqual(at[...], '' if attrs[k][2] == 'string' else 0)

        for k in attrs.keys():
            self.assertEqual(ea[k].name, "")

            ea[k].run()
            self.assertEqual(ea[k].name, "")
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(0)), at[...])

            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at[...]) <= attrs[k][3])
            else:
                self.assertEqual(at[...], '' if attrs[k][2] == 'string' else 0)
        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_0d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-123, "NX_INT", "int64"],
            "int8": [12, "NX_INT8", "int8"],
            "int16": [-123, "NX_INT16", "int16"],
            "int32": [12345, "NX_INT32", "int32"],
            "int64": [-12345, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [12, "NX_UINT8", "uint8"],
            "uint16": [123, "NX_UINT16", "uint16"],
            "uint32": [12345, "NX_UINT32", "uint32"],
            "uint64": [12345, "NX_UINT64", "uint64"],
            "float": [-12.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool"],
            "bool3": ["false", "NX_BOOLEAN", "bool"],
            "bool4": ["true", "NX_BOOLEAN", "bool"]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        for k in attrs.keys():
            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '')
            ds = TstDataSource()
            ds.valid = True
            ds.value = {
                "rank": NTP.rTf[0],
                "value": attrs[k][0] if attrs[k][2] != "bool"
                else Converters.toBool(attrs[k][0]),
                "tangoDType": NTP.pTt[(attrs[k][2])
                                      if attrs[k][2] else "string"],
                "shape": [0, 0]}
            ea[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(0)), at[...])

            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at[...]) <= attrs[k][3])
            else:
                self.assertEqual(at[...], '' if attrs[k][2] == 'string' else 0)

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].run()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)

            self._sc.checkScalarAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][3] if len(attrs[k]) > 3 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_0d_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["", "NX_CHAR", "string"],
            "datetime": ["", "NX_DATE_TIME", "string"],
            "iso8601": ["", "ISO8601", "string"],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max,
                    "NX_INT", "int64"],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max,
                     "NX_INT8", "int8"],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max,
                      "NX_INT16", "int16"],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max,
                      "NX_INT32", "int32"],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max,
                      "NX_INT64", "int64"],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                     "NX_UINT", "uint64"],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64"],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8"],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16"],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32"],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64"],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64"],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool"],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        for k in attrs.keys():
            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '')
            ds = TstDataSource()
            ds.valid = True
            ds.value = {"rank": NTP.rTf[0], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else Converters.toBool(attrs[k][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [0, 0]}
            ea[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(
                at.dtype, attrs[k][2] if attrs[k][2] else "string")
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(0)), at[...])

            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at[...]) <= attrs[k][3])
            else:
                self.assertEqual(at[...], '' if attrs[k][
                                 2] == 'string' or not attrs[k][2] else 0)

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].markFailed()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            # print el[k].h5Object, k, attrs[k][2], attrs[k][0]
            self._sc.checkScalarAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][3] if len(attrs[k]) > 3 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_0d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-123, "NX_INT", "int64"],
            "int8": [12, "NX_INT8", "int8"],
            "int16": [-123, "NX_INT16", "int16"],
            "int32": [12345, "NX_INT32", "int32"],
            "int64": [-12345, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [12, "NX_UINT8", "uint8"],
            "uint16": [123, "NX_UINT16", "uint16"],
            "uint32": [12345, "NX_UINT32", "uint32"],
            "uint64": [12345, "NX_UINT64", "uint64"],
            "float": [-12.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool"],
            "bool3": ["false", "NX_BOOLEAN", "bool"],
            "bool4": ["true", "NX_BOOLEAN", "bool"]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        for k in attrs.keys():
            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '')
            ds = TstDataSource()
            ds.valid = True
            ds.value = {"rank": NTP.rTf[0], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else Converters.toBool(attrs[k][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [1, 0]}
            ea[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(0)), at[...])

            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at[...]) <= attrs[k][3])
            else:
                self.assertEqual(at[...], '' if attrs[k][2] == 'string' else 0)

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].run()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)

            self._sc.checkScalarAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][3] if len(attrs[k]) > 3 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_0d_single_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["", "NX_CHAR", "string"],
            "datetime": ["", "NX_DATE_TIME", "string"],
            "iso8601": ["", "ISO8601", "string"],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max,
                    "NX_INT", "int64"],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max,
                     "NX_INT8", "int8"],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max,
                      "NX_INT16", "int16"],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max,
                      "NX_INT32", "int32"],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max,
                      "NX_INT64", "int64"],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                     "NX_UINT", "uint64"],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64"],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8"],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16"],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32"],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64"],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64"],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool"],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        for k in attrs.keys():
            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '')
            ds = TstDataSource()
            ds.valid = True
            ds.value = {
                "rank": NTP.rTf[0],
                "value": attrs[k][0] if attrs[k][2] != "bool"
                else Converters.toBool(attrs[k][0]),
                "tangoDType": NTP.pTt[(attrs[k][2])
                                      if attrs[k][2] else "string"],
                "shape": [1, 0]}
            ea[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(
                at.dtype, attrs[k][2] if attrs[k][2] else "string")
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(0)), at[...])

            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at[...]) <= attrs[k][3])
            else:
                self.assertEqual(at[...], '' if attrs[k][
                                 2] == 'string' or not attrs[k][2] else 0)

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].markFailed()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)

            self._sc.checkScalarAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][3] if len(attrs[k]) > 3 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        for k in attrs.keys():
            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '', (1,))
            ds = TstDataSource()
            ds.valid = True
            ds.value = {
                "rank": NTP.rTf[1], "value": [attrs[k][0]]
                if attrs[k][2] != "bool"
                else [Converters.toBool(attrs[k][0])],
                "tangoDType": NTP.pTt[(attrs[k][2])
                                      if attrs[k][2] else "string"],
                "shape": [1, 0]}
            ea[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].run()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)

            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(ea[k].h5Object.shape, (1,))
                self._sc.checkSpectrumAttribute(
                    el[k].h5Object, k, attrs[k][2], [attrs[k][0]],
                    attrs[k][4] if len(attrs[k]) > 4 else 0)
            else:
                self.assertEqual(ea[k].h5Object.shape, (1,))
                self._sc.checkScalarAttribute(
                    el[k].h5Object, k, attrs[k][2], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_1d_single_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["", "NX_CHAR", "string", (1,)],
            "datetime": ["", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["", "ISO8601", "string", (1,)],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max,
                    "NX_INT", "int64", (1,)],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max,
                     "NX_INT8", "int8", (1,)],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max,
                      "NX_INT16", "int16", (1,)],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max,
                      "NX_INT32", "int32", (1,)],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max,
                      "NX_INT64", "int64", (1,)],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                     "NX_UINT", "uint64", (1,)],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64", (1,)],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8", (1,)],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16", (1,)],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64", (1,)],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool", (1,)],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        for k in attrs.keys():
            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            if attrs[k][2] and attrs[k][2] != 'string':
                el[k].tagAttributes[k] = (attrs[k][1], '', (1,))
            else:
                el[k].tagAttributes[k] = (attrs[k][1], '',)
            ds = TstDataSource()
            ds.valid = True
            ds.value = {"rank": NTP.rTf[1], "value": [attrs[k][0]]
                        if attrs[k][2] != "bool"
                        else [Converters.toBool(attrs[k][0])],
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [1, 0]}
            ea[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            self.assertEqual(ea[k].markFailed(), None)
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            if attrs[k][2] and attrs[k][2] != 'string':
                self._sc.checkSpectrumAttribute(
                    el[k].h5Object, k, attrs[k][2], [attrs[k][0]],
                    attrs[k][5] if len(attrs[k]) > 5 else 0)
            else:
                self._sc.checkScalarAttribute(
                    el[k].h5Object, k, attrs[k][2], attrs[k][0],
                    attrs[k][5] if len(attrs[k]) > 5 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_1d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] = [bool(self.__rnd.randint(0, 1))
                                   for c in range(mlen[0])]
                else:
                    attrs[k][0] = [("true" if self.__rnd.randint(0, 1)
                                    else "false")
                                   for c in range(mlen[0])]

            attrs[k][3] = (mlen[0],)

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '', (attrs[k][3][0],))
            ds = TstDataSource()
            ds.valid = True

            ds.value = {"rank": NTP.rTf[1], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else [Converters.toBool(c) for c in attrs[k][0]],
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], 0]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].run()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            self._sc.checkSpectrumAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][4] if len(attrs[k]) > 4 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_1d_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["", "NX_CHAR", "string", (1,)],
            "datetime": ["", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["", "ISO8601", "string", (1,)],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max,
                    "NX_INT", "int64", (1,)],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max,
                     "NX_INT8", "int8", (1,)],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max,
                      "NX_INT16", "int16", (1,)],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max,
                      "NX_INT32", "int32", (1,)],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max,
                      "NX_INT64", "int64", (1,)],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                     "NX_UINT", "uint64", (1,)],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64", (1,)],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8", (1,)],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16", (1,)],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64", (1,)],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool", (1,)],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [attrs[k][0] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] = [False for c in range(mlen[0])]

            attrs[k][3] = (mlen[0],)

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], '', (attrs[k][3][0],))
            ds = TstDataSource()
            ds.valid = True

            ds.value = {"rank": NTP.rTf[1], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else [Converters.toBool(c) for c in attrs[k][0]],
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 0]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].markFailed()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            self._sc.checkSpectrumAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][5] if len(attrs[k]) > 5 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_2d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] == "string":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(1, 3)]]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(0, 3)]]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [[bool(self.__rnd.randint(0, 1))]]
                else:
                    attrs[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                     else "false")
                                    ]]

            attrs[k][3] = (1, 1)

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], '', (attrs[k][3][0], attrs[k][3][1]))
            ds = TstDataSource()
            ds.valid = True

            ds.value = {"rank": NTP.rTf[2], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else [[Converters.toBool(c) for c in attrs[k][0][0]]],
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], attrs[k][3][1]]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].run()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            self._sc.checkImageAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][4] if len(attrs[k]) > 4 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_2d_single_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        attrs = {
            "string": ["", "NX_CHAR", "string", (1,)],
            "datetime": ["", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["", "ISO8601", "string", (1,)],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max,
                    "NX_INT", "int64", (1,)],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max,
                     "NX_INT8", "int8", (1,)],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max,
                      "NX_INT16", "int16", (1,)],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max,
                      "NX_INT32", "int32", (1,)],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max,
                      "NX_INT64", "int64", (1,)],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                     "NX_UINT", "uint64", (1,)],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64", (1,)],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8", (1,)],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16", (1,)],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64", (1,)],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool", (1,)],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            attrs[k][0] = [[attrs[k][0]]]

            attrs[k][3] = (1, 1)

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], '', (attrs[k][3][0], attrs[k][3][1]))
            ds = TstDataSource()
            ds.valid = True

            ds.value = {"rank": NTP.rTf[2], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else [[Converters.toBool(c)
                               for c in attrs[k][0][0]]],
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], attrs[k][3][1]]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].markFailed()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            self._sc.checkImageAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][5] if len(attrs[k]) > 5 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_2d_double(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] == "string":
                attrs[k][0] = [
                    [attrs[k][0] * self.__rnd.randint(1, 3)
                     for c in range(self.__rnd.randint(2, 10))]]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [
                    [attrs[k][0] * self.__rnd.randint(0, 3)
                     for c in range(self.__rnd.randint(2, 10))]]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [[bool(self.__rnd.randint(0, 1))
                                    for c in range(self.__rnd.randint(2, 10))]]
                else:
                    attrs[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                     else "false")
                                    for c in range(self.__rnd.randint(2, 10))]]

            attrs[k][3] = (1, len(attrs[k][0][0]))

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], '', (attrs[k][3][0], attrs[k][3][1]))
            ds = TstDataSource()
            ds.valid = True

            ds.value = {"rank": NTP.rTf[2], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else [[Converters.toBool(c) for c in attrs[k][0][0]]],
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], attrs[k][3][1]]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].run()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            self._sc.checkImageAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][4] if len(attrs[k]) > 4 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_2d_double_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["", "NX_CHAR", "string", (1,)],
            "datetime": ["", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["", "ISO8601", "string", (1,)],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max, "NX_INT",
                    "int64", (1,)],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max, "NX_INT8",
                     "int8", (1,)],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max, "NX_INT16",
                      "int16", (1,)],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max, "NX_INT32",
                      "int32", (1,)],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max, "NX_INT64",
                      "int64", (1,)],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max, "NX_UINT",
                     "uint64", (1,)],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64", (1,)],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8", (1,)],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16", (1,)],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64", (1,)],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool", (1,)],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]
            attrs[k][0] = [[attrs[k][0]
                            for c in range(self.__rnd.randint(2, 10))]]

            attrs[k][3] = (1, len(attrs[k][0][0]))

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], '', (attrs[k][3][0], attrs[k][3][1]))
            ds = TstDataSource()
            ds.valid = True

            ds.value = {
                "rank": NTP.rTf[2], "value": attrs[k][0]
                if attrs[k][2] != "bool"
                else [[Converters.toBool(c) for c in attrs[k][0][0]]],
                "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                      else "string"],
                "shape": [attrs[k][3][0], attrs[k][3][1]]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].markFailed()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            self._sc.checkImageAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][5] if len(attrs[k]) > 5 else 0)

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_2d_double_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            if attrs[k][2] == "string":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(1, 3)]
                               for c in range(self.__rnd.randint(2, 10))]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(0, 3)]
                               for c in range(self.__rnd.randint(2, 10))]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [
                        [
                            bool(self.__rnd.randint(0, 1))]
                        for c in range(self.__rnd.randint(2, 10))
                    ]
                else:
                    attrs[k][0] = [
                        [
                            ("true" if self.__rnd.randint(0, 1) else "false")
                        ]
                        for c in range(self.__rnd.randint(2, 10))
                    ]

            attrs[k][3] = (len(attrs[k][0]), 1)

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], '', (attrs[k][3][0], attrs[k][3][1]))
            ds = TstDataSource()
            ds.valid = True

            print
            ds.value = {
                "rank": NTP.rTf[2], "value": attrs[k][0]
                if attrs[k][2] != "bool"
                else [[Converters.toBool(c[0])] for c in attrs[k][0]],
                "tangoDType": NTP.pTt[(attrs[k][2])
                                      if attrs[k][2] else "string"],
                "shape": [attrs[k][3][0], attrs[k][3][1]]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].run()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
            self._sc.checkImageAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][4] if len(attrs[k]) > 4 else 0)
        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_2d_double_2_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["", "NX_CHAR", "string", (1,)],
            "datetime": ["", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["", "ISO8601", "string", (1,)],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max,
                    "NX_INT", "int64", (1,)],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max,
                     "NX_INT8", "int8", (1,)],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max,
                      "NX_INT16", "int16", (1,)],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max,
                      "NX_INT32", "int32", (1,)],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max,
                      "NX_INT64", "int64", (1,)],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                     "NX_UINT", "uint64", (1,)],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64", (1,)],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8", (1,)],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16", (1,)],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64", (1,)],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool", (1,)],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            attrs[k][0] = [[attrs[k][0]]
                           for c in range(self.__rnd.randint(2, 10))]

            attrs[k][3] = (len(attrs[k][0]), 1)

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], '', (attrs[k][3][0], attrs[k][3][1]))
            ds = TstDataSource()
            ds.valid = True

            print
            ds.value = {"rank": NTP.rTf[2], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else [[Converters.toBool(c[0])] for c in attrs[k][0]],
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], attrs[k][3][1]]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].markFailed()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)
#            if ea[k].h5Object.dtype != 'string':
            self._sc.checkImageAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][5] if len(attrs[k]) > 5 else 0)
#            else:
#                self.assertEqual(
#                   ea[k].error[0],
#                   'Data for %s not found. DATASOURCE:Test DataSource' %k)
#                self.assertEqual(
#                    ea[k].error[1],
#                    'Storing multi-dimension string attributes not'
#                     ' supported by pniio')
        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_2d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", (1,)],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,)],
            "int": [-123, "NX_INT", "int64", (1,)],
            "int8": [12, "NX_INT8", "int8", (1,)],
            "int16": [-123, "NX_INT16", "int16", (1,)],
            "int32": [12345, "NX_INT32", "int32", (1,)],
            "int64": [-12345, "NX_INT64", "int64", (1,)],
            "uint": [123, "NX_UINT", "uint64", (1,)],
            "uint8": [12, "NX_UINT8", "uint8", (1,)],
            "uint16": [123, "NX_UINT16", "uint16", (1,)],
            "uint32": [12345, "NX_UINT32", "uint32", (1,)],
            "uint64": [12345, "NX_UINT64", "uint64", (1,)],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["true", "NX_BOOLEAN", "bool", (1,)]
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            mlen = self.__rnd.randint(2, 10)
            if attrs[k][2] == "string":

                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(1, 3)
                                for c in range(mlen)]
                               for c2 in range(self.__rnd.randint(2, 10))]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(0, 3)
                                for c in range(mlen)]
                               for c2 in range(self.__rnd.randint(2, 10))]
            else:
                if k == 'bool':
                    attrs[k][0] = [[bool(self.__rnd.randint(0, 1))
                                    for c in range(mlen)]
                                   for c2 in range(self.__rnd.randint(2, 10))]
                else:
                    attrs[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                     else "false")
                                    for c in range(mlen)]
                                   for c2 in range(self.__rnd.randint(2, 10))]

            attrs[k][3] = (len(attrs[k][0]), len(attrs[k][0][0]))

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], '', (attrs[k][3][0], attrs[k][3][1]))
            ds = TstDataSource()
            ds.valid = True

            print
            ds.value = {"rank": NTP.rTf[2], "value": attrs[k][0]
                        if attrs[k][2] != "bool"
                        else [[Converters.toBool(c) for c in row]
                              for row in attrs[k][0]],
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], attrs[k][3][1]]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].run()
            self.assertEqual(type(ea[k].h5Object), H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)

            self._sc.checkImageAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][4] if len(attrs[k]) > 4 else 0)
        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_run_value_2d_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        attrs = {
            "string": ["", "NX_CHAR", "string", (1,)],
            "datetime": ["", "NX_DATE_TIME", "string", (1,)],
            "iso8601": ["", "ISO8601", "string", (1,)],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max, "NX_INT",
                    "int64", (1,)],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max, "NX_INT8",
                     "int8", (1,)],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max, "NX_INT16",
                      "int16", (1,)],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max, "NX_INT32",
                      "int32", (1,)],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max, "NX_INT64",
                      "int64", (1,)],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max, "NX_UINT",
                     "uint64", (1,)],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64", (1,)],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8", (1,)],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16", (1,)],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64", (1,)],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool", (1,)],
        }

        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        ea = {}
        quin = 0
        for k in attrs.keys():

            quin = (quin + 1) % 4
            stt = [None, 'INIT', 'STEP', 'FINAL', 'POSTRUN'][quin]

            mlen = self.__rnd.randint(2, 10)
            attrs[k][0] = [[attrs[k][0]
                            for c in range(mlen)]
                           for c2 in range(self.__rnd.randint(2, 10))]

            attrs[k][3] = (len(attrs[k][0]), len(attrs[k][0][0]))

            el[k] = EField({"name": k, "units": "m"}, eFile)
            el[k].content = ["Test"]
            ea[k] = EAttribute({"name": k, "type": attrs[k][1]}, el[k])
            ea[k].name = k

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], '', (attrs[k][3][0], attrs[k][3][1]))
            ds = TstDataSource()
            ds.valid = True

            print
            ds.value = {
                "rank": NTP.rTf[2], "value": attrs[k][0]
                if attrs[k][2] != "bool"
                else [[Converters.toBool(c) for c in row]
                      for row in attrs[k][0]],
                "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                      else "string"],
                "shape": [attrs[k][3][0], attrs[k][3][1]]}
            ea[k].source = ds
            el[k].strategy = stt

            el[k].store()
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])

        for k in attrs.keys():
            self.assertEqual(ea[k].name, k)
            self.assertEqual(ea[k].h5Object, None)
            ea[k].markFailed()
            self.assertEqual(type(ea[k].h5Object),
                             H5CppWriter.H5CppAttribute)
            self.assertEqual(ea[k].h5Object.name, k)

            self._sc.checkImageAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][5] if len(attrs[k]) > 5 else 0)
        self._nxFile.close()

        os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
