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
# \file EGroupTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import numpy
import binascii
import time


from nxswriter.FElement import FElementWithAttr
from nxswriter.FElement import FElement
from nxswriter.EGroup import EGroup
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile
from nxswriter.Types import NTP, Converters
from nxswriter.Errors import XMLSettingSyntaxError
from nxstools import filewriter as FileWriter
from nxstools import h5cppwriter as H5CppWriter

try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker

# from  xml.sax import SAXParseException

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class EGroupH5CppTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None

        self._gattrs = {"name": "test", "type": "NXentry"}
        self._gname = "testGroup"
        self._gtype = "NXentry"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

        self._sc = Checker(self)

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
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, self._gattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 1)
        self.assertEqual(el.h5Object.attributes[
                         "NX_class"][...], self._gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_default_constructor_reload(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, self._gattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 1)
        self.assertEqual(el.h5Object.attributes[
                         "NX_class"][...], self._gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        self.myAssertRaise(XMLSettingSyntaxError, EGroup, self._gattrs, eFile)
        el = EGroup(self._gattrs, eFile, reloadmode=True)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, self._gattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 1)
        self.assertEqual(el.h5Object.attributes[
                         "NX_class"][...], self._gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_default_constructor_thesame_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, self._gattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 1)
        self.assertEqual(el.h5Object.attributes[
                         "NX_class"][...], self._gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        self.myAssertRaise(XMLSettingSyntaxError, EGroup, self._gattrs, eFile)

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_constructor_noname(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        gattrs = {"type": "NXentry", "short_name": "shortname"}
        el = EGroup(gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, gattrs["type"][2:])
        self.assertEqual(len(el.h5Object.attributes), 2)
        self.assertEqual(el.h5Object.attributes[
                         "NX_class"][...], self._gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())
        self.assertEqual(el.h5Object.attributes[
                         "short_name"][...], gattrs["short_name"])
        self.assertEqual(el.h5Object.attributes["short_name"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["short_name"].shape, ())

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_constructor_noobject(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        gattrs = {"type": "NXentry", "short_name": "shortname"}
        self.myAssertRaise(XMLSettingSyntaxError, EGroup, gattrs, None)

    # default constructor test
    # \brief It tests default settings
    def test_constructor_notype(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)

        gattrs = {"short_name": "shortname"}
        self.myAssertRaise(XMLSettingSyntaxError, EGroup, gattrs, eFile)

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_constructor_aTn(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        gattrs = {"type": "NXentry", "name": "shortname"}
        # map of tag attribute types
        maTn = {"signal": 1, "axis": 2, "primary": 3, "offset": 4,
                "stride": 6, "file_time": "12:34",
                "file_update_time": "12:45", "restricts": 12,
                "ignoreExtraGroups": True, "ignoreExtraFields": False,
                "ignoreExtraAttributes": True, "minOccus": 1, "maxOccus": 2
                }
        gattrs = dict(gattrs, **(maTn))
        el = EGroup(gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, gattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 14)
        self.assertEqual(
            el.h5Object.attributes["NX_class"][...], gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        for k in maTn.keys():
            self.assertEqual(el.h5Object.attributes[k][...], gattrs[k])
            self.assertEqual(
                el.h5Object.attributes[k].dtype, NTP.nTnp[NTP.aTn[k]])
            self.assertEqual(el.h5Object.attributes[k].shape, ())

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_constructor_aTnv(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        gattrs = {"type": "NXentry", "name": "shortname"}
        # map of tag attribute types
        maTnv = {"vector": "1 2 3 4 5"}
        raTnv = {"vector": [1, 2, 3, 4, 5]}
        gattrs = dict(gattrs, **(maTnv))
        rattrs = dict(gattrs)
        rattrs = dict(rattrs, **(raTnv))
        error = 1.e-14

        el = EGroup(gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, gattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 2)
        self.assertEqual(
            el.h5Object.attributes["NX_class"][...], gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        for k in raTnv.keys():
            for i in range(len(rattrs[k])):
                self.assertTrue(
                    abs(el.h5Object.attributes[k][i] - rattrs[k][i]) <= error)
            self.assertEqual(
                el.h5Object.attributes[k].dtype, NTP.nTnp[NTP.aTnv[k]])
            self.assertEqual(
                el.h5Object.attributes[k].shape, (len(rattrs[k]),))

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
        el = EGroup(self._gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        el.store()
        self.assertEqual(el.h5Object.name, self._gattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 1)
        self.assertEqual(el.h5Object.attributes[
                         "NX_class"][...], self._gattrs["type"])
#        self.myAssertRaise(ValueError, el.store)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_0d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertEqual(el.tagAttributes, {})

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

        for nm in attrs.keys():
            el.tagAttributes[nm] = (attrs[nm][1], str(attrs[nm][0]))
            el.store()
            at = el.h5Attribute(nm)
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[nm][0])), at[...])

            elif len(attrs[nm]) > 3:
                self.assertTrue(abs(at[...] - attrs[nm][0]) <= attrs[nm][3])
            else:
                self.assertEqual(at[...], attrs[nm][0])

        for nm in attrs.keys():
            el.tagAttributes[nm] = (attrs[nm][1], str(attrs[nm][0]), [])
            el.store()
            at = el.h5Attribute(nm)
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[nm][0])), at[...])

            elif len(attrs[nm]) > 3:
                self.assertTrue(abs(at[...] - attrs[nm][0]) <= attrs[nm][3])
            else:
                self.assertEqual(at[...], attrs[nm][0])

        for nm in attrs.keys():
            if attrs[nm][2] == 'string':
                "writing multi-dimensional string is not supported by pninx"
                continue
            el.tagAttributes[nm] = (attrs[nm][1], str(attrs[nm][0]), [1])
            el.store()

            at = el.h5Object.attributes[nm]
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[nm][0])), at[...])

            elif len(attrs[nm]) > 3:
                self.assertTrue(abs(at[...] - attrs[nm][0]) <= attrs[nm][3])
            else:

                if isinstance(at[...], numpy.ndarray):
                    self.assertEqual(
                        at[...], numpy.array(attrs[nm][0], dtype=attrs[nm][2]))
                else:
                    self.assertEqual(at[...], attrs[nm][0])

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertEqual(el.tagAttributes, {})

        attrs = {
            #    "string":["My string","NX_CHAR", "string" , (1,)],
            #    "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            #    "iso8601":["12:34:34","ISO8601", "string", (1,)],
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

        for nm in attrs.keys():
            if attrs[nm][2] == 'string':
                "writing multi-dimensional string is not supported by pninx"
                continue
            el.tagAttributes[nm] = (
                attrs[nm][1], str(attrs[nm][0]), attrs[nm][3])
            el.store()
            at = el.h5Object.attributes[nm]
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[nm][0])), at[...])

            elif len(attrs[nm]) > 4:
                self.assertTrue(abs(at[...] - attrs[nm][0]) <= attrs[nm][4])
            else:

                if isinstance(at[...], numpy.ndarray):
                    self.assertEqual(
                        at[...], numpy.array(attrs[nm][0], dtype=attrs[nm][2]))
                else:
                    self.assertEqual(at[...], attrs[nm][0])

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_1d_single_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertEqual(el.tagAttributes, {})

        attrs = {
            #     "string":["My string","NX_CHAR", "string" , (1,)],
            #     "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            #     "iso8601":["12:34:34","ISO8601", "string", (1,)],
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

        for nm in attrs.keys():
            if attrs[nm][2] != "bool":
                mlen = [self.__rnd.randint(1, 1), self.__rnd.randint(0, 3)]
                attrs[nm][0] = [
                    attrs[nm][0] * self.__rnd.randint(0, 3)
                    for r in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 1)]
                if nm == 'bool':
                    attrs[nm][0] = [bool(self.__rnd.randint(0, 1))
                                    for c in range(mlen[0])]
                else:
                    attrs[nm][0] = [("true" if self.__rnd.randint(0, 1)
                                     else "false")
                                    for c in range(mlen[0])]

            attrs[nm][3] = (mlen[0],)

        for nm in attrs.keys():
            el.tagAttributes[nm] = (attrs[nm][1], "".join(
                [str(it) + " " for it in attrs[nm][0]]), attrs[nm][3])
            el.store()
            at = el.h5Object.attributes[nm]
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                for i in range(len(attrs[nm][0])):
                    self.assertEqual(
                        Converters.toBool(str(attrs[nm][0][i])), at[...])
                pass
            elif len(attrs[nm]) > 4:
                for i in range(len(attrs[nm][0])):
                    self.assertTrue(
                        abs(at[...] - attrs[nm][0][i]) <= attrs[nm][4])
            else:

                for i in range(len(attrs[nm][0])):
                    self.assertEqual(at[...], attrs[nm][0][i])

        self._nxFile.close()
        os.remove(self._fname)

        # constructor test
    # \brief It tests default settings
    def test_store_1d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertEqual(el.tagAttributes, {})

        attrs = {
            #  "string":["My string","NX_CHAR", "string" , (1,)],
            #  "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            #  "iso8601":["12:34:34","ISO8601", "string", (1,)],
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

        for nm in attrs.keys():
            if attrs[nm][2] != "bool":
                mlen = [self.__rnd.randint(2, 10), self.__rnd.randint(0, 3)]
                attrs[nm][0] = [
                    attrs[nm][0] * self.__rnd.randint(0, 3)
                    for r in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(2, 10)]
                if nm == 'bool':
                    attrs[nm][0] = [bool(self.__rnd.randint(0, 1))
                                    for c in range(mlen[0])]
                else:
                    attrs[nm][0] = [("true" if self.__rnd.randint(0, 1)
                                     else "false")
                                    for c in range(mlen[0])]

            attrs[nm][3] = (mlen[0],)

        for nm in attrs.keys():
            el.tagAttributes[nm] = (attrs[nm][1], "".join(
                [str(it) + " " for it in attrs[nm][0]]), attrs[nm][3])
            el.store()
            at = el.h5Object.attributes[nm]
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                for i in range(len(attrs[nm][0])):
                    self.assertEqual(
                        Converters.toBool(str(attrs[nm][0][i])), at[i])
                pass
            elif len(attrs[nm]) > 4:
                for i in range(len(attrs[nm][0])):
                    self.assertTrue(
                        abs(at[i] - attrs[nm][0][i]) <= attrs[nm][4])
            else:

                for i in range(len(attrs[nm][0])):
                    self.assertEqual(at[i], attrs[nm][0][i])

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_2d(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertEqual(el.tagAttributes, {})

        attrs = {
            #      "string":["My string","NX_CHAR", "string" , (1,)],
            #      "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            #      "iso8601":["12:34:34","ISO8601", "string", (1,)],
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

        for nm in attrs.keys():
            if attrs[nm][2] != "bool":
                mlen = [self.__rnd.randint(2, 10), self.__rnd.randint(2, 10),
                        (2 << numpy.dtype(attrs[nm][2]).itemsize)]
                #                print "SH",nm,mlen[2]
                attrs[nm][0] = [
                    [attrs[nm][0] * self.__rnd.randint(0, 3)
                     for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(2, 10), self.__rnd.randint(2, 10)]
                if nm == 'bool':
                    attrs[nm][0] = [[
                        bool(self.__rnd.randint(0, 1))
                        for c in range(mlen[1])] for r in range(mlen[0])]
                else:
                    attrs[nm][0] = [[
                        ("True" if self.__rnd.randint(0, 1) else "False")
                        for c in range(mlen[1])] for r in range(mlen[0])]

            attrs[nm][3] = (mlen[0], mlen[1])

        for nm in attrs.keys():
            el.tagAttributes[nm] = (
                attrs[nm][1],
                "".join(["".join([str(it) + " " for it in sub]) +
                         "\n" for sub in attrs[nm][0]]),
                attrs[nm][3]
            )
            el.store()
            at = el.h5Object.attributes[nm]
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertEqual(
                            Converters.toBool(
                                str(attrs[nm][0][i][j])), at[i, j])
                pass
            elif len(attrs[nm]) > 4:
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertTrue(
                            abs(at[i, j] - attrs[nm][0][i][j]) <= attrs[nm][4])
            else:
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertEqual(at[i, j], attrs[nm][0][i][j])

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_store_2d_single(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertEqual(el.tagAttributes, {})

        attrs = {
            #   "string":["My string","NX_CHAR", "string" , (1,)],
            #   "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            #   "iso8601":["12:34:34","ISO8601", "string", (1,)],
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

        for nm in attrs.keys():
            if attrs[nm][2] != "bool":
                mlen = [self.__rnd.randint(1, 1), self.__rnd.randint(1, 1),
                        (2 << numpy.dtype(attrs[nm][2]).itemsize)]
#                print "SH",nm,mlen[2]
                attrs[nm][0] = [
                    [attrs[nm][0] * self.__rnd.randint(0, 3)
                     for r in range(mlen[1])] for c in range(mlen[0])]
            else:
                mlen = [self.__rnd.randint(1, 1), self.__rnd.randint(1, 1)]
                if nm == 'bool':
                    attrs[nm][0] = [[
                        bool(self.__rnd.randint(0, 1))
                        for c in range(mlen[1])] for r in range(mlen[0])]
                else:
                    attrs[nm][0] = [[
                        ("True" if self.__rnd.randint(0, 1) else "False")
                        for c in range(mlen[1])] for r in range(mlen[0])]

            attrs[nm][3] = (mlen[0], mlen[1])

        for nm in attrs.keys():
            el.tagAttributes[nm] = (
                attrs[nm][1],
                "".join(["".join([str(it) + " " for it in sub]) +
                         "\n" for sub in attrs[nm][0]]),
                attrs[nm][3]
            )
            el.store()
            at = el.h5Object.attributes[nm]
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertEqual(
                            Converters.toBool(str(attrs[nm][0][i][j])),
                            at[...])
                pass
            elif len(attrs[nm]) > 4:
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertTrue(
                            abs(at[...] - attrs[nm][0][i][j]) <= attrs[nm][4])
            else:
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertEqual(at[...], attrs[nm][0][i][j])

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_fetchName_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        el = EGroup(self._gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, self._gattrs["name"])
        self.assertEqual(len(el.h5Object.attributes), 1)
        self.assertEqual(el.h5Object.attributes[
                         "NX_class"][...], self._gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        # gNames = {}
        self.assertEqual(el.store(), None)

        # gNames = {}

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_fetchName_noname(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        gattrs = {"type": "NXentry"}
        el = EGroup(gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, gattrs["type"][2:])
        self.assertEqual(len(el.h5Object.attributes), 1)
        self.assertEqual(
            el.h5Object.attributes["NX_class"][...], gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        # gNames = {}
        self.assertEqual(el.store(), None)

        # gNames = {}

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_fetchName_notype(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        FileWriter.writer = H5CppWriter
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        gattrs = {"type": "NXentry"}
        el = EGroup(gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), H5CppWriter.H5CppGroup)
        self.assertEqual(el.h5Object.name, gattrs["type"][2:])
        self.assertEqual(len(el.h5Object.attributes), 1)
        self.assertEqual(
            el.h5Object.attributes["NX_class"][...], gattrs["type"])
        self.assertEqual(el.h5Object.attributes["NX_class"].dtype, "string")
        self.assertEqual(el.h5Object.attributes["NX_class"].shape, ())

        # gNames = {}
        el._tagAttrs.pop("type")

        self._nxFile.close()
        os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
