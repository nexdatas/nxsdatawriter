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
# \file EFieldTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import binascii
import struct
import numpy
import time


from nxswriter.FElement import FElementWithAttr
from nxswriter.FElement import FElement
from nxswriter.EField import EField
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile
from nxswriter.Types import NTP, Converters

from nxstools import filewriter as FileWriter
from nxstools import h5cppwriter as H5CppWriter

from nxswriter.Errors import XMLSettingSyntaxError

try:
    from TstDataSource import TstDataSource
except Exception:
    from .TstDataSource import TstDataSource


try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

PNIIO = True


# test fixture
class EFieldH5CppTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"name": "test", "units": "m"}
        self._gattrs = {"name": "test", "type": "NXentry"}
        self._gname = "testGroup"
        self._gtype = "NXentry"
        self._fdname = "testField"
        self._fdtype = "int64"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self._sc = Checker(self)

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)
#        self.__seed =241361343400098333007607831038323262554

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)
        print("CHECKER SEED = %s" % self._sc.seed)

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
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()

        el = EField(self._fattrs, None)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.source, None)
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.source, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)

        self.assertEqual(el.store(), None)

        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_default_thesame(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.source, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)

#        self.myAssertRaise(ValueError, el.store)
#        el.content= ["sdf"]
        self.assertEqual(el.store(), None)

        self.myAssertRaise(XMLSettingSyntaxError, el.store)

        self._nxFile.close()
        os.remove(self._fname)
    # default store method
    # \brief It tests default settings

    def test_store_default_reload(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.source, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)

#        self.myAssertRaise(ValueError, el.store)
#        el.content= ["sdf"]
        self.assertEqual(el.store(), None)

        self.myAssertRaise(XMLSettingSyntaxError, el.store)
        el = EField(self._fattrs, eFile, reloadmode=True)
        self.assertEqual(el.store(), None)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.source, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        fattrs = {"name": "test", "units": "m", "type": "NX_INT"}
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(fattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.source, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)

        self.myAssertRaise(ValueError, el.store)

        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_grows_1(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        ds = TstDataSource()
        el.source = ds
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('INIT', None))

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppField)

        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_grows_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        ds = TstDataSource()
        el.source = ds
        el.strategy = 'STEP'
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'STEP')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('STEP', None))
        self.assertEqual(el.grows, 1)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_grows_3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        ds = TstDataSource()
        el.source = ds
        el.strategy = 'STEP'
        el.grows = 2
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'STEP')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, 2)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('STEP', None))
        self.assertEqual(el.grows, 1)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_grows_4(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        ds = TstDataSource()
        el.source = ds
        el.strategy = 'INIT'
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('INIT', None))
        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_grows_5(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        ds = TstDataSource()
        ds.valid = False
        el.source = ds
        el.strategy = 'STEP'
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'STEP')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), None)
        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_grows_7(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField(self._fattrs, eFile)
        el.rank = '2'
        ds = TstDataSource()
        ds.dims = [3, 4]
        el.source = ds
        el.strategy = 'STEP'
        el.grows = 2
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "2")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'STEP')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, 2)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('STEP', None))
        self.assertEqual(el.grows, 2)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_grows_6(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fattrs = {"name": "test", "units": "m", "type": "NX_INT64"}
        el = EField(fattrs, eFile)
        el.rank = '2'
        ds = TstDataSource()
        ds.dims = [3, 4]
        el.source = ds
        el.strategy = 'STEP'
        el.grows = 2
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "2")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'STEP')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, 2)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('STEP', None))
        self.assertEqual(el.grows, 2)
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_0d_step(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "string2": ["My string", "NX_CHAR", ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-132, "NX_INT", "int64"],
            "int8": [13, "NX_INT8", "int8"],
            "int16": [-223, "NX_INT16", "int16"],
            "int32": [13235, "NX_INT32", "int32"],
            "int64": [-12425, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [65, "NX_UINT8", "uint8"],
            "uint16": [453, "NX_UINT16", "uint16"],
            "uint32": [12235, "NX_UINT32", "uint32"],
            "uint64": [14345, "NX_UINT64", "uint64"],
            "float": [-16.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-2.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-4.355e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-2.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        for k in attrs:
            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, 'STEP')
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), ("STEP", None))
            self.assertEqual(el[k].grows, 1)

        for k in attrs:
            h5 = el[k].h5Object
            self.assertEqual(h5.shape, (0,))
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.size, 0)
            self.assertEqual(len(h5.attributes), 2)
            self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
            self._sc.checkScalarAttribute(h5, "units", "string", "m")

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_0d_initfinal(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "string2": ["My string", "NX_CHAR", ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-132, "NX_INT", "int64"],
            "int8": [13, "NX_INT8", "int8"],
            "int16": [-223, "NX_INT16", "int16"],
            "int32": [13235, "NX_INT32", "int32"],
            "int64": [-12425, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [65, "NX_UINT8", "uint8"],
            "uint16": [453, "NX_UINT16", "uint16"],
            "uint32": [12235, "NX_UINT32", "uint32"],
            "uint64": [14345, "NX_UINT64", "uint64"],
            "float": [-16.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-2.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-4.355e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-2.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        flip = False
        for k in attrs:
            flip = not flip
            stt = 'INIT' if flip else 'FINAL'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].source = ds

            el[k].strategy = stt

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt, None))
            self.assertEqual(el[k].grows, None)

        for k in attrs:
            h5 = el[k].h5Object
            if attrs[k][2] and attrs[k][2] not in ['string']:
                self.assertEqual(h5.shape, (1,))
            else:
                self.assertEqual(h5.shape, ())
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.size, 1)
            self.assertEqual(len(h5.attributes), 2)
            self._sc.checkScalarAttribute(
                h5, "type", "string", attrs[k][1])
            self._sc.checkScalarAttribute(h5, "units", "string", "m")

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_0d_postrun(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "none": ["My string", "NX_CHAR", ""],
            "string": ["My string", "NX_CHAR", "string"],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-132, "NX_INT", "int64"],
            "int8": [13, "NX_INT8", "int8"],
            "int16": [-223, "NX_INT16", "int16"],
            "int32": [13235, "NX_INT32", "int32"],
            "int64": [-12425, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [65, "NX_UINT8", "uint8"],
            "uint16": [453, "NX_UINT16", "uint16"],
            "uint32": [12235, "NX_UINT32", "uint32"],
            "uint64": [14345, "NX_UINT64", "uint64"],
            "float": [-16.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-2.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-4.355e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-2.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        for k in attrs:
            stt = 'POSTRUN'
            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].postrun = k
            el[k].strategy = stt

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt, None))
            self.assertEqual(el[k].grows, None)

        for k in attrs:
            h5 = el[k].h5Object
            self.assertEqual(h5.shape, (0,))
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.size, 0)
            self.assertEqual(len(h5.attributes), 3)
            self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
            self._sc.checkScalarAttribute(h5, "units", "string", "m")
            self._sc.checkScalarAttribute(h5, "postrun", "string", k)

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_1d_step(self):
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quot = 0
        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None

            if attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for r in range(mlen[0])]
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

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].rank = "1"
            el[k].lengths = {"1": str(attrs[k][3][0])}
            el[k].source = ds
            el[k].grows = grow

            el[k].strategy = 'STEP'

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {"1": str(attrs[k][3][0])})
            self.assertEqual(el[k].strategy, 'STEP')
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), ("STEP", None))
            self.assertEqual(el[k].grows, grow if grow and grow else 1)

        trip = 0
        for k in attrs:
            trip = (trip + 1) % 3
            grow = trip - 1 if trip else None
            h5 = el[k].h5Object
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')
            if attrs[k][2] and attrs[k][2] != 'string_old':
                if el[k].grows == 2:
                    self.assertEqual(h5.shape, (1, 0))
                else:
                    self.assertEqual(h5.shape, (0, 1))

                self.assertEqual(h5.size, 0)
                self.assertEqual(len(h5.attributes), 2)
                self._sc.checkScalarAttribute(
                    h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
            else:
                if el[k].grows == 2:
                    self.assertEqual(h5.shape, (attrs[k][3][0], 0))
                else:
                    self.assertEqual(h5.shape, (0, attrs[k][3][0]))

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_1d_initfinal(self):
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        flip = False
        for k in attrs:
            flip = not flip
            stt = 'INIT' if flip else 'FINAL'

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
                    attrs[k][0] = [
                        ("true" if self.__rnd.randint(0, 1) else "false")
                        for c in range(mlen[0])]

            attrs[k][3] = (mlen[0],)

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].rank = "1"
            el[k].lengths = {"1": str(attrs[k][3][0])}
            el[k].source = ds
            el[k].strategy = stt

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {"1": str(attrs[k][3][0])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt, None))
            self.assertEqual(el[k].grows, None)

        for k in attrs:
            h5 = el[k].h5Object
