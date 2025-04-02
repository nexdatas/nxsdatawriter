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
# \file ELinkTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct

# try:
#     from TstDataSource import TstDataSource
# except Exception:
#     from .TstDataSource import TstDataSource

try:
    from Checkers import Checker
except Exception:
    from .Checkers import Checker

from nxswriter.FElement import FElement
# from nxswriter.ELink import ELink
from nxswriter.EField import EField
from nxswriter.EVirtualField import EVirtualField, EVirtualDataMap
from nxswriter.H5Elements import EDim
from nxswriter.H5Elements import EDimensions
from nxswriter.EGroup import EGroup
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile
# from nxswriter.Errors import XMLSettingSyntaxError
# from nxswriter.FetchNameHandler import TNObject

from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter


# from  xml.sax import SAXParseException

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class EVirtualFieldH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._fname2 = "test2.h5"
        self._nxFile = None
        self._eFile = None

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"name": "testField", "units": "m", "type": "NX_INT"}
        self._gattrs = {"name": "testGroup", "type": "NXentry"}
        self._vattrs = {"name": "test_virtual_field", "type": "NX_INT"}
        self._dmattrs1 = {"rank": 1}
        self._diattrs1 = {"index": "1", "value": "1"}

        self._gname = "testGroup"
        self._gtype = "NXentry"
        self._fdname = "testField"
        self._fdtype = "int64"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self._sc = Checker(self)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        FileWriter.writer = H5PYWriter
        print("\nsetting up...")
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
        if not H5PYWriter.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        li = EVirtualField({}, eFile)
        self.assertTrue(isinstance(li, Element))
        self.assertTrue(isinstance(li, FElement))
        self.assertEqual(li.tagName, "vds")
        self.assertEqual(li.content, [])

        self.assertEqual(li.h5Object, None)
#        self.assertEqual(type(el.h5Object), None)
#        self.assertEqual(el.h5Object.name, self._gattrs["name"])
#        self.assertEqual(el.h5Object.nattrs, 1)
#        self.assertEqual(el.h5Object.attr("NX_class")[...],
# self._gattrs["type"])
#        self.assertEqual(el.h5Object.attr("NX_class").dtype, "string")
#        self.assertEqual(el.h5Object.attr("NX_class").shape, ())

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createVDS_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        if not H5PYWriter.is_vds_supported():
            print("Skip the test: VDS not supported")
            return
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()

        vf = EVirtualField(self._vattrs, gr)

        dm1 = EDimensions(self._dmattrs1, vf)
        di1 = EDim(self._diattrs1, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)

        vmattrs1 = {"name": "map1",
                    # "target": "/testField",
                    "target":
                    "EVirtualFieldH5PYTesttest_createVDS_default.h5:"
                    "/testField"
                    }
        vm1 = EVirtualDataMap(vmattrs1, vf)
        dm1 = EDimensions(self._dmattrs1, vm1)
        di1 = EDim(self._diattrs1, dm1)
        self.assertEqual(di1.store(""), None)
        self.assertEqual(dm1.store(""), None)
        self.assertEqual(vm1.store(""), None)
        self.assertEqual(vf.store(""), ('FINAL', None))
        self.assertEqual(vf.run(), None)

        rv = gr.h5Object.open("test_virtual_field")
        self.assertEqual(rv.read(), fi.h5Object.read())

        self._nxFile.close()
        #  os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
