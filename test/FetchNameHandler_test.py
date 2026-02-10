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
# \file FetchNameHandlerTest.py
# unittests for field Tags running Tango Server
#
import unittest
import sys
import struct

from xml import sax

from nxswriter.FetchNameHandler import FetchNameHandler
from nxswriter.Errors import XMLSyntaxError
from nxswriter.FetchNameHandler import TNObject


def tobytes(x):
    """ decode str to  bytes
    :param x: string
    :type x: :obj:`str`
    :returns:  decode string in byte array
    :rtype: :obj:``bytes
    """
    if sys.version_info > (3,):
        return bytes(x, "utf-8")
    else:
        return bytes(x)


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class FetchNameHandlerTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name": "test", "units": "m"}

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

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

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        self.assertEqual(el.groupTypes.children, [])

    # constructor test
    # \brief It tests default settings
    def test_group_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el, sax.ContentHandler))
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        self.assertEqual(el.groupTypes.children, [])
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        self.assertEqual(len(el.groupTypes.children), 1)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["type"][2:])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_group_names(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "instrument", "type": "NXinstrument"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        self.assertEqual(el.groupTypes.children, [])
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("group", attr2), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["name"])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 1)
        ch = ch.child(name=attr2["name"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr2["name"])
        self.assertEqual(ch.nxtype, attr2["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_group_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "scan", "type": "NX_FLOAT"}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("field", attr2), None)
        self.assertEqual(el.endElement("field"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["name"])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_group_no_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"type": "NXentry"}
        # sattr1 = {attr1["type"]: "entry"}

        attr2 = {"name": "instrument1", "type": "NXinstrument"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("group", attr2), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["type"][2:])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 1)
        ch = ch.child(name=attr2["name"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr2["name"])
        self.assertEqual(ch.nxtype, attr2["type"])
        self.assertEqual(len(ch.children), 0)

#        self.assertEqual(el.groupTypes, dict(dict({"":""},**sattr1),**sattr2))

    # constructor test
    # \brief It tests default settings
    def test_group_name_only_types(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"type": "NXentry"}
        # sattr1 = {attr1["type"]: "entry"}

        attr2 = {"type": "NXinstrument", "units": "m"}
        # sattr2 = {attr2["type"]: "instrument"}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("group", attr2), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["type"][2:])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 1)
        ch = ch.child(nxtype=attr2["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr2["type"][2:])
        self.assertEqual(ch.nxtype, attr2["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_group_name_notype(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry"}
        # sattr1 = {"1": attr1["name"]}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.startElement("group", attr1), None)
        self.myAssertRaise(XMLSyntaxError, el.endElement, "group")
        self.assertTrue(isinstance(el.groupTypes, TNObject))

    # constructor test
    # \brief It tests default settings
    def test_attribute_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"type": "NXentry"}
        sattr1 = {attr1["type"]: "entry1"}

        attr2 = {"name": "name"}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("attribute", attr2), None)
        self.assertEqual(el.characters("entry1"), None)
        self.assertEqual(el.endElement("attribute"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, sattr1["NXentry"])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_attribute_type(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1"}
        # sattr1 = {"NXentry": "entry1"}

        attr2 = {"name": "type"}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("attribute", attr2), None)
        self.assertEqual(el.characters("NXentry"), None)
        self.assertEqual(el.endElement("attribute"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(name=attr1["name"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["name"])
        self.assertEqual(ch.nxtype, "NXentry")
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_attribute_name_type(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {}
        # sattr1 = {"NXentry": "entry1"}

        at1 = {"name": "name"}
        at2 = {"name": "type"}

        el = FetchNameHandler()
        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("attribute", at1), None)
        self.assertEqual(el.characters("entry1"), None)
        self.assertEqual(el.endElement("attribute"), None)

        self.assertEqual(el.startElement("attribute", at2), None)
        self.assertEqual(el.characters("NXentry"), None)
        self.assertEqual(el.endElement("attribute"), None)

        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype="NXentry")
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, "entry1")
        self.assertEqual(ch.nxtype, "NXentry")
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        sax.parseString(tobytes('<group type="%s" name="%s" />' %
                                (attr1["type"], attr1["name"])), el)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        self.assertEqual(len(el.groupTypes.children), 1)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["type"][2:])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_names(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "instrument", "type": "NXinstrument"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        sax.parseString(
            tobytes('<group type="%s" name="%s"><group type="%s" name="%s"/>'
                    '</group>'
                    % (attr1["type"], attr1["name"], attr2["type"],
                       attr2["name"])),
            el)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["name"])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 1)
        ch = ch.child(name=attr2["name"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr2["name"])
        self.assertEqual(ch.nxtype, attr2["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "scan", "type": "NX_FLOAT"}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        sax.parseString(
            tobytes('<group type="%s" name="%s"><field type="%s" name="%s"/>'
                    '</group>'
                    % (attr1["type"], attr1["name"], attr2["type"],
                       attr2["name"])),
            el)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["name"])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_no_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"type": "NXentry"}
        # sattr1 = {attr1["type"]: "entry"}

        attr2 = {"name": "instrument1", "type": "NXinstrument"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        sax.parseString(
            tobytes('<group type="%s" ><group type="%s" name="%s"/></group>'
                    % (attr1["type"], attr2["type"], attr2["name"])),
            el)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["type"][2:])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 1)
        ch = ch.child(name=attr2["name"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr2["name"])
        self.assertEqual(ch.nxtype, attr2["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_only_types(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"type": "NXentry"}
        # sattr1 = {attr1["type"]: "entry"}

        attr2 = {"type": "NXinstrument", "units": "m"}
        # sattr2 = {attr2["type"]: "instrument"}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        sax.parseString(
            tobytes('<group type="%s" ><group type="%s"/></group>'
                    % (attr1["type"], attr2["type"])), el)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["type"][2:])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 1)
        ch = ch.child(nxtype=attr2["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr2["type"][2:])
        self.assertEqual(ch.nxtype, attr2["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_notype(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry"}
        # sattr1 = {"1": attr1["name"]}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        self.myAssertRaise(
            XMLSyntaxError, sax.parseString,
            tobytes('<group name="%s" />' % (attr1["name"])), el)

        self.assertTrue(isinstance(el.groupTypes, TNObject))
        self.assertEqual(len(el.groupTypes.children), 1)
        ch = el.groupTypes.child(name="entry")
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, "entry")
        self.assertEqual(ch.nxtype, "")

    # constructor test
    # \brief It tests default settings
    def test_XML_attribute_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"type": "NXentry"}
        sattr1 = {attr1["type"]: "entry1"}

        # attr2 = {"name": "name"}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        sax.parseString(
            tobytes('<group type="%s" ><attribute name="name">'
                    'entry1</attribute></group>'
                    % (attr1["type"])), el)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype=attr1["type"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, sattr1["NXentry"])
        self.assertEqual(ch.nxtype, attr1["type"])
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_XML_attribute_type(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1"}
        # sattr1 = {"NXentry": "entry1"}

        # attr2 = {"name": "type"}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        sax.parseString(tobytes(
            '<group name="%s" ><attribute name="type">NXentry'
            '</attribute></group>'
            % (attr1["name"])), el)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(name=attr1["name"])
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, attr1["name"])
        self.assertEqual(ch.nxtype, "NXentry")
        self.assertEqual(len(ch.children), 0)

    # constructor test
    # \brief It tests default settings
    def test_XML_attribute_name_type(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        # attr1 = {}
        # sattr1 = {"NXentry": "entry1"}

        # at1 = {"name": "name"}
        # at2 = {"name": "type"}

        # parser = sax.make_parser()
        el = FetchNameHandler()
        sax.parseString(
            b'<group><attribute name="type">NXentry</attribute>'
            b'<attribute name="name">entry1</attribute></group>', el)

        self.assertEqual(el.groupTypes.name, "root")
        self.assertEqual(el.groupTypes.nxtype, None)
        ch = el.groupTypes.child(nxtype="NXentry")
        self.assertTrue(isinstance(ch, TNObject))
        self.assertEqual(ch.name, "entry1")
        self.assertEqual(ch.nxtype, "NXentry")
        self.assertEqual(len(ch.children), 0)


if __name__ == '__main__':
    unittest.main()