#            self.assertEqual(h5.shape,(attrs[k][3][0],))
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.shape, (1,))
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(h5.size, 1)
                self.assertEqual(len(h5.attributes), 2)
                self._sc.checkScalarAttribute(
                    h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_1d_postrun(self):
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        flip = False
        for k in attrs:
            flip = not flip
            stt = 'POSTRUN'

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
                    attrs[k][0] = [
                        ("true" if self.__rnd.randint(0, 1) else "false")
                        for c in range(mlen[0])]

            attrs[k][3] = (mlen[0],)

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].rank = "1"
            el[k].lengths = {"1": str(attrs[k][3][0])}
            el[k].source = ds
            el[k].strategy = stt
            el[k].postrun = k

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {"1": str(attrs[k][3][0])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt, None))
            self.assertEqual(el[k].grows, None)

        for k in attrs:
            h5 = el[k].h5Object
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.shape, (1,))
            self.assertEqual(h5.size, 1)
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(len(h5.attributes), 3)
                self._sc.checkScalarAttribute(
                    h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
                self._sc.checkScalarAttribute(h5, "postrun", "string", k)

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_2d_step(self):
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

        for k in attrs.keys():
            if attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [[
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for c in range(mlen[1])] for i in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] = [[
                        bool(self.__rnd.randint(0, 1))
                        for c in range(mlen[1])] for r in range(mlen[0])]
                else:
                    attrs[k][0] = [[
                        ("True" if self.__rnd.randint(0, 1) else "False")
                        for c in range(mlen[1])] for r in range(mlen[0])]

            attrs[k][3] = (mlen[0], mlen[1])

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        for k in attrs:
            quin = (quin + 1) % 5
            grow = quin - 1 if quin else None

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].source = ds
            el[k].grows = grow
            el[k].strategy = 'STEP'

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(
                el[k].lengths, {"1": str(attrs[k][3][0]),
                                "2": str(attrs[k][3][1])})
            self.assertEqual(el[k].strategy, 'STEP')
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), ("STEP", None))
#            if attrs[k][2] and attrs[k][2] != 'string':
            self.assertEqual(el[k].grows, grow if grow and grow else 1)

        for k in attrs:
            h5 = el[k].h5Object
            print(h5.dtype)
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')
            if attrs[k][2] and attrs[k][2] != 'string_old':
                if el[k].grows == 3:
                    self.assertEqual(h5.shape, (1, 1, 0))
                elif el[k].grows == 2:
                    self.assertEqual(h5.shape, (1, 0, 1))
                else:
                    self.assertEqual(h5.shape, (0, 1, 1))
                self.assertEqual(h5.size, 0)
                self.assertEqual(len(h5.attributes), 2)
                self._sc.checkScalarAttribute(
                    h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
            else:
                self.assertEqual(h5.shape, (0, attrs[k][3][0],
                                            attrs[k][3][1]))

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_2d_initfinal(self):
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

        for k in attrs.keys():
            if attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [
                    [[attrs[k][0] * self.__rnd.randint(0, 3)]
                     for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] = [[
                        bool(self.__rnd.randint(0, 1))
                        for c in range(mlen[1])] for r in range(mlen[0])]
                else:
                    attrs[k][0] = [[
                        ("True" if self.__rnd.randint(0, 1) else "False")
                        for c in range(mlen[1])] for r in range(mlen[0])]

            attrs[k][3] = (mlen[0], mlen[1])

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        flip = False
        for k in attrs:
            flip = not flip
            quin = (quin + 1) % 5
            # grow = quin - 1 if quin else None
            stt = 'INIT' if flip else 'FINAL'

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].source = ds
            el[k].strategy = stt

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(
                el[k].lengths, {"1": str(attrs[k][3][0]),
                                "2": str(attrs[k][3][1])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt, None))
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(el[k].grows, None)

        for k in attrs:
            h5 = el[k].h5Object
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')

            if attrs[k][2] and attrs[k][2] != 'string_old':
                self.assertEqual(h5.shape, (1, 1))
                self.assertEqual(h5.size, 1)
                self.assertEqual(len(h5.attributes), 2)
                self._sc.checkScalarAttribute(
                    h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
            else:
                self.assertEqual(h5.shape, (attrs[k][3][0], attrs[k][3][1]))

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_create_2d_postrun(self):
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

        for k in attrs.keys():
            if attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [[
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] = [[
                        bool(self.__rnd.randint(0, 1))
                        for c in range(mlen[1])] for r in range(mlen[0])]
                else:
                    attrs[k][0] = [[
                        ("True" if self.__rnd.randint(0, 1) else "False")
                        for c in range(mlen[1])] for r in range(mlen[0])]

            attrs[k][3] = (mlen[0], mlen[1])

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        flip = False
        for k in attrs:
            flip = not flip
            quin = (quin + 1) % 5
            # grow = quin - 1 if quin else None
            stt = 'INIT' if flip else 'FINAL'

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            ds = TstDataSource()
            ds.valid = True
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].source = ds
            el[k].postrun = k
            stt = 'POSTRUN'
            el[k].strategy = stt

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(
                el[k].lengths, {"1": str(attrs[k][3][0]),
                                "2": str(attrs[k][3][1])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt, None))
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(el[k].grows, None)

        for k in attrs:
            h5 = el[k].h5Object
            self.assertEqual(
                h5.dtype, attrs[k][2] if attrs[k][2] else 'string')
            if attrs[k][2] and attrs[k][2] != 'string_old':
                self.assertEqual(h5.shape, (1, 1))
                self.assertEqual(h5.size, 1)
                self.assertEqual(len(h5.attributes), 3)
                self._sc.checkScalarAttribute(
                    h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
                self._sc.checkScalarAttribute(h5, "postrun", "string", k)
            else:
                self.assertEqual(h5.shape, (attrs[k][3][0], attrs[k][3][1]))

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_createAttributes_aTn(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fattrs = {"name": "testfield", "type": "NX_INT"}
        maTn = {"signal": 1, "axis": 2, "primary": 3, "offset": 4,
                "stride": 6, "file_time": "12:34",
                "file_update_time": "12:45", "restricts": 12,
                "ignoreExtraGroups": True, "ignoreExtraFields": False,
                "ignoreExtraAttributes": True, "minOccus": 1, "maxOccus": 2
                }

        fattrs = dict(fattrs, **(maTn))
        el = EField(fattrs, eFile)

        ds = TstDataSource()
        ds.valid = True
        el.source = ds
        el.strategy = 'STEP'

        el.store()

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppField)
        self.assertEqual(el.h5Object.name, fattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 14)
        self.assertEqual(el.h5Object.attributes["type"][...], fattrs["type"])
        self.assertEqual(el.h5Object.attributes["type"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["type"].shape, ())

        for k in maTn.keys():
            self.assertEqual(el.h5Object.attributes[k][...], fattrs[k])
            self.assertEqual(
                el.h5Object.attributes[k].dtype, NTP.nTnp[NTP.aTn[k]])
            self.assertEqual(el.h5Object.attributes[k].shape, ())

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_createAttributes_aTnv(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        fattrs = {"name": "testfield", "type": "NX_INT"}
        maTnv = {"vector": "1.2 12.3 13.3"}
        raTnv = {"vector": (1.2, 12.3, 13.3)}
        error = 1.e-14

        fattrs = dict(fattrs, **(maTnv))
        rattrs = dict(fattrs)
        rattrs = dict(rattrs, **(raTnv))

        el = EField(fattrs, eFile)

        ds = TstDataSource()
        ds.valid = True
        el.source = ds
        el.strategy = 'STEP'

        el.store()

        FileWriter.writer = H5CppWriter
        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppField)
        self.assertEqual(el.h5Object.name, fattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 2)
        self.assertEqual(el.h5Object.attributes["type"][...], fattrs["type"])
        self.assertEqual(el.h5Object.attributes["type"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["type"].shape, ())

        for k in raTnv.keys():
            for i in range(len(rattrs[k])):
                self.assertTrue(
                    abs(el.h5Object.attributes[k][...][i] -
                        rattrs[k][i]) <= error)
            self.assertEqual(
                el.h5Object.attributes[k].dtype, NTP.nTnp[NTP.aTnv[k]])
            self.assertEqual(
                el.h5Object.attributes[k].shape, (len(rattrs[k]),))

        self._nxFile.close()

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_createAttributes_0d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        for _ in range(1):
            attrs = {
                "string": ["My_string", "NX_CHAR", "string"],
                #            "string":["My string","NX_CHAR", "string"],
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

            FileWriter.writer = H5CppWriter
            self._nxFile = FileWriter.create_file(
                self._fname, overwrite=True).root()
            eFile = EFile({}, None, self._nxFile)

            el = {}
            for k in attrs.keys():
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)

                self.assertEqual(el[k].tagAttributes, {})
                el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]))
                ds = TstDataSource()
                ds.valid = True
                el[k].source = ds
                el[k].strategy = 'STEP'

                el[k].store()
                at = el[k].h5Attribute(k)
                self.assertEqual(at.dtype, attrs[k][2])
                if attrs[k][2] == "bool":
                    self.assertEqual(
                        Converters.toBool(str(attrs[k][0])), at[...])

                elif len(attrs[k]) > 3:
                    self.assertTrue(abs(at[...] - attrs[k][0]) <= attrs[k][3])
                else:
                    self.assertEqual(at[...], attrs[k][0])

            for k in attrs.keys():
                el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]), [])
                el[k]._createAttributes()
                at = el[k].h5Object.attributes[k]
                self._sc.checkScalarAttribute(
                    el[k].h5Object, k, attrs[k][2], attrs[k][0],
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
    def test_store_createAttributes_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            #            "string":["My string","NX_CHAR", "string" , (1,)],
            "string": ["My_string", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        el = {}
        for k in attrs.keys():
            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": "m"}, eFile)

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (
                attrs[k][1], str(attrs[k][0]), attrs[k][3])

            ds = TstDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store()
            el[k].h5Object.attributes[k]
            self._sc.checkScalarAttribute(
                el[k].h5Object, k, attrs[k][2], attrs[k][0],
                attrs[k][4] if len(attrs[k]) > 4 else 0)
            #            self._sc.checkSpectrumAttribute(
            # el[k].h5Object, k, attrs[k][2], [attrs[k][0]] ,
            # attrs[k][3] if len(attrs[k])>3 else 0)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_createAttributes_1d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        for i in range(10):
            attrs = {
                #            "string":["My string","NX_CHAR", "string" , (1,)],
                "string": ["My_string", "NX_CHAR", "string", (1,)],
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

            for k in attrs.keys():
                if attrs[k][2] == "string":
                    mlen = [
                        self.__rnd.randint(1, 10), self.__rnd.randint(1, 3)]
                    attrs[k][0] = [
                        attrs[k][0] * self.__rnd.randint(1, 3)
                        for r in range(mlen[0])]
                elif attrs[k][2] != "bool":
                    mlen = [
                        self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                    attrs[k][0] = [
                        attrs[k][0] * self.__rnd.randint(0, 3)
                        for r in range(mlen[0])]
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

            FileWriter.writer = H5CppWriter
            self._nxFile = FileWriter.create_file(
                self._fname, overwrite=True).root()
            eFile = EFile({}, None, self._nxFile)

            el = {}
            for k in attrs.keys():
                # print k, attrs[k][0]
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)

                self.assertEqual(el[k].tagAttributes, {})
                el[k].tagAttributes[k] = (attrs[k][1], "".join(
                    [str(it) + " " for it in attrs[k][0]]), attrs[k][3])
                # print el[k].tagAttributes[k]
                ds = TstDataSource()
                ds.valid = True
                el[k].source = ds
                el[k].strategy = 'STEP'

                el[k].store()

                el[k].h5Object.attributes[k]
                self._sc.checkSpectrumAttribute(
                    el[k].h5Object, k, attrs[k][2], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0)

            self._nxFile.close()
            os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_createAttributes_2d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        for i in range(10):

            attrs = {
                "string": ["My_string", "NX_CHAR", "string", (1,)],
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

            for k in attrs.keys():
                if attrs[k][2] == "string":
                    mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                        1, 10), self.__rnd.randint(0, 3)]
                    attrs[k][0] = [
                        [attrs[k][0] * self.__rnd.randint(1, 3)
                         for r in range(mlen[1])] for c in range(mlen[0])]
                elif attrs[k][2] != "bool":
                    mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                        1, 10), self.__rnd.randint(0, 3)]
                    attrs[k][0] = [
                        [attrs[k][0] * self.__rnd.randint(0, 3)
                         for r in range(mlen[1])] for c in range(mlen[0])]
                else:
                    mlen = [
                        self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                    if k == 'bool':
                        attrs[k][0] = [[
                            bool(self.__rnd.randint(0, 1))
                            for c in range(mlen[1])] for r in range(mlen[0])]
                    else:
                        attrs[k][0] = [[
                            ("True" if self.__rnd.randint(0, 1) else "False")
                            for c in range(mlen[1])]for r in range(mlen[0])]

                attrs[k][3] = (mlen[0], mlen[1])

            FileWriter.writer = H5CppWriter
            self._nxFile = FileWriter.create_file(
                self._fname, overwrite=True).root()
            eFile = EFile({}, None, self._nxFile)

            el = {}
            for k in attrs.keys():
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)

                self.assertEqual(el[k].tagAttributes, {})
                el[k].tagAttributes[k] = (
                    attrs[k][1],
                    "".join(["".join([str(it) + " " for it in sub]) +
                             "\n" for sub in attrs[k][0]]),
                    attrs[k][3]
                )

                ds = TstDataSource()
                ds.valid = True
                el[k].source = ds
                el[k].strategy = 'STEP'

                el[k].store()

                at = el[k].h5Object.attributes[k]
                self._sc.checkImageAttribute(
                    el[k].h5Object, k, attrs[k][2], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0)

                self.assertEqual(at.dtype, attrs[k][2])
                if attrs[k][2] == "bool":
                    for i in range(len(attrs[k][0])):
                        for j in range(len(attrs[k][0][i])):
                            self.assertEqual(
                                Converters.toBool(str(attrs[k][0][i][j])),
                                at[i, j])
                    pass
                elif len(attrs[k]) > 4:
                    for i in range(len(attrs[k][0])):
                        for j in range(len(attrs[k][0][i])):
                            self.assertTrue(
                                abs(at[i, j] - attrs[k][0][i][j]) <=
                                attrs[k][4])
                else:
                    for i in range(len(attrs[k][0])):
                        for j in range(len(attrs[k][0][i])):
                            if at.dtype == "string" and at.shape == (1,):
                                self.assertEqual(at[...], attrs[k][0][i][j])
                            else:
                                self.assertEqual(at[i, j], attrs[k][0][i][j])

            self._nxFile.close()
            os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_value_0d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "string2": ["My string", "NX_CHAR", ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-132, "NX_INT", "int64"],
            "int8": [13, "NX_INT8", "int8"],
            "int16": [-223, "NX_INT16", "int16"],
            "int32": [13235, "NX_INT32", "int32"],
            "int64": [-12425, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [65, "NX_UINT8", "uint8"],
            "uint16": [453, "NX_UINT16", "uint16"],
            "uint32": [12235, "NX_UINT32", "uint32"],
            "uint64": [14345, "NX_UINT64", "uint64"],
            "float": [-16.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-2.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-4.355e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-2.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        for k in attrs:
            quin = (quin + 1) % 5
            stt = [None, 'INIT', 'FINAL', 'STEP', 'POSTRUN'][quin]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            el[k].content.append(str(attrs[k][0]))

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [str(attrs[k][0])])
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].grows, None)
            if stt != 'POSTRUN':
                if stt in ['STEP'] or (
                        attrs[k][2] and attrs[k][2] not in ['string']):
                    self._sc.checkXMLScalarField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][4] if len(
                            attrs[k]) > 4 else 0,
                        attrs={"type": attrs[k][1], "units": "m"})
                else:
                    self._sc.checkXMLStringScalarField(
                        self._nxFile, k, 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][4] if len(
                            attrs[k]) > 4 else 0,
                        attrs={"type": attrs[k][1], "units": "m"})
            else:
                self._sc.checkXMLScalarField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(
                        attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None}
                )
        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_value_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None

            if attrs[k][2] == "string":
                mlen = [1, self.__rnd.randint(1, 3)]
                attrs[k][0] = [attrs[k][0] * self.__rnd.randint(1, 3)]
            elif attrs[k][2] != "bool":
                mlen = [1, self.__rnd.randint(0, 3)]
                attrs[k][0] = [attrs[k][0] * self.__rnd.randint(0, 3)]
            else:
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [bool(self.__rnd.randint(0, 1))]
                else:
                    attrs[k][0] = [
                        ("true" if self.__rnd.randint(0, 1) else "false")
                    ]

            attrs[k][3] = (mlen[0],)

            quin = (quin + 1) % 5
            stt = [None, 'INIT', 'STEP', 'POSTRUN', 'FINAL'][quin]

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": ""}, eFile)
            el[k].rank = "1"
            el[k].lengths = {"1": str(attrs[k][3][0])}
            el[k].grows = grow

            el[k].strategy = stt
            el[k].content.append(" ".join([str(a) for a in attrs[k][0]]))
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(
                el[k].content, [" ".join([str(a) for a in attrs[k][0]])])
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {"1": str(attrs[k][3][0])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].grows, None)

            if stt != 'POSTRUN':
                self._sc.checkXMLSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": ""})
            else:
                self._sc.checkXMLSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_value_1d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None

            if attrs[k][2] == "string":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 3)]
                attrs[k][0] = [
                    attrs[k][0] * self.__rnd.randint(1, 3)
                    for r in range(mlen[0])]
            elif attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for r in range(mlen[0])]
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

            quin = (quin + 1) % 5
            stt = [None, 'INIT', 'FINAL', 'STEP', 'POSTRUN'][quin]

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": ""}, eFile)
            el[k].rank = "1"
            el[k].lengths = {"1": str(attrs[k][3][0])}
            el[k].grows = grow

            el[k].strategy = stt
            el[k].content.append(" ".join([str(a) for a in attrs[k][0]]))
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(
                el[k].content, [" ".join([str(a) for a in attrs[k][0]])])
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {"1": str(attrs[k][3][0])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].grows, None)
            if stt != 'POSTRUN':
                self._sc.checkXMLSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][3] if len(attrs[k]) > 3 else 0,
                    attrs={"type": attrs[k][1], "units": ""})
            else:
                self._sc.checkXMLSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][3] if len(attrs[k]) > 3 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_value_2d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
