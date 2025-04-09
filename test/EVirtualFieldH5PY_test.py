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
import struct

# try:
#     from TstDataSource import TstDataSource
# except Exception:
#     from .TstDataSource import TstDataSource


from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter


# from  xml.sax import SAXParseException

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


try:
    import EVirtualFieldH5Cpp_test
except Exception:
    from . import EVirtualFieldH5Cpp_test


# test fixture
class EVirtualFieldH5PYTest(EVirtualFieldH5Cpp_test.EVirtualFieldH5CppTest):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        EVirtualFieldH5Cpp_test.EVirtualFieldH5CppTest.__init__(
            self, methodName)
        #  unittest.TestCase.__init__(self, methodName)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        FileWriter.writer = H5PYWriter
        print("\nsetting up...")
        print("CHECKER SEED = %s" % self._sc.seed)


if __name__ == '__main__':
    unittest.main()
