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
# \file TNObjectTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time

from nxswriter.FetchNameHandler import TNObject


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class ElementTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        root = TNObject()
        self.assertEqual(root.name, 'root')
        self.assertEqual(root.nxtype, None)
        self.assertEqual(root.parent(), None)
        self.assertEqual(root.children, [])

        nn = self.__rnd.randint(1, 9)
        mname = "myname%s" % nn
        mtype = "NXtype%s" % nn
        el = TNObject(mname)
        self.assertEqual(el.name, mname)
        self.assertEqual(el.nxtype, None)
        self.assertEqual(el.parent(), None)
        self.assertEqual(el.children, [])

        nn = self.__rnd.randint(1, 9)
        mname = "mywname%s" % nn
        mtype = "NXwtype%s" % nn
        el = TNObject(mname, mtype)
        self.assertEqual(el.name, mname)
        self.assertEqual(el.nxtype, mtype)
        self.assertEqual(el.parent(), None)
        self.assertEqual(el.children, [])

        nn = self.__rnd.randint(1, 9)
        mname = "myename%s" % nn
        mtype = "NXetype%s" % nn
        self.assertEqual(root.children, [])
        el = TNObject(mname, mtype, root)
        self.assertEqual(root.children, [el])
        self.assertEqual(el.name, mname)
        self.assertEqual(el.nxtype, mtype)
        self.assertEqual(el.parent(), root)
        self.assertEqual(el.children, [])

        nn = self.__rnd.randint(1, 9)
        mname = "mysname%s" % nn
        mtype = "NXstype%s" % nn
        self.assertEqual(root.children, [el])
        el2 = TNObject(mname, mtype, root)
        self.assertEqual(root.children, [el, el2])
        self.assertEqual(el2.name, mname)
        self.assertEqual(el2.nxtype, mtype)
        self.assertEqual(el2.parent(), root)
        self.assertEqual(el2.children, [])

        nn = self.__rnd.randint(1, 9)
        mname = "mygname%s" % nn
        mtype = "NXgtype%s" % nn
        self.assertEqual(root.children, [el, el2])
        self.assertEqual(el2.children, [])
        el3 = TNObject(mname, mtype, el2)
        self.assertEqual(el2.children, [el3])
        self.assertEqual(root.children, [el, el2])
        self.assertEqual(el3.name, mname)
        self.assertEqual(el3.nxtype, mtype)
        self.assertEqual(el3.parent(), el2)
        self.assertEqual(el3.children, [])

    # constructor test
    # \brief It tests default settings
    def test_child(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        root = TNObject()
        self.assertEqual(root.name, 'root')
        self.assertEqual(root.nxtype, None)
        self.assertEqual(root.parent(), None)
        self.assertEqual(root.children, [])

        nn = self.__rnd.randint(1, 10)
        mname = "myaname%s" % nn
        mtype = "NXatype%s" % nn
        el = TNObject(mname)
        self.assertEqual(el.name, mname)
        self.assertEqual(el.nxtype, None)
        self.assertEqual(el.parent(), None)
        self.assertEqual(el.children, [])

        nn = self.__rnd.randint(1, 10)
        mname = "myname%s" % nn
        mtype = "NXtype%s" % nn
        self.assertEqual(root.children, [])
        el = TNObject(mname, mtype, root)
        self.assertEqual(root.children, [el])
        self.assertEqual(el.name, mname)
        self.assertEqual(el.nxtype, mtype)
        self.assertEqual(el.parent(), root)
        self.assertEqual(el.children, [])

        nn = self.__rnd.randint(1, 10)
        mname2 = "myename%s" % nn
        mtype2 = "NXetype%s" % nn
        self.assertEqual(root.children, [el])
        el2 = TNObject(mname2, mtype2, root)
        self.assertEqual(root.children, [el, el2])
        self.assertEqual(el2.name, mname2)
        self.assertEqual(el2.nxtype, mtype2)
        self.assertEqual(el2.parent(), root)
        self.assertEqual(el2.children, [])

        nn = self.__rnd.randint(1, 10)
        mname3 = "mywname%s" % nn
        mtype3 = "NXwtype%s" % nn
        self.assertEqual(root.children, [el, el2])
        self.assertEqual(el2.children, [])
        el3 = TNObject(mname3, mtype3, el2)
        self.assertEqual(el2.children, [el3])
        self.assertEqual(root.children, [el, el2])
        self.assertEqual(el3.name, mname3)
        self.assertEqual(el3.nxtype, mtype3)
        self.assertEqual(el3.parent(), el2)
        self.assertEqual(el3.children, [])

        ch = root.child()
        self.assertEqual(ch, el)
        ch = root.child(mname)
        self.assertEqual(ch, el)
        ch = root.child(mname2)
        self.assertEqual(ch, el2)
        ch = root.child(mname3)
        self.assertEqual(ch, None)

        ch = root.child(nxtype=mtype)
        self.assertEqual(ch, el)
        ch = root.child(nxtype=mtype2)
        self.assertEqual(ch, el2)
        ch = root.child(nxtype=mtype3)
        self.assertEqual(ch, None)

        ch = el2.child()
        self.assertEqual(ch, el3)
        ch = el2.child(mname3)
        self.assertEqual(ch, el3)
        ch = el2.child(mname2)
        self.assertEqual(ch, None)

        ch = el2.child(nxtype=mtype3)
        self.assertEqual(ch, el3)
        ch = el2.child(nxtype=mtype2)
        self.assertEqual(ch, None)

        ch = el3.child()
        self.assertEqual(ch, None)
        ch = el3.child(mname2)
        self.assertEqual(ch, None)

        ch = el3.child(nxtype=mtype2)
        self.assertEqual(ch, None)


if __name__ == '__main__':
    unittest.main()