# self._fname= '%s/%s_%s.h5' % (os.getcwd(), self.__class__.__name__, fun
# )
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        for k in attrs.keys():
            if attrs[k][2] == "string":
                mlen = [self.__rnd.randint(1, 10), 1, self.__rnd.randint(1, 3)]
                attrs[k][0] = [[
                    attrs[k][0] * self.__rnd.randint(1, 3)
                    for c in range(mlen[1])] for i in range(mlen[0])]
            elif attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [[
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for c in range(mlen[1])] for i in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] = [[
                        bool(self.__rnd.randint(0, 1))
                        for c in range(mlen[1])] for r in range(mlen[0])]
                else:
                    attrs[k][0] = [[
                        ("True" if self.__rnd.randint(0, 1) else "False")
                        for c in range(mlen[1])] for r in range(mlen[0])]

            attrs[k][3] = (mlen[0], mlen[1])

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None

            quin = (quin + 1) % 5
            stt = [None, 'INIT', 'STEP', 'POSTRUN', 'FINAL'][quin]

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": ""}, eFile)
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].grows = grow

            el[k].strategy = stt
            el[k].content.append(
                "".join(["".join([str(it) + " " for it in sub]) +
                         "\n" for sub in attrs[k][0]]))
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content,
                             ["".join(["".join([str(it) + " " for it in sub]) +
                                       "\n" for sub in attrs[k][0]])])
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(
                el[k].lengths, {"1": str(attrs[k][3][0]),
                                "2": str(attrs[k][3][1])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), None)
            if attrs[k][2] == 'string_old':
                self.assertEqual(el[k].grows, None)
                if stt != 'POSTRUN':
                    self._sc.checkXMLSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], [it[0] for it in attrs[k][0]],
                        attrs={
                            "type": attrs[k][1], "units": ""}
                    )
                else:
                    self._sc.checkXMLSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], [it[0] for it in attrs[k][0]],
                        attrs={
                            "type": attrs[k][1], "units": "", "postrun": None}
                    )

            elif stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkXMLImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": ""})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkXMLImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # default store method
    # \brief It tests default settings
    def test_store_value_2d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
# self._fname= '%s/%s_%s.h5' % (os.getcwd(), self.__class__.__name__, fun
# )
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        for k in attrs.keys():
            if attrs[k][2] == "string":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    2, 10), self.__rnd.randint(1, 3)]
                attrs[k][0] = [[
                    attrs[k][0] * self.__rnd.randint(1, 3)
                    for c in range(mlen[1])] for i in range(mlen[0])]
            elif attrs[k][2] != "bool":
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(
                    1, 10), self.__rnd.randint(0, 3)]
                attrs[k][0] = [[
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for c in range(mlen[1])] for i in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 10), self.__rnd.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] = [[
                        bool(self.__rnd.randint(0, 1))
                        for c in range(mlen[1])] for r in range(mlen[0])]
                else:
                    attrs[k][0] = [[
                        ("True" if self.__rnd.randint(0, 1) else "False")
                        for c in range(mlen[1])] for r in range(mlen[0])]

            attrs[k][3] = (mlen[0], mlen[1])

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None

            quin = (quin + 1) % 5
            stt = [None, 'INIT', 'FINAL', 'STEP', 'POSTRUN'][quin]

            el[k] = EField(
                {"name": k, "type": attrs[k][1], "units": ""}, eFile)
            el[k].rank = "2"
            el[k].lengths = {
                "1": str(attrs[k][3][0]), "2": str(attrs[k][3][1])}
            el[k].grows = grow

            el[k].strategy = stt
            el[k].content.append(
                "".join(["".join([str(it) + " " for it in sub]) +
                         "\n" for sub in attrs[k][0]]))
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content,
                             ["".join(
                                 ["".join([str(it) + " " for it in sub]) +
                                  "\n" for sub in attrs[k][0]])])
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(
                el[k].lengths, {"1": str(attrs[k][3][0]),
                                "2": str(attrs[k][3][1])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), None)
            if attrs[k][2] == 'string_old':
                self.assertEqual(el[k].grows, None)
#                self.assertEqual(el[k].grows, 1 if stt == 'STEP' else None)
                self._sc.checkXMLStringImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs={
                        "type": attrs[k][1], "units": ""}
                )
            elif stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkXMLImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": ""})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkXMLImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noData(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EField({"name": "myfield", "units": "m"}, eFile)
        ds = TstDataSource()
        el.source = ds

        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 2)
        self.assertEqual(el.shuffle, True)

        self.assertEqual(el.error, None)
        ds.valid = True
        self.assertEqual(el.run(), None)
#            self.myAssertRaise(ValueError, el[k].store)
        self.assertEqual(
            el.error[0],
            'Data for unnamed object not found. DATASOURCE:Test DataSource')
        self.assertEqual(el.error[1], 'H5 Object not created')
        ds.valid = False
        self.assertEqual(el.run(), None)
#            self.myAssertRaise(ValueError, el[k].store)
        self.assertEqual(
            el.error[0],
            'Data for unnamed object not found. DATASOURCE:Test DataSource')
        self.assertEqual(el.error[1], 'Data without value')
        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_0d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "string2": ["My string", "NX_CHAR", ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-132, "NX_INT", "int64"],
            "int8": [13, "NX_INT8", "int8"],
            "int16": [-223, "NX_INT16", "int16"],
            "int32": [13235, "NX_INT32", "int32"],
            "int64": [-12425, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [65, "NX_UINT8", "uint8"],
            "uint16": [453, "NX_UINT16", "uint16"],
            "uint32": [12235, "NX_UINT32", "uint32"],
            "uint64": [14345, "NX_UINT64", "uint64"],
            "float": [-16.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-2.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-4.355e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-2.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[0], "value": attrs[k][0],
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"], "shape": [0, 0]}
            el[k].source = ds
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)
            self.assertEqual(el[k].error, None)

            el[k].store()
#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].run(), None)
            #            self.myAssertRaise(ValueError, el[k].store)
            if stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                if stt in ['STEP'] or (
                        attrs[k][2] and attrs[k][2] not in ['string']):
                    self._sc.checkSingleScalarField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][3] if len(attrs[k]) > 3 else 0,
                        attrs={"type": attrs[k][1], "units": "m"})
                else:
                    self._sc.checkSingleStringScalarField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][3] if len(attrs[k]) > 3 else 0,
                        attrs={"type": attrs[k][1], "units": "m"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleScalarField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][3] if len(attrs[k]) > 3 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None}
                )
            self.assertEqual(el[k].error, None)

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_0d_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["", "NX_CHAR", "string"],
            "string2": ["", "NX_CHAR", ""],
            "datetime": ["", "NX_DATE_TIME", "string"],
            "iso8601": ["", "ISO8601", "string"],
            "int": [numpy.iinfo(getattr(numpy, 'int64')).max, "NX_INT",
                    "int64"],
            "int8": [numpy.iinfo(getattr(numpy, 'int8')).max, "NX_INT8",
                     "int8"],
            "int16": [numpy.iinfo(getattr(numpy, 'int16')).max, "NX_INT16",
                      "int16"],
            "int32": [numpy.iinfo(getattr(numpy, 'int32')).max, "NX_INT32",
                      "int32"],
            "int64": [numpy.iinfo(getattr(numpy, 'int64')).max, "NX_INT64",
                      "int64"],
            "uint": [numpy.iinfo(getattr(numpy, 'uint64')).max, "NX_UINT",
                     "uint64"],
            #            "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT", "uint64"],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8"],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16"],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32"],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64"],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64"],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[0], "value": attrs[k][0],
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"], "shape": [0, 0]}
            el[k].source = ds
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)
            self.assertEqual(el[k].error, None)

            el[k].store()
#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].markFailed(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            if stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                if stt in ['STEP'] or (
                        attrs[k][2] and attrs[k][2] not in ['string']):
                    self._sc.checkSingleScalarField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][3] if len(attrs[k]) > 3 else 0,
                        attrs={"type": attrs[k][1], "units": "m",
                               "nexdatas_canfail": "FAILED"})
                else:
                    self._sc.checkSingleStringScalarField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][3] if len(attrs[k]) > 3 else 0,
                        attrs={"type": attrs[k][1], "units": "m",
                               "nexdatas_canfail": "FAILED"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleScalarField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][3] if len(attrs[k]) > 3 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None,
                        "nexdatas_canfail": "FAILED"}
                )
            self.assertEqual(el[k].error, None)

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_0d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string"],
            "string2": ["My string", "NX_CHAR", ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string"],
            "iso8601": ["12:34:34", "ISO8601", "string"],
            "int": [-132, "NX_INT", "int64"],
            "int8": [13, "NX_INT8", "int8"],
            "int16": [-223, "NX_INT16", "int16"],
            "int32": [13235, "NX_INT32", "int32"],
            "int64": [-12425, "NX_INT64", "int64"],
            "uint": [123, "NX_UINT", "uint64"],
            "uint8": [65, "NX_UINT8", "uint8"],
            "uint16": [453, "NX_UINT16", "uint16"],
            "uint32": [12235, "NX_UINT32", "uint32"],
            "uint64": [14345, "NX_UINT64", "uint64"],
            "float": [-16.345, "NX_FLOAT", "float64", 1.e-14],
            "number": [-2.345e+2, "NX_NUMBER", "float64", 1.e-14],
            "float32": [-4.355e-1, "NX_FLOAT32", "float32", 1.e-5],
            "float64": [-2.345, "NX_FLOAT64", "float64", 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool"],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 10

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            stt = 'STEP'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            if attrs[k][2] == "string":
                attrs[k][0] = [
                    attrs[k][0] * self.__rnd.randint(1, 3)
                    for r in range(steps)]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [
                    attrs[k][0] * self.__rnd.randint(0, 3)
                    for r in range(steps)]
            else:
                if k == 'bool':
                    attrs[k][0] = [bool(self.__rnd.randint(0, 1))
                                   for c in range(steps)]
                else:
                    attrs[k][0] = [("true" if self.__rnd.randint(0, 1)
                                    else "false")
                                   for c in range(steps)]

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[0], "value": attrs[k][0][0],
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [0, 0]}
            # print k
            # print ds.value
            el[k].source = ds
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()
#            self.assertEqual(el[k].store(), None)
            for i in range(steps):
                ds.value = {"rank": NTP.rTf[0], "value": attrs[k][0][i],
                            "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                                  else "string"],
                            "shape": [0, 0]}
                self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)
#            self.assertEqual(el[k].grows, (grow if grow and grow else 1))
            self._sc.checkScalarField(
                self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                attrs[k][1], attrs[k][0],
                attrs[k][3] if len(attrs[k]) > 3 else 0,
                attrs={
                    "type": attrs[k][1], "units": "m"}
            )

            self.assertEqual(el[k].error, None)

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_0d_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["My string", "NX_CHAR", "string", ""],
            "string2": ["My string", "NX_CHAR", "", ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", ""],
            "iso8601": ["12:34:34", "ISO8601", "string", ""],
            "int": [-132, "NX_INT", "int64",
                    numpy.iinfo(getattr(numpy, 'int64')).max],
            "int8": [13, "NX_INT8", "int8",
                     numpy.iinfo(getattr(numpy, 'int8')).max],
            "int16": [-223, "NX_INT16", "int16",
                      numpy.iinfo(getattr(numpy, 'int16')).max],
            "int32": [13235, "NX_INT32", "int32",
                      numpy.iinfo(getattr(numpy, 'int32')).max],
            "int64": [-12425, "NX_INT64", "int64",
                      numpy.iinfo(getattr(numpy, 'int64')).max],
            "uint": [123, "NX_UINT", "uint64",
                     numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint":[123,"NX_UINT", "uint64",
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint8": [65, "NX_UINT8", "uint8",
                      numpy.iinfo(getattr(numpy, 'uint8')).max],
            "uint16": [453, "NX_UINT16", "uint16",
                       numpy.iinfo(getattr(numpy, 'uint16')).max],
            "uint32": [12235, "NX_UINT32", "uint32",
                       numpy.iinfo(getattr(numpy, 'uint32')).max],
            "uint64": [14345, "NX_UINT64", "uint64",
                       numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint64":[14345,"NX_UINT64",
            # "uint64",numpy.iinfo(getattr(numpy, 'uint64')).max],
            "float": [-16.345, "NX_FLOAT", "float64",
                      numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "number": [-2.345e+2, "NX_NUMBER", "float64",
                       numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "float32": [-4.355e-1, "NX_FLOAT32", "float32",
                        numpy.finfo(getattr(numpy, 'float32')).max, 1.e-5],
            "float64": [-2.345, "NX_FLOAT64", "float64",
                        numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", False],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 10

        for k in attrs:
            quot = (quot + 1) % 4
            grow = 1
            quin = (quin + 1) % 5

            stt = 'STEP'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            if attrs[k][2] == "string":
                attrs[k][0] = [(attrs[k][0] if r % 2 else attrs[k][3])
                               for r in range(steps)]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [(attrs[k][0] if r % 2 else attrs[k][3])
                               for r in range(steps)]
            else:
                attrs[k][0] = [(attrs[k][0] if r % 2 else attrs[k][3])
                               for r in range(steps)]

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[0], "value": attrs[k][0][0],
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"], "shape": [0, 0]}
            el[k].source = ds
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()
#            self.assertEqual(el[k].store(), None)
            for i in range(steps):
                ds.value = {"rank": NTP.rTf[0], "value": attrs[k][0][i],
                            "tangoDType": NTP.pTt[
                                (attrs[k][2]) if attrs[k][2]
                                else "string"], "shape": [0, 0]}
                if i % 2:
                    self.assertEqual(el[k].run(), None)
                else:
                    self.assertEqual(
                        el[k].h5Object.grow(
                            grow - 1 if grow and grow > 0 else 0), None)
                    self.assertEqual(el[k].markFailed(), None)

            self._sc.checkScalarField(
                self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                attrs[k][1], attrs[k][0],
                attrs[k][4] if len(attrs[k]) > 4 else 0,
                attrs={
                    "type": attrs[k][1], "units": "m",
                    "nexdatas_canfail": "FAILED"}
            )

            self.assertEqual(el[k].error, None)

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        supp = ["string", "datetime", "iso8601"]

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            if attrs[k][2] == "string":
                mlen = [1, self.__rnd.randint(1, 3)]
                attrs[k][0] = [attrs[k][0] * self.__rnd.randint(1, 3)]
            elif attrs[k][2] != "bool":
                mlen = [1, self.__rnd.randint(0, 3)]
                attrs[k][0] = [attrs[k][0] * self.__rnd.randint(0, 3)]
            else:
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [bool(self.__rnd.randint(0, 1))]
                else:
                    attrs[k][0] = [("true" if self.__rnd.randint(0, 1)
                                    else "false")
                                   ]

            attrs[k][3] = (mlen[0],)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[1],
                        "value": (attrs[k][0] if attrs[k][2] != "bool"
                                  else [Converters.toBool(attrs[k][0][0])]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], 0]}
            el[k].source = ds
            el[k].rank = "1"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)
            el[k].store()
#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            if PNIIO or k in supp:
                self.assertEqual(el[k].error, None)
                if stt != 'POSTRUN':
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][4] if len(attrs[k]) > 4 else 0,
                        attrs={"type": attrs[k][1], "units": "m"})
                else:
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][4] if len(attrs[k]) > 4 else 0,
                        attrs={
                            "type": attrs[k][1], "units": "m", "postrun": None}
                    )

            else:
                self.assertEqual(
                    el[k].error[0],
                    'Data for %s on Test DataSource not found' % k)

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_1d_single_markFailed(self):
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
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max, "NX_UINT8",
                      "uint8", (1,)],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16", (1,)],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32", (1,)],
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
            "float": [numpy.finfo(getattr(numpy, 'float64')).max,
                      "NX_FLOAT", "float64", (1,), 1.e-14],
            "number": [numpy.finfo(getattr(numpy, 'float64')).max,
                       "NX_NUMBER", "float64", (1,), 1.e-14],
            "float32": [numpy.finfo(getattr(numpy, 'float32')).max,
                        "NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64": [numpy.finfo(getattr(numpy, 'float64')).max,
                        "NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool": [False, "NX_BOOLEAN", "bool", (1,)],
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["false", "NX_BOOLEAN", "bool", (1,)]
        }

        supp = ["string", "datetime", "iso8601"]

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = None
            quin = (quin + 1) % 5

            if attrs[k][2] == "string":
                mlen = [1, self.__rnd.randint(1, 3)]
                attrs[k][0] = [attrs[k][0]]
            elif attrs[k][2] != "bool":
                mlen = [1, self.__rnd.randint(0, 3)]
                attrs[k][0] = [attrs[k][0]]
            else:
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [False]
                else:
                    attrs[k][0] = [("false")
                                   ]

            attrs[k][3] = (mlen[0],)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[1],
                        "value": (attrs[k][0] if attrs[k][2] != "bool"
                                  else [Converters.toBool(attrs[k][0][0])]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 0]}
            el[k].source = ds
            el[k].rank = "1"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()
#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].markFailed(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            if PNIIO or k in supp:
                self.assertEqual(el[k].error, None)
                if stt != 'POSTRUN':
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][4] if len(attrs[k]) > 4 else 0,
                        attrs={"type": attrs[k][1], "units": "m",
                               "nexdatas_canfail": "FAILED"})
                else:
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleSpectrumField(
                        self._nxFile, k, attrs[k][
                            2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][4] if len(attrs[k]) > 4 else 0,
                        attrs={
                            "type": attrs[k][1], "units": "m",
                            "postrun": None, "nexdatas_canfail": "FAILED"}
                    )

            else:
                self.assertEqual(
                    el[k].error[0],
                    'Data for %s on Test DataSource not found' % k)

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 10

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            stt = 'STEP'

            if attrs[k][2] != "bool":
                attrs[k][0] = [
                    [attrs[k][0] * self.__rnd.randint(0, 3)]
                    for r in range(steps)]
            else:
                if k == 'bool':
                    attrs[k][0] = [[bool(self.__rnd.randint(0, 1))]
                                   for r in range(steps)]
                else:
                    attrs[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                     else "false")]
                                   for r in range(steps)]

            attrs[k][3] = (1,)

            stt = 'STEP'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()

            ds.value = {"rank": NTP.rTf[1],
                        "value": (attrs[k][0][0] if attrs[k][2] != "bool"
                                  else [Converters.toBool(attrs[k][0][0][0])]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 0]}

            el[k].rank = "1"
            el[k].source = ds
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

            self.assertEqual(el[k].error, None)
            for i in range(steps):
                ds.value = {
                    "rank": NTP.rTf[1],
                    "value": (attrs[k][0][i] if attrs[k][2] != "bool"
                              else [Converters.toBool(attrs[k][0][i][0])]),
                    "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                          else "string"],
                    "shape": [attrs[k][3][0], 0]}
                self.assertEqual(el[k].run(), None)

            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old":
                val = [a[0] for a in attrs[k][0]]
                self._sc.checkSingleStringSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], val,
                    attrs={
                        "type": attrs[k][1], "units": "m"}
                )
            else:

                if grow and grow > 1:
                    val = [[a[0] for a in attrs[k][0]]]
                else:
                    val = attrs[k][0]
                self._sc.checkSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], val,
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m"}
                )

                # self._sc.checkSpectrumField(self._nxFile, k, attrs[k][2]
                # if attrs[k][2] else 'string',
                #   attrs[k][1], attrs[k][0],
                # attrs[k][3] if len(attrs[k])> 3 else 0,
                # attrs = {"type":attrs[k][1], "units":"m"}
                #  )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_1d_single_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,), ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,), ""],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,), ""],
            "int": [-123, "NX_INT", "int64", (1,),
                    numpy.iinfo(getattr(numpy, 'int64')).max],
            "int8": [12, "NX_INT8", "int8", (1,),
                     numpy.iinfo(getattr(numpy, 'int8')).max],
            "int16": [-123, "NX_INT16", "int16", (1,),
                      numpy.iinfo(getattr(numpy, 'int16')).max],
            "int32": [12345, "NX_INT32", "int32", (1,),
                      numpy.iinfo(getattr(numpy, 'int32')).max],
            "int64": [-12345, "NX_INT64", "int64", (1,),
                      numpy.iinfo(getattr(numpy, 'int64')).max],
            "uint": [123, "NX_UINT", "uint64", (1,),
                     numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint":[123,"NX_UINT", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint8": [12, "NX_UINT8", "uint8", (1,),
                      numpy.iinfo(getattr(numpy, 'uint8')).max],
            "uint16": [123, "NX_UINT16", "uint16", (1,),
                       numpy.iinfo(getattr(numpy, 'uint16')).max],
            "uint32": [12345, "NX_UINT32", "uint32", (1,),
                       numpy.iinfo(getattr(numpy, 'uint32')).max],
            "uint64": [12345, "NX_UINT64", "uint64", (1,),
                       numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint64":[12345,"NX_UINT64", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "float": [-12.345, "NX_FLOAT", "float64", (1,),
                      numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,),
                       numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,),
                        numpy.finfo(getattr(numpy, 'float32')).max, 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,),
                        numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,), False],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 10

        for k in attrs:
            quot = (quot + 1) % 4
            grow = self.__rnd.randint(0, 2) if attrs[k][2] != "string" else 1

            quin = (quin + 1) % 5

            stt = 'STEP'

            attrs[k][0] = [[(attrs[k][0] if r % 2 else attrs[k][4])]
                           for r in range(steps)]
            attrs[k][3] = (1,)

            stt = 'STEP'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()

            ds.value = {"rank": NTP.rTf[1],
                        "value": attrs[k][0][0],
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 0]}

            el[k].rank = "1"
            el[k].source = ds
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()
            self.assertEqual(el[k].error, None)
            for i in range(steps):
                ds.value = {"rank": NTP.rTf[1],
                            "value": (attrs[k][0][i] if attrs[k][2] != "bool"
                                      else [Converters.toBool(
                                            attrs[k][0][i][0])]),
                            "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                                  else "string"],
                            "shape": [attrs[k][3][0], 0]}
                if i % 2:
                    self.assertEqual(el[k].run(), None)
                else:
                    self.assertEqual(
                        el[k].h5Object.grow(grow - 1 if grow and grow > 0
                                            else 0), None)
                    self.assertEqual(el[k].markFailed(), None)

            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old":
                val = [a[0] for a in attrs[k][0]]
                self._sc.checkSingleStringSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], val,
                    attrs={
                        "type": attrs[k][1], "units": "m",
                        "nexdatas_canfail": "FAILED"}
                )
            else:

                if grow and grow > 1:
                    val = [[a[0] for a in attrs[k][0]]]
                else:
                    val = attrs[k][0]
                self._sc.checkSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], val,
                    attrs[k][5] if len(attrs[k]) > 5 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m",
                        "nexdatas_canfail": "FAILED"}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_1d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            if attrs[k][2] == "string":
                attrs[k][0] = [attrs[k][0] * self.__rnd.randint(1, 3)
                               for c in range(self.__rnd.randint(2, 10))]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [attrs[k][0] * self.__rnd.randint(0, 3)
                               for c in range(self.__rnd.randint(2, 10))]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [bool(self.__rnd.randint(0, 1))
                                   for c in range(self.__rnd.randint(2, 10))]
                else:
                    attrs[k][0] = [("true" if self.__rnd.randint(0, 1)
                                    else "false")
                                   for c in range(self.__rnd.randint(2, 10))]

            attrs[k][3] = (len(attrs[k][0]),)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[1],
                        "value": (attrs[k][0] if attrs[k][2] != "bool"
                                  else [Converters.toBool(c)
                                        for c in attrs[k][0]]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 0]}
            el[k].source = ds
            el[k].rank = "1"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()
            self.assertEqual(el[k].error, None)

#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)

            self.assertEqual(el[k].error, None)
            if stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_1d_reshape(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            if attrs[k][2] == "string":
                attrs[k][0] = [attrs[k][0] * self.__rnd.randint(1, 3)
                               for c in range(self.__rnd.randint(2, 10))]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [attrs[k][0] * self.__rnd.randint(0, 3)
                               for c in range(self.__rnd.randint(2, 10))]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [bool(self.__rnd.randint(0, 1))
                                   for c in range(self.__rnd.randint(2, 10))]
                else:
                    attrs[k][0] = [("true" if self.__rnd.randint(0, 1)
                                    else "false")
                                   for c in range(self.__rnd.randint(2, 10))]

            attrs[k][3] = (len(attrs[k][0]),)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            el[k].source = ds
            el[k].rank = "1"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()
            self.assertEqual(el[k].error, None)
            ds.value = {"rank": NTP.rTf[1],
                        "value": (attrs[k][0] if attrs[k][2] != "bool"
                                  else [Converters.toBool(c)
                                        for c in attrs[k][0]]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 0]}
#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)

            self.assertEqual(el[k].error, None)
            if stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_1d_markFailed(self):
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
            "bool2": ["FaLse", "NX_BOOLEAN", "bool", (1,)],
            "bool3": ["false", "NX_BOOLEAN", "bool", (1,)],
            "bool4": ["false", "NX_BOOLEAN", "bool", (1,)]
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = None
            quin = (quin + 1) % 5

            if attrs[k][2] == "string":
                attrs[k][0] = [attrs[k][0]
                               for c in range(self.__rnd.randint(2, 10))]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [attrs[k][0]
                               for c in range(self.__rnd.randint(2, 10))]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [
                        False for c in range(self.__rnd.randint(2, 10))]
                else:
                    attrs[k][0] = [("false")
                                   for c in range(self.__rnd.randint(2, 10))]

            attrs[k][3] = (len(attrs[k][0]),)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[1],
                        "value": (attrs[k][0] if attrs[k][2] != "bool"
                                  else [Converters.toBool(c)
                                        for c in attrs[k][0]]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 0]}
            el[k].source = ds
            el[k].rank = "1"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()
            self.assertEqual(el[k].error, None)

#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].markFailed(), None)
#            self.myAssertRaise(ValueError, el[k].store)

            self.assertEqual(el[k].error, None)
            if stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [attrs[k][0][0]],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleSpectrumField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [attrs[k][0][0]],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None,
                        "nexdatas_canfail": "FAILED"}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_1d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 13

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            stt = 'STEP'

            if attrs[k][2] == "string":
                mlen = self.__rnd.randint(2, 10)
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(1, 3)
                                for c in range(mlen)] for r in range(steps)]
            elif attrs[k][2] != "bool":
                mlen = self.__rnd.randint(2, 10)
#                print "ST",steps, mlen
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(0, 3)
                                for c in range(mlen)] for r in range(steps)]
            else:
                if k == 'bool':
                    mlen = self.__rnd.randint(2, 10)
                    attrs[k][0] = [[
                        bool(self.__rnd.randint(0, 1))
                        for c in range(mlen)] for r in range(steps)]
                else:
                    mlen = self.__rnd.randint(2, 10)
                    attrs[k][0] = [[
                        ("true" if self.__rnd.randint(0, 1) else "false")
                        for c in range(mlen)] for r in range(steps)]

            attrs[k][3] = (len(attrs[k][0][0]),)
#            sys.stdout.write("b.")k ,attrs[k][0][0]

            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[1],
                        "value": (attrs[k][0][0] if attrs[k][2] != "bool"
                                  else [Converters.toBool(c)
                                        for c in attrs[k][0][0]]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 0]}
            el[k].source = ds
            el[k].rank = "1"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

            for i in range(steps):
                ds.value = {
                    "rank": NTP.rTf[1],
                    "value": (attrs[k][0][i] if attrs[k][2] != "bool"
                              else [Converters.toBool(c)
                                    for c in attrs[k][0][i]]),
                    "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                          else "string"],
                    "shape": [attrs[k][3][0], 0]}
                self.assertEqual(el[k].run(), None)

            self.assertEqual(el[k].error, None)

#            self.assertEqual(el[k].store(), None)
#            self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)
#            print "nn", k
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkStringSpectrumField(
                    self._nxFile, k, 'string',
                    attrs[k][1], attrs[k][0],
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self._sc.checkSpectrumField(
                    self._nxFile, k, attrs[k][2],
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(
                        attrs[k]) > 4 else 0,
                    grows=grow,
                    attrs={"type": attrs[k][1], "units": "m"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_1d_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,), ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,), ""],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,), ""],
            "int": [-123, "NX_INT", "int64", (1,),
                    numpy.iinfo(getattr(numpy, 'int64')).max],
            "int8": [12, "NX_INT8", "int8", (1,),
                     numpy.iinfo(getattr(numpy, 'int8')).max],
            "int16": [-123, "NX_INT16", "int16", (1,),
                      numpy.iinfo(getattr(numpy, 'int16')).max],
            "int32": [12345, "NX_INT32", "int32", (1,),
                      numpy.iinfo(getattr(numpy, 'int32')).max],
            "int64": [-12345, "NX_INT64", "int64", (1,),
                      numpy.iinfo(getattr(numpy, 'int64')).max],
            "uint": [123, "NX_UINT", "uint64", (1,),
                     numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint":[123,"NX_UINT", "uint64", (1,),
            #  numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint8": [12, "NX_UINT8", "uint8", (1,),
                      numpy.iinfo(getattr(numpy, 'uint8')).max],
            "uint16": [123, "NX_UINT16", "uint16", (1,),
                       numpy.iinfo(getattr(numpy, 'uint16')).max],
            "uint32": [12345, "NX_UINT32", "uint32", (1,),
                       numpy.iinfo(getattr(numpy, 'uint32')).max],
            "uint64": [12345, "NX_UINT64", "uint64", (1,),
                       numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint64":[12345,"NX_UINT64", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "float": [-12.345, "NX_FLOAT", "float64", (1,),
                      numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,),
                       numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,),
                        numpy.finfo(getattr(numpy, 'float32')).max, 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,),
                        numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,), False],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 13

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5
            if attrs[k][2] == 'string':
                grow = 0

            stt = 'STEP'

            mlen = self.__rnd.randint(2, 10)
            attrs[k][0] = [[(attrs[k][0] if not r % 2 else attrs[k][4])
                            for c in range(mlen)] for r in range(steps)]

            attrs[k][3] = (len(attrs[k][0][0]),)

            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[1],
                        "value": (attrs[k][0][0]
                                  if attrs[k][2] != "bool"
                                  else [Converters.toBool(c)
                                        for c in attrs[k][0][0]]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], 0]}
            el[k].source = ds
            el[k].rank = "1"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

            for i in range(steps):
                ds.value = {
                    "rank": NTP.rTf[1],
                    "value": attrs[k][0][i],
                    "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                          else "string"],
                    "shape": [attrs[k][3][0], 0]}
                if not i % 2:
                    self.assertEqual(el[k].run(), None)
                else:
                    self.assertEqual(
                        el[k].h5Object.grow(grow - 1 if grow and grow > 0
                                            else 0), None)
                    self.assertEqual(el[k].markFailed(), None)

            self.assertEqual(el[k].error, None)
#            self.assertEqual(el[k].store(), None)
#            self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkStringSpectrumField(
                    self._nxFile, k, 'string',
                    attrs[k][1], attrs[k][0],
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})
            else:
                self._sc.checkSpectrumField(
                    self._nxFile, k, attrs[k][2],
                    attrs[k][1], attrs[k][0],
                    attrs[k][5] if len(attrs[k]) > 5 else 0,
                    grows=grow,
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_2d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        supp = ["string", "datetime", "iso8601"]

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            if attrs[k][2] == "string":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(1, 3)]]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(0, 3)]]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [[bool(self.__rnd.randint(0, 1))]]
                else:
                    attrs[k][0] = [[
                        ("true" if self.__rnd.randint(0, 1) else "false")
                    ]]

            attrs[k][3] = (1, 1)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {
                "rank": NTP.rTf[2],
                "value": (attrs[k][0] if attrs[k][2] != "bool"
                          else [[Converters.toBool(attrs[k][0][0][0])]]),
                "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                      else "string"],
                "shape": [1, 1]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)

            # print k, supp
            # print el[k].error
            if PNIIO or k in supp:
                self.assertEqual(el[k].error, None)

                if attrs[k][2] == "string_old" or not attrs[k][2]:
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleScalarField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0][0][0], 0,
                        attrs={"type": attrs[k][1], "units": "m"})

                elif stt != 'POSTRUN':
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleImageField(
                        self._nxFile, k, attrs[k][2] if attrs[k][2]
                        else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][4] if len(attrs[k]) > 4 else 0,
                        attrs={"type": attrs[k][1], "units": "m"})
                else:
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleImageField(
                        self._nxFile, k, attrs[k][2]
                        if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][4] if len(attrs[k]) > 4 else 0,
                        attrs={
                            "type": attrs[k][1], "units": "m",
                            "postrun": None}
                    )
            else:
                self.assertEqual(
                    el[k].error[0],
                    "Data for %s on Test DataSource not found" % k)

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_2d_single_markFailed(self):
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
            #            "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,
            # "NX_UINT64", "uint64", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
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

        supp = ["string", "datetime", "iso8601"]

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            attrs[k][0] = [[attrs[k][0]]]

            attrs[k][3] = (1, 1)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value":
                        (attrs[k][0] if attrs[k][2] != "bool"
                         else [[Converters.toBool(attrs[k][0][0][0])]]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [1, 1]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)
#            self.assertEqual(el[k].run(), None)
            self.assertEqual(el[k].markFailed(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            if PNIIO or k in supp:
                self.assertEqual(el[k].error, None)

                if attrs[k][2] == "string_old" or not attrs[k][2]:
                    self.assertEqual(el[k].grows, None)
                    if stt != 'POSTRUN':
                        self._sc.checkSingleScalarField(
                            self._nxFile, k,
                            attrs[k][2] if attrs[k][2] else 'string',
                            attrs[k][1], attrs[k][0][0][0], 0,
                            attrs={"type": attrs[k][1], "units": "m",
                                   "nexdatas_canfail": "FAILED"})
                    else:
                        self._sc.checkSingleScalarField(
                            self._nxFile, k,
                            attrs[k][2] if attrs[k][2] else 'string',
                            attrs[k][1], attrs[k][0][0][0], 0,
                            attrs={"type": attrs[k][1], "units": "m",
                                   "postrun": None,
                                   "nexdatas_canfail": "FAILED"})

                elif stt != 'POSTRUN':
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleImageField(
                        self._nxFile, k, attrs[k][2] if attrs[k][2]
                        else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][5] if len(attrs[k]) > 5 else 0,
                        attrs={"type": attrs[k][1], "units": "m",
                               "nexdatas_canfail": "FAILED"})
                else:
                    self.assertEqual(el[k].grows, None)
                    self._sc.checkSingleImageField(
                        self._nxFile, k, attrs[k][2]
                        if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs[k][5] if len(attrs[k]) > 5 else 0,
                        attrs={
                            "type": attrs[k][1], "units": "m",
                            "postrun": None, "nexdatas_canfail": "FAILED"}
                    )
            else:
                self.assertEqual(
                    el[k].error[0],
                    "Data for %s on Test DataSource not found" % k)

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_2d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 12

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            if attrs[k][2] == "string":
                attrs[k][0] = [
                    [[attrs[k][0] * self.__rnd.randint(1, 3)]]
                    for r in range(steps)]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [
                    [[attrs[k][0] * self.__rnd.randint(0, 3)]]
                    for r in range(steps)]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [[[bool(self.__rnd.randint(0, 1))]]
                                   for r in range(steps)]
                else:
                    attrs[k][0] = [[[("true" if self.__rnd.randint(0, 1)
                                      else "false")
                                     ]] for r in range(steps)]

            attrs[k][3] = (1, 1)

            stt = 'STEP'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0] if attrs[k][2] != "bool"
                                  else [[Converters.toBool(
                                         attrs[k][0][0][0][0])]]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [1, 1]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

            for i in range(steps):
                ds.value = {
                    "rank": NTP.rTf[2],
                    "value":
                    (attrs[k][0][i] if attrs[k][2] != "bool"
                     else [[Converters.toBool(attrs[k][0][i][0][0])]]),
                    "tangoDType":
                    NTP.pTt[(attrs[k][2]) if attrs[k][2] else "string"],
                    "shape": [attrs[k][3][0], 0]}
                self.assertEqual(el[k].run(), None)

            self.assertEqual(el[k].error, None)
#            self.assertEqual(el[k].store(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkScalarField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [c[0][0] for c in attrs[k][0]], 0,
                    attrs={"type": attrs[k][1], "units": "m"})

            else:
                self._sc.checkImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0, grow,
                    attrs={"type": attrs[k][1], "units": "m"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_2d_single_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,), ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,), ""],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,), ""],
            "int": [-123, "NX_INT", "int64", (1,),
                    numpy.iinfo(getattr(numpy, 'int64')).max],
            "int8": [12, "NX_INT8", "int8", (1,),
                     numpy.iinfo(getattr(numpy, 'int8')).max],
            "int16": [-123, "NX_INT16", "int16", (1,),
                      numpy.iinfo(getattr(numpy, 'int16')).max],
            "int32": [12345, "NX_INT32", "int32", (1,),
                      numpy.iinfo(getattr(numpy, 'int32')).max],
            "int64": [-12345, "NX_INT64", "int64", (1,),
                      numpy.iinfo(getattr(numpy, 'int64')).max],
            "uint": [123, "NX_UINT", "uint64", (1,),
                     numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint":[123,"NX_UINT", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint8": [12, "NX_UINT8", "uint8", (1,),
                      numpy.iinfo(getattr(numpy, 'uint8')).max],
            "uint16": [123, "NX_UINT16", "uint16", (1,),
                       numpy.iinfo(getattr(numpy, 'uint16')).max],
            "uint32": [12345, "NX_UINT32", "uint32", (1,),
                       numpy.iinfo(getattr(numpy, 'uint32')).max],
            #            "uint64":[12345,"NX_UINT64", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint64": [12345, "NX_UINT64", "uint64", (1,),
                       numpy.iinfo(getattr(numpy, 'uint64')).max],
            "float": [-12.345, "NX_FLOAT", "float64", (1,),
                      numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,),
                       numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,),
                        numpy.finfo(getattr(numpy, 'float32')).max, 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,),
                        numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,), False],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 12

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5
            if attrs[k][2] == 'string':
                grow = 1

            attrs[k][0] = [[[attrs[k][0] if r % 2 else attrs[k][4]]]
                           for r in range(steps)]
            attrs[k][3] = (1, 1)

            stt = 'STEP'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)

            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [1, 1]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

            for i in range(steps):
                ds.value = {"rank": NTP.rTf[2],
                            "value": (attrs[k][0][i] if attrs[k][2] != "bool"
                                      else [[Converters.toBool(
                                             attrs[k][0][i][0][0])]]),
                            "tangoDType": NTP.pTt[(attrs[k][2])
                                                  if attrs[k][2]
                                                  else "string"],
                            "shape": [attrs[k][3][0], 0]}
                if i % 2:
                    self.assertEqual(el[k].run(), None)
                else:
                    self.assertEqual(
                        el[k].h5Object.grow(grow - 1 if grow and grow > 0
                                            else 0), None)
                    self.assertEqual(el[k].markFailed(), None)

            self.assertEqual(el[k].error, None)
#            self.assertEqual(el[k].store(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkScalarField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [c[0][0] for c in attrs[k][0]], 0,
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})

            else:
                self._sc.checkImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][5] if len(attrs[k]) > 5 else 0, grow,
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_2d_double(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

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

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0] if attrs[k][2] != "bool"
                                  else [[Converters.toBool(c)
                                         for c in attrs[k][0][0]]]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [1, attrs[k][3][1]]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self.assertEqual(el[k].grows, None)
                if stt != 'POSTRUN':
                    self._sc.checkSingleStringImageField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs={"type": attrs[k][1], "units": "m"})
                else:
                    self._sc.checkSingleSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0][0], 0,
                        attrs={"type": attrs[k][1], "units": "m",
                               "postrun": None})

            elif stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_2d_double_markFailed(self):
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            quin = (quin + 1) % 5
            grow = None

            attrs[k][0] = [[attrs[k][0]
                            for c in range(self.__rnd.randint(2, 10))]]
            attrs[k][3] = (1, len(attrs[k][0][0]))

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [1, attrs[k][3][1]]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

            self.assertEqual(el[k].markFailed(), None)
            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self.assertEqual(el[k].grows, None)
                if stt != 'POSTRUN':
                    self._sc.checkSingleStringImageField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs={"type": attrs[k][1], "units": "m",
                               "nexdatas_canfail": "FAILED"})
                else:
                    self._sc.checkSingleStringImageField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs={"type": attrs[k][1], "units": "m",
                               "postrun": None, "nexdatas_canfail": "FAILED"})

            elif stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [[attrs[k][0][0][0]]],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [[attrs[k][0][0][0]]],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None,
                        "nexdatas_canfail": "FAILED"}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_2d_double(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 11

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            mlen = self.__rnd.randint(2, 10)
            if attrs[k][2] == "string_old":
                attrs[k][0] = [
                    [[attrs[k][0] * self.__rnd.randint(1, 3)
                      for c in range(mlen)]] for r in range(steps)]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [
                    [[attrs[k][0] * self.__rnd.randint(0, 3)
                      for c in range(mlen)]] for r in range(steps)]
            else:
                if k == 'bool':
                    attrs[k][0] = [
                        [
                            [
                                bool(self.__rnd.randint(0, 1))
                                for c in range(mlen)]]
                        for r in range(steps)
                    ]
                else:
                    attrs[k][0] = [
                        [
                            [("true" if self.__rnd.randint(0, 1) else "false")
                             for c in range(mlen)]]
                        for r in range(steps)
                    ]

            attrs[k][3] = (1, len(attrs[k][0][0][0]))

            stt = "STEP"
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0][0] if attrs[k][2] != "bool"
                                  else [[Converters.toBool(c)
                                         for c in attrs[k][0][0][0]]]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [1, attrs[k][3][1]]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)

            for i in range(steps):
                ds.value = {"rank": NTP.rTf[2],
                            "value": (attrs[k][0][i] if attrs[k][2] != "bool"
                                      else [[Converters.toBool(c)
                                             for c in attrs[k][0][i][0]]]),
                            "tangoDType": NTP.pTt[
                                (attrs[k][2])
                                if attrs[k][2] else "string"],
                            "shape": [1, attrs[k][3][1]]}
                self.assertEqual(el[k].run(), None)

            self.assertEqual(el[k].error, None)
#            self.myAssertRaise(ValueError, el[k].store)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkStringImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    # attrs[k][1], [[ row[0]  for
                    # row in img]for img in
                    # attrs[k][0]] ,
                    attrs[k][1], attrs[k][0],
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self._sc.checkImageField(self._nxFile, k, attrs[k][2],
                                         attrs[k][1], attrs[k][0],
                                         attrs[k][4] if len(
                    attrs[k]) > 4 else 0, grow,
                    attrs={"type": attrs[k][1], "units": "m"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_2d_double_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,), ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,), ""],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,), ""],
            "int": [-123, "NX_INT", "int64", (1,),
                    numpy.iinfo(getattr(numpy, 'int64')).max],
            "int8": [12, "NX_INT8", "int8", (1,),
                     numpy.iinfo(getattr(numpy, 'int8')).max],
            "int16": [-123, "NX_INT16", "int16", (1,),
                      numpy.iinfo(getattr(numpy, 'int16')).max],
            "int32": [12345, "NX_INT32", "int32", (1,),
                      numpy.iinfo(getattr(numpy, 'int32')).max],
            "int64": [-12345, "NX_INT64", "int64", (1,),
                      numpy.iinfo(getattr(numpy, 'int64')).max],
            #            "uint":[123,"NX_UINT", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint": [123, "NX_UINT", "uint64", (1,),
                     numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint8": [12, "NX_UINT8", "uint8", (1,),
                      numpy.iinfo(getattr(numpy, 'uint8')).max],
            "uint16": [123, "NX_UINT16", "uint16", (1,),
                       numpy.iinfo(getattr(numpy, 'uint16')).max],
            "uint32": [12345, "NX_UINT32", "uint32", (1,),
                       numpy.iinfo(getattr(numpy, 'uint32')).max],
            "uint64": [12345, "NX_UINT64", "uint64", (1,),
                       numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint64":[12345,"NX_UINT64", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "float": [-12.345, "NX_FLOAT", "float64", (1,), 1.e-14,
                      numpy.finfo(getattr(numpy, 'float64')).max],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,), 1.e-14,
                       numpy.finfo(getattr(numpy, 'float64')).max],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,), 1.e-5,
                        numpy.finfo(getattr(numpy, 'float32')).max],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,), 1.e-14,
                        numpy.finfo(getattr(numpy, 'float64')).max],
            "bool": [True, "NX_BOOLEAN", "bool", (1,), False],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 11

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5
            if attrs[k][2] == 'string':
                grow = 0

            mlen = self.__rnd.randint(2, 10)
            attrs[k][0] = [[[(attrs[k][0] if not r % 2 else attrs[k][4])
                             for c in range(mlen)]]
                           for r in range(steps)]
            attrs[k][3] = (1, len(attrs[k][0][0][0]))

            stt = "STEP"
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [1, attrs[k][3][1]]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)

            for i in range(steps):
                ds.value = {"rank": NTP.rTf[2],
                            "value": (attrs[k][0][i]),
                            "tangoDType": NTP.pTt[(attrs[k][2])
                                                  if attrs[k][2]
                                                  else "string"],
                            "shape": [1, attrs[k][3][1]]}
                if not i % 2:
                    self.assertEqual(el[k].run(), None)
                else:
                    self.assertEqual(
                        el[k].h5Object.grow(grow - 1
                                            if grow and grow > 0 else 0),
                        None)
                    self.assertEqual(el[k].markFailed(), None)

            self.assertEqual(el[k].error, None)
#            self.myAssertRaise(ValueError, el[k].store)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkStringImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1],
                    [[row for row in img]
                     for img in attrs[k][0]],
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})
            else:
                self._sc.checkImageField(self._nxFile, k, attrs[k][2],
                                         attrs[k][1], attrs[k][0],
                                         attrs[k][5] if len(
                    attrs[k]) > 5 else 0, grow,
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_2d_double_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            if attrs[k][2] == "string":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(1, 3)]
                               for c in range(self.__rnd.randint(2, 10))]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [[attrs[k][0] * self.__rnd.randint(0, 3)]
                               for c in range(self.__rnd.randint(2, 10))]
            else:
                # mlen = [1]
                if k == 'bool':
                    attrs[k][0] = [[bool(self.__rnd.randint(0, 1))]
                                   for c in range(self.__rnd.randint(2, 10))]
                else:
                    attrs[k][0] = [[("true" if self.__rnd.randint(0, 1)
                                     else "false")]
                                   for c in range(self.__rnd.randint(2, 10))]

            attrs[k][3] = (len(attrs[k][0]), 1)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (
                            attrs[k][0] if attrs[k][2] != "bool"
                            else [[Converters.toBool(c[0])]
                                  for c in attrs[k][0]]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], 1]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].run(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self.assertEqual(el[k].grows, None)
                if stt != 'POSTRUN':
                    self._sc.checkSingleSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], [c[0] for c in attrs[k][0]], 0,
                        attrs={"type": attrs[k][1], "units": "m"})
                else:
                    self._sc.checkSingleStringImageField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], [c[0] for c in attrs[k][0]],
                        attrs={"type": attrs[k][1], "units": "m",
                               "postrun": None})

            elif stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(
                        attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_2d_double_2_markFailed(self):
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
            #  "uint":[numpy.iinfo(getattr(numpy, 'uint64')).max,"NX_UINT",
            # "uint64", (1,)],
            "uint8": [numpy.iinfo(getattr(numpy, 'uint8')).max,
                      "NX_UINT8", "uint8", (1,)],
            "uint16": [numpy.iinfo(getattr(numpy, 'uint16')).max,
                       "NX_UINT16", "uint16", (1,)],
            "uint32": [numpy.iinfo(getattr(numpy, 'uint32')).max,
                       "NX_UINT32", "uint32", (1,)],
            "uint64": [numpy.iinfo(getattr(numpy, 'uint64')).max,
                       "NX_UINT64", "uint64", (1,)],
            # "uint64":[numpy.iinfo(getattr(numpy, 'uint64')).max,"NX_UINT64",
            #      "uint64", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = None
            quin = (quin + 1) % 5

            attrs[k][0] = [[attrs[k][0]]
                           for c in range(self.__rnd.randint(2, 10))]
            attrs[k][3] = (len(attrs[k][0]), 1)

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], 1]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].markFailed(), None)
#            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self.assertEqual(el[k].grows, None)
                if stt != 'POSTRUN':
                    self._sc.checkSingleSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], [c[0] for c in attrs[k][0]], 0,
                        attrs={"type": attrs[k][1], "units": "m",
                               "nexdatas_canfail": "FAILED"})
                else:
                    self._sc.checkSingleSpectrumField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], [c[0] for c in attrs[k][0]], 0,
                        attrs={"type": attrs[k][1], "units": "m",
                               "postrun": None, "nexdatas_canfail": "FAILED"})

            elif stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [[attrs[k][0][0][0]]],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [[attrs[k][0][0][0]]],
                    attrs[k][4] if len(
                        attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m",
                        "postrun": None, "nexdatas_canfail": "FAILED"}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_2d_double_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 11

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            mlen = self.__rnd.randint(2, 10)
            if attrs[k][2] == "string":
                attrs[k][0] = [[[attrs[k][0] * self.__rnd.randint(1, 3)]
                                for c in range(mlen)] for r in range(steps)]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [
                    [[attrs[k][0] * self.__rnd.randint(0, 3)]
                     for c in range(mlen)] for r in range(steps)]
            else:
                if k == 'bool':
                    attrs[k][0] = [
                        [[bool(self.__rnd.randint(0, 1))]
                         for c in range(mlen)] for r in range(steps)
                    ]
                else:
                    attrs[k][0] = [
                        [[("true" if self.__rnd.randint(0, 1) else "false")]
                         for c in range(mlen)] for r in range(steps)
                    ]

            attrs[k][3] = (len(attrs[k][0][0]), 1)

            stt = "STEP"
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nnn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0][0] if attrs[k][2] != "bool"
                                  else [[Converters.toBool(c[0])]
                                        for c in attrs[k][0][0]]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], 1]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)

            for i in range(steps):
                ds.value = {"rank": NTP.rTf[2],
                            "value": (attrs[k][0][i] if attrs[k][2] != "bool"
                                      else [[Converters.toBool(c[0])]
                                            for c in attrs[k][0][i]]),
                            "tangoDType": NTP.pTt[(attrs[k][2])
                                                  if attrs[k][2]
                                                  else "string"],
                            "shape": [attrs[k][3][0], 1]}
                self.assertEqual(el[k].run(), None)

#            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old" or not attrs[k][2]:

                self._sc.checkStringImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self._sc.checkImageField(
                    self._nxFile, k, attrs[k][2],
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0, grow,
                    attrs={"type": attrs[k][1], "units": "m"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_2d_double_2_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,), ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,), ""],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,), ""],
            "int": [-123, "NX_INT", "int64", (1,),
                    numpy.iinfo(getattr(numpy, 'int64')).max],
            "int8": [12, "NX_INT8", "int8", (1,),
                     numpy.iinfo(getattr(numpy, 'int8')).max],
            "int16": [-123, "NX_INT16", "int16", (1,),
                      numpy.iinfo(getattr(numpy, 'int16')).max],
            "int32": [12345, "NX_INT32", "int32", (1,),
                      numpy.iinfo(getattr(numpy, 'int32')).max],
            "int64": [-12345, "NX_INT64", "int64", (1,),
                      numpy.iinfo(getattr(numpy, 'int64')).max],
            "uint": [123, "NX_UINT", "uint64", (1,),
                     numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint":[123,"NX_UINT", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint8": [12, "NX_UINT8", "uint8", (1,),
                      numpy.iinfo(getattr(numpy, 'uint8')).max],
            "uint16": [123, "NX_UINT16", "uint16", (1,),
                       numpy.iinfo(getattr(numpy, 'uint16')).max],
            "uint32": [12345, "NX_UINT32", "uint32", (1,),
                       numpy.iinfo(getattr(numpy, 'uint32')).max],
            "uint64": [12345, "NX_UINT64", "uint64", (1,),
                       numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint64":[12345,"NX_UINT64", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "float": [-12.345, "NX_FLOAT", "float64", (1,),
                      numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,),
                       numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,),
                        numpy.finfo(getattr(numpy, 'float32')).max, 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,),
                        numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,), False],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 11

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5
#            if attrs[k][2] == 'string':
#                grow = 0

            mlen = self.__rnd.randint(2, 10)
            attrs[k][0] = [[[attrs[k][0] if not r % 2 else attrs[k][4]]
                            for c in range(mlen)] for r in range(steps)]
            attrs[k][3] = (len(attrs[k][0][0]), 1)

            stt = "STEP"
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nnn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], 1]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)

            for i in range(steps):
                ds.value = {"rank": NTP.rTf[2],
                            "value": (attrs[k][0][i]),
                            "tangoDType": NTP.pTt[(attrs[k][2])
                                                  if attrs[k][2]
                                                  else "string"],
                            "shape": [attrs[k][3][0], 1]}
                if not i % 2:
                    self.assertEqual(el[k].run(), None)
                else:
                    self.assertEqual(
                        el[k].h5Object.grow(
                            grow - 1 if grow and grow > 0 else 0), None)
                    self.assertEqual(el[k].markFailed(), None)

#            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkStringImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [[row for row in img]
                                  for img in attrs[k][0]],
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})
            else:
                self._sc.checkImageField(
                    self._nxFile, k, attrs[k][2],
                    attrs[k][1], attrs[k][0],
                    attrs[k][5] if len(attrs[k]) > 5 else 0, grow,
                    attrs={"type": attrs[k][1], "units": "m",
                           "nexdatas_canfail": "FAILED"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_2d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

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

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0] if attrs[k][2] != "bool"
                                  else [[Converters.toBool(c) for c in row]
                                        for row in attrs[k][0]]),
                        "tangoDType": NTP.pTt[(attrs[k][2]) if attrs[k][2]
                                              else "string"],
                        "shape": [attrs[k][3][0], attrs[k][3][1]]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].run(), None)
            self.assertEqual(el[k].error, None)
#            self.myAssertRaise(ValueError, el[k].store)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self.assertEqual(el[k].grows, None)
                if stt != 'POSTRUN':
                    self._sc.checkSingleStringImageField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs={"type": attrs[k][1], "units": "m"})
                else:
                    self._sc.checkSingleStringImageField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs={"type": attrs[k][1], "units": "m",
                               "postrun": None})

            elif stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m", "postrun": None}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_noX_2d_markFailed(self):
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0

        for k in attrs:
            quot = (quot + 1) % 4
            grow = None
            quin = (quin + 1) % 5

            mlen = self.__rnd.randint(2, 10)

            attrs[k][0] = [[attrs[k][0]
                            for c in range(mlen)]
                           for c2 in range(self.__rnd.randint(2, 10))]
            attrs[k][3] = (len(attrs[k][0]), len(attrs[k][0][0]))

            stt = [None, 'INIT', 'FINAL', 'POSTRUN'][quot]
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], attrs[k][3][1]]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

#            self.assertEqual(el[k].store(), None)
            self.assertEqual(el[k].markFailed(), None)
            self.assertEqual(el[k].error, None)
#            self.myAssertRaise(ValueError, el[k].store)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self.assertEqual(el[k].grows, None)
                if stt != 'POSTRUN':
                    self._sc.checkSingleStringImageField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs={"type": attrs[k][1], "units": "m",
                               "nexdatas_canfail": "FAILED"})
                else:
                    self._sc.checkSingleStringImageField(
                        self._nxFile, k,
                        attrs[k][2] if attrs[k][2] else 'string',
                        attrs[k][1], attrs[k][0],
                        attrs={"type": attrs[k][1], "units": "m",
                               "postrun": None, "nexdatas_canfail": "FAILED"})

            elif stt != 'POSTRUN':
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [[attrs[k][0][0][0]]],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={"type": attrs[k][1],
                           "units": "m", "nexdatas_canfail": "FAILED"})
            else:
                self.assertEqual(el[k].grows, None)
                self._sc.checkSingleImageField(
                    self._nxFile, k, attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], [[attrs[k][0][0][0]]],
                    attrs[k][4] if len(attrs[k]) > 4 else 0,
                    attrs={
                        "type": attrs[k][1], "units": "m",
                        "postrun": None, "nexdatas_canfail": "FAILED"}
                )

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_2d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,)],
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

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 11

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5

            mlen = [self.__rnd.randint(2, 10), self.__rnd.randint(2, 10)]
            if attrs[k][2] == "string":

                attrs[k][0] = [[[attrs[k][0] * self.__rnd.randint(1, 3)
                                 for c in range(mlen[0])]
                                for c2 in range(mlen[1])]
                               for r in range(steps)]
            elif attrs[k][2] != "bool":
                attrs[k][0] = [
                    [[attrs[k][0] * self.__rnd.randint(0, 3)
                      for c in range(mlen[0])] for c2 in range(mlen[1])]
                    for r in range(steps)]
            else:
                if k == 'bool':
                    attrs[k][0] = [[[bool(self.__rnd.randint(0, 1))
                                     for c in range(mlen[0])]
                                    for c2 in range(mlen[1])]
                                   for r in range(steps)]
                else:
                    attrs[k][0] = [[[("true" if self.__rnd.randint(0, 1)
                                      else "false")
                                     for c in range(mlen[0])]
                                    for c2 in range(mlen[1])]
                                   for r in range(steps)]

            attrs[k][3] = (len(attrs[k][0][0]), len(attrs[k][0][0][0]))

            stt = 'STEP'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {
                "rank": NTP.rTf[2],
                "value": (attrs[k][0][0]
                          if attrs[k][2] != "bool"
                          else [[Converters.toBool(c) for c in row]
                                for row in attrs[k][0][0]]),
                "tangoDType": NTP.pTt[(attrs[k][2])
                                      if attrs[k][2] else "string"],
                "shape": [attrs[k][3][0], attrs[k][3][1]]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

            for i in range(steps):
                ds.value = {
                    "rank": NTP.rTf[2],
                    "value": (attrs[k][0][i] if attrs[k][2] != "bool"
                              else [[Converters.toBool(c) for c in row]
                                    for row in attrs[k][0][i]]),
                    "tangoDType": NTP.pTt[(attrs[k][2])
                                          if attrs[k][2] else "string"],
                    "shape": [attrs[k][3][0], attrs[k][3][1]]}
                self.assertEqual(el[k].run(), None)

            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkStringImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs={"type": attrs[k][1], "units": "m"})
            else:
                self._sc.checkImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][4] if len(attrs[k]) > 4 else 0, grow,
                    attrs={"type": attrs[k][1], "units": "m"})

        self._nxFile.close()
        os.remove(self._fname)

    # run method tests
    # \brief It tests default settings
    def test_run_X_2d_markFailed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        attrs = {
            "string": ["Mystring", "NX_CHAR", "string", (1,), ""],
            "datetime": ["12:34:34", "NX_DATE_TIME", "string", (1,), ""],
            "iso8601": ["12:34:34", "ISO8601", "string", (1,), ""],
            "int": [-123, "NX_INT", "int64", (1,),
                    numpy.iinfo(getattr(numpy, 'int64')).max],
            "int8": [12, "NX_INT8", "int8", (1,),
                     numpy.iinfo(getattr(numpy, 'int8')).max],
            "int16": [-123, "NX_INT16", "int16", (1,),
                      numpy.iinfo(getattr(numpy, 'int16')).max],
            "int32": [12345, "NX_INT32", "int32", (1,),
                      numpy.iinfo(getattr(numpy, 'int32')).max],
            "int64": [-12345, "NX_INT64", "int64", (1,),
                      numpy.iinfo(getattr(numpy, 'int64')).max],
            "uint": [123, "NX_UINT", "uint64", (1,),
                     numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint":[123,"NX_UINT", "uint64", (1,),
            # numpy.iinfo(getattr(numpy, 'uint64')).max],
            "uint8": [12, "NX_UINT8", "uint8", (1,),
                      numpy.iinfo(getattr(numpy, 'uint8')).max],
            "uint16": [123, "NX_UINT16", "uint16", (1,),
                       numpy.iinfo(getattr(numpy, 'uint16')).max],
            "uint32": [12345, "NX_UINT32", "uint32", (1,),
                       numpy.iinfo(getattr(numpy, 'uint32')).max],
            "uint64": [12345, "NX_UINT64", "uint64", (1,),
                       numpy.iinfo(getattr(numpy, 'uint64')).max],
            #            "uint64":[12345,"NX_UINT64", "uint64",
            # (1,), numpy.iinfo(getattr(numpy, 'uint64')).max],
            "float": [-12.345, "NX_FLOAT", "float64", (1,),
                      numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "number": [-12.345e+2, "NX_NUMBER", "float64", (1,),
                       numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "float32": [-12.345e-1, "NX_FLOAT32", "float32", (1,),
                        numpy.finfo(getattr(numpy, 'float32')).max, 1.e-5],
            "float64": [-12.345, "NX_FLOAT64", "float64", (1,),
                        numpy.finfo(getattr(numpy, 'float64')).max, 1.e-14],
            "bool": [True, "NX_BOOLEAN", "bool", (1,), False],
        }

        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = {}
        quin = 0
        quot = 0
        steps = 11

        for k in attrs:
            quot = (quot + 1) % 4
            grow = quot - 1 if quot else None
            quin = (quin + 1) % 5
            if attrs[k][2] == 'string':
                grow = 0

            mlen = [self.__rnd.randint(2, 10), self.__rnd.randint(2, 10)]
            attrs[k][0] = [[[(attrs[k][0] if not r % 2
                              else attrs[k][4]) for c in range(mlen[0])]
                            for c2 in range(mlen[1])] for r in range(steps)]
            attrs[k][3] = (len(attrs[k][0][0]), len(attrs[k][0][0][0]))

            stt = 'STEP'
            if attrs[k][1]:
                el[k] = EField(
                    {"name": k, "type": attrs[k][1], "units": "m"}, eFile)
            else:
                el[k] = EField({"name": k, "units": "m"}, eFile)


#            print "nn",k
            el[k].strategy = stt
            ds = TstDataSource()
            ds.value = {"rank": NTP.rTf[2],
                        "value": (attrs[k][0][0]),
                        "tangoDType": NTP.pTt[(attrs[k][2])
                                              if attrs[k][2] else "string"],
                        "shape": [attrs[k][3][0], attrs[k][3][1]]}
            el[k].source = ds
            el[k].rank = "2"
            el[k].grows = grow

            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 2)
            self.assertEqual(el[k].shuffle, True)

            el[k].store()

            for i in range(steps):
                ds.value = {
                    "rank": NTP.rTf[2],
                    "value": (
                        attrs[k][0][i] if attrs[k][2] != "bool"
                        else [[Converters.toBool(c) for c in row]
                              for row in attrs[k][0][i]]),
                    "tangoDType": NTP.pTt[(attrs[k][2])
                                          if attrs[k][2] else "string"],
                    "shape": [attrs[k][3][0], attrs[k][3][1]]}
                if not i % 2:
                    self.assertEqual(el[k].run(), None)
                else:
                    self.assertEqual(
                        el[k].h5Object.grow(
                            grow - 1 if grow and grow > 0 else 0), None)
                    self.assertEqual(el[k].markFailed(), None)

            self.assertEqual(el[k].error, None)
            if attrs[k][2] == "string_old" or not attrs[k][2]:
                self._sc.checkStringImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs={"type": attrs[k][1],
                           "units": "m",
                           "nexdatas_canfail": "FAILED"})
            else:
                self._sc.checkImageField(
                    self._nxFile, k,
                    attrs[k][2] if attrs[k][2] else 'string',
                    attrs[k][1], attrs[k][0],
                    attrs[k][5] if len(attrs[k]) > 5 else 0, grow,
                    attrs={"type": attrs[k][1],
                           "units": "m",
                           "nexdatas_canfail": "FAILED"})

        self._nxFile.close()
        os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
