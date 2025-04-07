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
# \file NexusXMLHandlerTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct
import json
from nxswriter.ThreadPool import ThreadPool
from nxswriter.Element import Element
from nxswriter.EGroup import EGroup
from nxswriter.EField import EField
from nxswriter.EAttribute import EAttribute
from nxswriter.ELink import ELink
from nxswriter.EStrategy import EStrategy
from nxswriter.FElement import FElement
from nxswriter.H5Elements import (
    EDoc, ESymbol, EDimensions, EDim, EFile, EFilter, ESlab, ESlice,
    ESelection)
from nxswriter.EVirtualField import (
    EVirtualField, EVirtualDataMap, EVirtualSourceView)
from nxswriter.DataSourceFactory import DataSourceFactory
from nxswriter.Errors import UnsupportedTagError
from nxswriter.FetchNameHandler import TNObject

from nxstools import filewriter as FileWriter
from nxstools import h5cppwriter as H5CppWriter


from xml import sax

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


from nxswriter.NexusXMLHandler import NexusXMLHandler


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


class Closeable(object):
    # consturctor

    def __init__(self):
        # close flag
        self.closed = False

    # close method
    def close(self):
        self.closed = True


class DataSourcePool(object):
    # consturctor

    def __init__(self):
        # close flag
        self.canfail = False


# test element
class TElement(FElement):
    # The last TElement instance
    instance = None
    # groupTypes

    groupTypes = TNObject()
    ch = TNObject("myentry1", "NXmyentry", groupTypes)
    # strategy
    strategy = None
    # trigger
    trigger = None

    # consturctor
    def __init__(self, attrs, last, streams=None, reloadmode=False):
        TElement.instance = self
        # costructor flag
        self.constructed = True
        # createLink flag
        self.linked = False
        # store flag
        self.stored = False
        # sax attributes
        self.attrs = attrs
        # tag content
        self.content = []
        # the last object
        self.last = last
        # groupTypes
        self.groupTypes = {}
        # strategy
        self.strategy = None
        # trigger
        self.trigger = None
        # run flag
        self.started = False
        # h5object
        self.h5Object = Closeable()
        self._streams = streams
        self.reloadmode = reloadmode

    @classmethod
    def getGroupTypes(self, tno, gt):
        if hasattr(tno, "__call__"):
            gt[tno().nxtype] = tno().name
            for ch in tno().children:
                self.getGroupTypes(ch, gt)
        else:
            gt[tno.nxtype] = tno.name
            for ch in tno.children:
                self.getGroupTypes(ch, gt)

    # creates links
    def createLink(self, groupTypes):
        self.linked = True
        self.groupTypes = {"": ""}
        self.getGroupTypes(groupTypes, self.groupTypes)

    # stores names
    def store(self):
        self.stored = True
        if TElement.trigger:
            self.strategy, self.trigger = TElement.strategy, TElement.trigger
            return TElement.strategy, TElement.trigger
        if TElement.strategy:
            self.strategy = TElement.strategy
            return TElement.strategy, None

    # run method
    def run(self):
        self.started = True


# test element
class SElement(FElement):
    # consturctor

    def __init__(self, attrs, last, streams=None):
        SElement.instance = self
        self.canfail = False
        self._streams = streams

    # run method
    def setCanFail(self):
        self.canfail = True


# test element
class InnerTag(object):
    # The last TElement instance
    instance = None
    # strategy
    strategy = None
    # trigger
    trigger = None

    # consturctor
    def __init__(self, attrs, last, streams=None):
        InnerTag.instance = self
        # costructor flag
        self.constructed = True
        # store flag
        self.stored = False
        # sax attributes
        self.attrs = attrs
        # tag content
        self.content = []
        # the last object
        self.last = last
        # strategy
        self.strategy = None
        # trigger
        self.trigger = None
        # h5object
        self.h5Object = Closeable()
        # xml string
        self.xml = None
        # json
        self.json = None
        self._streams = streams

    # stores names
    def store(self, xml, myjson):
        self.xml = xml
        self.json = myjson
        self.stored = True
        if InnerTag.trigger:
            self.strategy, self.trigger = InnerTag.strategy, InnerTag.trigger
            return InnerTag.strategy, InnerTag.trigger
        if InnerTag.strategy:
            self.strategy = InnerTag.strategy
            return InnerTag.strategy


# test element
class InnerTagDSDC(object):
    # The last TElement instance
    instance = None
    # strategy
    strategy = None
    # trigger
    trigger = None

    # consturctor
    def __init__(self, attrs, last, streams=None):
        InnerTagDSDC.instance = self
        # costructor flag
        self.constructed = True
        # store flag
        self.stored = False
        # sax attributes
        self.attrs = attrs
        # tag content
        self.content = []
        # the last object
        self.last = last
        # strategy
        self.strategy = None
        # trigger
        self.trigger = None
        # h5object
        self.h5Object = Closeable()
        # xml string
        self.xml = None
        # json
        self.json = None
        # datasources
        self.datasources = None
        # decoders
        self.decoders = None
        self._streams = streams

    # stores names
    def store(self, xml, myjson):
        self.xml = xml
        print("JSON %s" % self.json)
        self.json = myjson
        self.stored = True
        if InnerTagDC.trigger:
            self.strategy, self.trigger = (
                InnerTagDC.strategy, InnerTagDC.trigger)
            return InnerTagDC.strategy, InnerTagDC.trigger
        if InnerTagDC.strategy:
            self.strategy = InnerTagDC.strategy
            return InnerTagDC.strategy

    # sets the used datasources
    # \param datasources pool to be set
    def setDataSources(self, datasources):
        self.datasources = datasources

    # sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self.decoders = decoders


# test element
class InnerTagDS(object):
    # The last TElement instance
    instance = None
    # strategy
    strategy = None
    # trigger
    trigger = None

    # consturctor
    def __init__(self, attrs, last, streams=None):
        InnerTagDS.instance = self
        # costructor flag
        self.constructed = True
        # store flag
        self.stored = False
        # sax attributes
        self.attrs = attrs
        # tag content
        self.content = []
        # the last object
        self.last = last
        # strategy
        self.strategy = None
        # trigger
        self.trigger = None
        # h5object
        self.h5Object = Closeable()
        # xml string
        self.xml = None
        # json
        self.json = None
        # datasources
        self.datasources = None
        # decoders
        self.decoders = None
        self._streams = streams

    # stores names
    def store(self, xml, myjson):
        self.xml = xml
        print("JSON %s" % self.json)
        self.json = myjson
        self.stored = True
        if InnerTagDS.trigger:
            self.strategy, self.trigger = (
                InnerTagDS.strategy, InnerTagDS.trigger)
            return InnerTagDS.strategy, InnerTagDS.trigger
        if InnerTagDS.strategy:
            self.strategy = InnerTagDS.strategy
            return InnerTagDS.strategy

    # sets the used datasources
    # \param datasources pool to be set
    def setDataSources(self, datasources):
        self.datasources = datasources


# test element
class InnerTagDC(object):
    # The last TElement instance
    instance = None
    # strategy
    strategy = None
    # trigger
    trigger = None

    # consturctor
    def __init__(self, attrs, last, streams=None):
        InnerTagDC.instance = self
        # costructor flag
        self.constructed = True
        # store flag
        self.stored = False
        # sax attributes
        self.attrs = attrs
        # tag content
        self.content = []
        # the last object
        self.last = last
        # strategy
        self.strategy = None
        # trigger
        self.trigger = None
        # h5object
        self.h5Object = Closeable()
        # xml string
        self.xml = None
        # json
        self.json = None
        # datasources
        self.datasources = None
        # decoders
        self.decoders = None
        self._streams = streams

    # stores names
    def store(self, xml, myjson):
        self.xml = xml
        print("JSON %s" % self.json)
        self.json = myjson
        self.stored = True
        if InnerTagDC.trigger:
            self.strategy, self.trigger = (
                InnerTagDC.strategy, InnerTagDC.trigger)
            return InnerTagDC.strategy, InnerTagDC.trigger
        if InnerTagDC.strategy:
            self.strategy = InnerTagDC.strategy
            return InnerTagDC.strategy

    # sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self.decoders = decoders


# test element
class TElementOS(FElement):
    # The last TElement instance
    instance = None
    # groupTypes
    groupTypes = {"NXmyentry": "myentry1"}

    # consturctor
    def __init__(self, attrs, last, streams=None, reloadmode=False):
        TElementOS.instance = self
        # costructor flag
        self.constructed = True
        # fetchName flag
        self.fetched = False
        # createLink flag
        self.linked = False
        # store flag
        self.stored = False
        # sax attributes
        self.attrs = attrs
        # tag content
        self.content = []
        # the last object
        self.last = last
        # groupTypes
        self.groupTypes = {}
        # h5object
        self._streams = streams
        self.h5Object = Closeable()
        self.reloadmode = reloadmode

    # fetches names
    def fetchName(self, groupTypes):
        self.fetched = True
        for k in TElementOS.groupTypes:
            groupTypes[k] = TElementOS.groupTypes[k]

    # creates links
    def createLink(self, groupTypes):
        self.linked = True
        self.groupTypes = groupTypes


# test element
class TElementOL(object):
    # The last TElement instance
    instance = None
    # groupTypes
    groupTypes = {"NXmyentry": "myentry1"}

    # consturctor
    def __init__(self, attrs, last, streams=None, reloadmode=False):
        TElementOL.instance = self
        # costructor flag
        self.constructed = True
        # fetchName flag
        self.fetched = False
        # createLink flag
        self.linked = False
        # store flag
        self.stored = False
        # sax attributes
        self.attrs = attrs
        # tag content
        self.content = []
        # the last object
        self.last = last
        # groupTypes
        self.groupTypes = {}
        self._streams = streams
        self.reloadmode = reloadmode

    # fetches names
    def fetchName(self, groupTypes):
        self.fetched = True
        for k in TElementOL.groupTypes:
            groupTypes[k] = TElementOL.groupTypes[k]


# test element
class TElementOF(object):
    # The last TElement instance
    instance = None
    # groupTypes
    groupTypes = {"NXmyentry": "myentry1"}

    # consturctor
    def __init__(self, attrs, last, streams=None, reloadmode=False):
        TElementOF.instance = self
        # costructor flag
        self.constructed = True
        # fetchName flag
        self.fetched = False
        # createLink flag
        self.linked = False
        # store flag
        self.stored = False
        # sax attributes
        self.attrs = attrs
        # tag content
        self.content = []
        # the last object
        self.last = last
        # groupTypes
        self.groupTypes = {}
        self._streams = streams
        self.reloadmode = reloadmode


# test fixture
class NexusXMLHandlerH5CppTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
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

    # constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        nh = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(nh, sax.ContentHandler))
        self.assertTrue(isinstance(nh.initPool, ThreadPool))
        self.assertTrue(isinstance(nh.stepPool, ThreadPool))
        self.assertTrue(isinstance(nh.finalPool, ThreadPool))
        self.assertEqual(nh.triggerPools, {})
        self.assertEqual(
            nh.withXMLinput, {'datasource': DataSourceFactory, 'doc': EDoc})
        self.assertEqual(
            nh.elementClass, {
                'group': EGroup, 'field': EField,
                'attribute': EAttribute, 'link': ELink,
                'symbols': Element, 'symbol': ESymbol,
                'dimensions': EDimensions, 'dim': EDim,
                'enumeration': Element, 'item': Element,
                'strategy': EStrategy, 'filter': EFilter,
                'vds': EVirtualField, 'map': EVirtualDataMap,
                'sourceview': EVirtualSourceView,
                'slab': ESlab, 'slice': ESlice, 'selection': ESelection,
            })
        self.assertEqual(nh.transparentTags, ['definition'])
        self.assertEqual(nh.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry")
        self.assertEqual(len(en.attributes), 1)
        self.assertEqual(en.size, 0)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())
        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_XML_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)
        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry", "type": "NXentry", "shortname": "myentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}
        st = ''
        for a in attr1:
            st += ' %s ="%s"' % (a, attr1[a])
        xml = '<group%s/>' % (st)

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry")
        self.assertEqual(len(en.attributes), 2)
        self.assertEqual(en.size, 0)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        at = en.attributes["shortname"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "shortname")
        self.assertEqual(at[...], "myentry")

        self.assertEqual(el.close(), None)

        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "instrument", "type": "NXinstrument"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("group", attr2), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry1")
        self.assertEqual(len(en.attributes), 1)
        self.assertEqual(en.size, 1)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        ins = en.open(attr2["name"])
        self.assertTrue(ins.is_valid)
        self.assertEqual(ins.name, "instrument")
        self.assertEqual(len(ins.attributes), 1)
        self.assertEqual(ins.size, 0)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "instrument", "type": "NXinstrument", "signal": "1"}
        # sattr2 = {attr2["type"]: attr2["name"]}
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)

        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<group%s/>' % (st)
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry1")
        self.assertEqual(len(en.attributes), 1)
        self.assertEqual(en.size, 1)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        ins = en.open(attr2["name"])
        self.assertTrue(ins.is_valid)
        self.assertEqual(ins.name, "instrument")
        self.assertEqual(len(ins.attributes), 2)
        self.assertEqual(ins.size, 0)

        at = ins.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXinstrument")

        at = ins.attributes["signal"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "int64")
        self.assertEqual(at.name, "signal")
        self.assertEqual(at[...], 1)

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_XML_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "counter")
        self.assertEqual(len(en.attributes), 2)
        self.assertEqual(en.read(), value)
        self.assertTrue(hasattr(en.shape, "__iter__"))
        self.assertEqual(len(en.shape), 0)
        self.assertEqual(en.shape, ())

        at = en.attributes["type"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "type")
        self.assertEqual(at[...], "NX_CHAR")

        at = en.attributes["axis"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "int64")
        self.assertEqual(at.name, "axis")
        self.assertEqual(at[...], 1)

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "counter", "type": "NX_CHAR"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        self.assertEqual(el.startElement("field", attr1), None)
        self.assertEqual(el.characters("field"), None)
        self.assertEqual(el.endElement("field"), None)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "counter")
        self.assertEqual(len(en.attributes), 1)
        self.assertEqual(en.read(), "field")
        self.assertTrue(hasattr(en.shape, "__iter__"))
        self.assertEqual(len(en.shape), 0)
        self.assertEqual(en.shape, ())

        at = en.attributes["type"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "type")
        self.assertEqual(at[...], "NX_CHAR")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_field_empty(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "counter", "type": "NX_CHAR"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        self.assertEqual(el.startElement("field", attr1), None)
        self.assertEqual(el.characters(""), None)
        self.assertEqual(el.endElement("field"), None)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "counter")
        self.assertEqual(len(en.attributes), 1)
        self.assertEqual(en.read(), "")
        #        self.myAssertRaise(MemoryError, en.read)
        self.assertTrue(hasattr(en.shape, "__iter__"))
        self.assertEqual(len(en.shape), 0)
        self.assertEqual(en.shape, ())

        at = en.attributes["type"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "type")
        self.assertEqual(at[...], "NX_CHAR")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_XML_field_empty(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "counter", "type": "NX_CHAR"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = ''
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "counter")
        self.assertEqual(len(en.attributes), 1)
        self.assertEqual(en.read(), "")
#        self.myAssertRaise(MemoryError, en.read)
#        self.assertEqual(en.read(), "")
        self.assertTrue(hasattr(en.shape, "__iter__"))
        self.assertEqual(len(en.shape), 0)
        self.assertEqual(en.shape, ())

        at = en.attributes["type"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "type")
        self.assertEqual(at[...], "NX_CHAR")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_field_value_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "counter", "type": "NX_INT"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        self.assertEqual(el.startElement("field", attr1), None)
        self.assertEqual(el.characters(""), None)
        self.myAssertRaise(ValueError, el.endElement, "field")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_XML_field_value_error(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)

        attr1 = {"name": "counter", "type": "NX_INT"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = ''
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        self.myAssertRaise(ValueError, sax.parseString, xml, el)

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("field", attr2), None)
        self.assertEqual(el.characters("1234"), None)
        self.assertEqual(el.endElement("field"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry1")
        self.assertEqual(len(en.attributes), 1)
        self.assertEqual(en.size, 1)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        cnt = en.open(attr2["name"])
        self.assertTrue(cnt.is_valid)
        self.assertEqual(cnt.name, "counter")
        self.assertEqual(len(cnt.attributes), 1)
        self.assertEqual(cnt.read(), 1234)
        self.assertTrue(hasattr(cnt.shape, "__iter__"))
        self.assertEqual(len(cnt.shape), 1)
        self.assertEqual(cnt.shape[0], 1)

        at = cnt.attributes["type"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "type")
        self.assertEqual(at[...], "NX_INT")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry1")
        self.assertEqual(len(en.attributes), 1)
        self.assertEqual(en.size, 1)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        cnt = en.open(attr2["name"])
        self.assertTrue(cnt.is_valid)
        self.assertEqual(cnt.name, "counter")
        self.assertEqual(len(cnt.attributes), 1)
        self.assertEqual(cnt.read(), 1234)
        self.assertTrue(hasattr(cnt.shape, "__iter__"))
        self.assertEqual(len(cnt.shape), 1)
        self.assertEqual(cnt.shape[0], 1)

        at = cnt.attributes["type"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "type")
        self.assertEqual(at[...], "NX_INT")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_attribute(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT32"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<attribute%s>' % (st)
        xml += value
        xml += '</attribute>'
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry1")
        self.assertEqual(len(en.attributes), 2)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        at = en.attributes[attr2["name"]]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.name, "counter")
        self.assertEqual(at.dtype, "int32")
        self.assertEqual(at[...], 1234)

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_attribute(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT32"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("attribute", attr2), None)
        self.assertEqual(el.characters("1234"), None)
        self.assertEqual(el.endElement("attribute"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry1")
        self.assertEqual(len(en.attributes), 2)

        at = en.attributes["NX_class"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "NX_class")
        self.assertEqual(at[...], "NXentry")

        at = en.attributes[attr2["name"]]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.name, "counter")
        self.assertEqual(at.dtype, "int32")
        self.assertEqual(at[...], 1234)

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_XML_field_attribute(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry1", "type": "NX_CHAR"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT32"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value1 = '1234'
        value2 = '34'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value1
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<attribute%s>' % (st)
        xml += value2
        xml += '</attribute>'
        xml += '</field>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry1")
        self.assertEqual(len(en.attributes), 2)
        self.assertEqual(en.read(), '1234')
        self.assertTrue(hasattr(en.shape, "__iter__"))
        self.assertEqual(len(en.shape), 0)
        self.assertEqual(en.shape, ())

        at = en.attributes["type"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "type")
        self.assertEqual(at[...], "NX_CHAR")

        at = en.attributes[attr2["name"]]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.name, "counter")
        self.assertEqual(at.dtype, "int32")
        self.assertEqual(at[...], 34)

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_field_attribute(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})

        attr1 = {"name": "entry1", "type": "NX_INT"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT32"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        self.assertEqual(el.startElement("field", attr1), None)
        self.assertEqual(el.characters("12"), None)
        self.assertEqual(el.startElement("attribute", attr2), None)
        self.assertEqual(el.characters("1234"), None)
        self.assertEqual(el.endElement("attribute"), None)
        self.assertEqual(el.endElement("field"), None)

        self.assertEqual(el.triggerPools, {})

        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.is_valid)
        self.assertEqual(en.name, "entry1")
        self.assertEqual(len(en.attributes), 2)
        self.assertTrue(hasattr(en.shape, "__iter__"))
        self.assertEqual(len(en.shape), 1)
        self.assertEqual(en.shape[0], 1)
        self.assertEqual(en.read(), 12)

        at = en.attributes["type"]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.dtype, "string")
        self.assertEqual(at.name, "type")
        self.assertEqual(at[...], "NX_INT")

        at = en.attributes[attr2["name"]]
        self.assertTrue(at.is_valid)
        self.assertTrue(hasattr(at.shape, "__iter__"))
        self.assertEqual(len(at.shape), 0)
        self.assertEqual(at.shape, ())

        self.assertEqual(at.name, "counter")
        self.assertEqual(at.dtype, "int32")
        self.assertEqual(at[...], 1234)

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        ins = TElement.instance
        self.assertTrue(isinstance(ins, TElement))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(ins.linked)
        self.assertTrue(ins.stored)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TEOS_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElementOS.instance = None
        TElement.strategy = None
        TElement.trigger = None
        el.elementClass = {"field": TElementOS}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        ins = TElementOS.instance
        self.assertTrue(isinstance(ins, TElementOS))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertEqual(TElementOS.groupTypes, {"NXmyentry": "myentry1"})
        self.assertTrue(ins.linked)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TEOL_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElementOL.instance = None
        TElement.strategy = None
        TElement.trigger = None
        el.elementClass = {"field": TElementOL}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        ins = TElementOL.instance
        self.assertTrue(isinstance(ins, TElementOL))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertEqual(TElementOL.groupTypes, {"NXmyentry": "myentry1"})
        self.assertEqual(len(ins.groupTypes), 0)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TEOF_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElementOF.instance = None
        TElement.strategy = None
        TElement.trigger = None
        el.elementClass = {"field": TElementOF}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        ins = TElementOF.instance
        self.assertTrue(isinstance(ins, TElementOF))
        self.assertTrue(ins.constructed)
        self.assertTrue(not ins.reloadmode)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertEqual(TElementOF.groupTypes, {"NXmyentry": "myentry1"})
        self.assertEqual(len(ins.groupTypes), 0)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_group_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement, "group": TElementOS}

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(not gr.reloadmode)
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_group_field_reload(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile, reloadmode=True)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement, "group": TElementOS}

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(not fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(fl.reloadmode)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(gr.reloadmode)
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(not gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_group_field_groupTypes(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)
        groupTypes = TNObject()
        TNObject("mmyentry2", "NXmmyentry2", groupTypes)
        TNObject("mmyentry3", "NXmmyentry3", groupTypes)

        el = NexusXMLHandler(self._eFile, groupTypes=groupTypes)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement, "group": TElementOS}

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_field_INIT(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.strategy = 'INIT'
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        self.assertTrue(isinstance(el.initPool, ThreadPool))

        ins = TElement.instance

        self.assertTrue(isinstance(ins, TElement))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(ins.linked)
        self.assertTrue(ins.stored)

        self.assertEqual("", ins.groupTypes[""])
        self.assertTrue(not ins.started)
        el.finalPool.runAndWait()
        self.assertTrue(not ins.started)
        el.stepPool.runAndWait()
        self.assertTrue(not ins.started)
        el.initPool.runAndWait()
        self.assertTrue(ins.started)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_field_INIT_canfail_false(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        dsp = DataSourcePool()
        el = NexusXMLHandler(self._eFile, datasources=dsp)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.strategy = 'INIT'
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement, "strategy": SElement}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        strtag = '<strategy mode="INIT" />'
        # dsvalue = '<device member="attribute">Something </device>
        # <record name="myrecord"></record>'
        # dsend = '</datasource>'
        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += strtag
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        self.assertTrue(isinstance(el.initPool, ThreadPool))

        ins = TElement.instance
        sins = SElement.instance

        self.assertEqual(sins.canfail, False)

        self.assertTrue(isinstance(ins, TElement))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(ins.linked)
        self.assertTrue(ins.stored)

        self.assertEqual("", ins.groupTypes[""])
        self.assertTrue(not ins.started)
        el.finalPool.runAndWait()
        self.assertTrue(not ins.started)
        el.stepPool.runAndWait()
        self.assertTrue(not ins.started)
        el.initPool.runAndWait()
        self.assertTrue(ins.started)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_field_INIT_canfail_true(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        dsp = DataSourcePool()
        dsp.canfail = True
        el = NexusXMLHandler(self._eFile, datasources=dsp)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.strategy = 'INIT'
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement, "strategy": SElement}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        strtag = '<strategy mode="INIT" />'

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += strtag
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        self.assertTrue(isinstance(el.initPool, ThreadPool))

        ins = TElement.instance

        sins = SElement.instance

        self.assertEqual(sins.canfail, True)

        self.assertTrue(isinstance(ins, TElement))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(ins.linked)
        self.assertTrue(ins.stored)

        self.assertEqual("", ins.groupTypes[""])
        self.assertTrue(not ins.started)
        el.finalPool.runAndWait()
        self.assertTrue(not ins.started)
        el.stepPool.runAndWait()
        self.assertTrue(not ins.started)
        el.initPool.runAndWait()
        self.assertTrue(ins.started)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_field_STEP(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        TElement.instance = None
        TElement.strategy = 'STEP'
        el.elementClass = {"field": TElement}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        self.assertTrue(isinstance(el.initPool, ThreadPool))

        ins = TElement.instance

        self.assertTrue(isinstance(ins, TElement))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(ins.linked)
        self.assertTrue(ins.stored)

        self.assertEqual("", ins.groupTypes[""])
        self.assertTrue(not ins.started)
        el.finalPool.runAndWait()
        self.assertTrue(not ins.started)
        el.initPool.runAndWait()
        self.assertTrue(not ins.started)
        el.stepPool.runAndWait()
        self.assertTrue(ins.started)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_field_FINAL(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.strategy = None
        TElement.trigger = None
        TElement.instance = None
        TElement.strategy = 'FINAL'
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)

        el.elementClass = {"field": TElement}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        self.assertTrue(isinstance(el.initPool, ThreadPool))

        ins = TElement.instance

        self.assertTrue(isinstance(ins, TElement))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(ins.linked)
        self.assertTrue(ins.stored)

        self.assertEqual("", ins.groupTypes[""])
        self.assertTrue(not ins.started)
        el.initPool.runAndWait()
        self.assertTrue(not ins.started)
        el.stepPool.runAndWait()
        self.assertTrue(not ins.started)
        el.finalPool.runAndWait()
        self.assertTrue(ins.started)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_TE_field_STEP_trigger(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = 'STEP'
        TElement.trigger = 'mytrigger'
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement}

        attr1 = {"name": "counter", "type": "NX_CHAR", "axis": 1}
        # sattr1 = {attr1["type"]: attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<field%s>' % (st)
        xml += value
        xml += '</field>'
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(len(el.triggerPools), 1)
        self.assertTrue(isinstance(el.triggerPools["mytrigger"], ThreadPool))
        self.assertTrue(isinstance(el.initPool, ThreadPool))

        ins = TElement.instance

        self.assertTrue(isinstance(ins, TElement))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(ins.linked)
        self.assertTrue(ins.stored)

        self.assertTrue(not ins.started)
        el.finalPool.runAndWait()
        self.assertTrue(not ins.started)
        el.initPool.runAndWait()
        self.assertTrue(not ins.started)
        el.stepPool.runAndWait()
        self.assertTrue(not ins.started)

        el.triggerPools["mytrigger"].runAndWait()
        self.assertTrue(ins.started)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_transparent(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        self.assertTrue('definition' in el.transparentTags)
        el.elementClass = {"field": TElement, "group": TElementOS}

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += '<definition></definition>'
        xml += value
        xml += '</field>'
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_transparent_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement, "group": TElementOS}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        xml += '<definition></definition>'
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_transparent_3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement, "group": TElementOS}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        xml += '<definition>'
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</definition>'
        xml += '</group>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_transparent_4(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"field": TElement, "group": TElementOS}
        el.transparentTags = ['mydefinition']

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<mydefinition>'
        xml += '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</group>'
        xml += '</mydefinition>'

        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        #       self.assertTrue(gr.fetched)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_unsupported(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = {"NXmmyentry": "mmyentry1"}
        el.elementClass = {"field": TElement, "group": TElementOS}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<mydefinition>'
        xml += '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</group>'
        xml += '</mydefinition>'

        self.assertTrue(el.raiseUnsupportedTag)
        self.myAssertRaise(UnsupportedTagError, sax.parseString, xml, el)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_unsupported_false(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = {"NXmmyentry": "mmyentry1"}
        el.elementClass = {"field": TElement, "group": TElementOS}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<mydefinition>'
        xml += '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += '</field>'
        xml += '</group>'
        xml += '</mydefinition>'

        el.raiseUnsupportedTag = False
        self.assertTrue(not el.raiseUnsupportedTag)
        if sys.version_info > (3,):
            sax.parseString(bytes(xml, "UTF-8"), el)
        else:
            sax.parseString(xml, el)
        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_inner(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        parser = sax.make_parser()
        errorHandler = sax.ErrorHandler()

        el = NexusXMLHandler(self._eFile, parser=parser)

        parser.setContentHandler(el)
        parser.setErrorHandler(errorHandler)

        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"group": TElementOS, "field": TElement}
        el.withXMLinput = {"datasource": InnerTag}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        dsstart = '<datasource myname="testdatasource">'
        dsvalue = '<device member="attribute">Something </device>' + \
                  '<record name="myrecord"></record>'
        dsend = '</datasource>'

        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += dsstart
        xml += dsvalue
        xml += dsend
        xml += '</field>'
        xml += '</group>'

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(StringIO(xml))
        parser.parse(inpsrc)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        ds = InnerTag.instance
        ds = InnerTag.instance
        self.assertEqual(len(ds.xml), 3)
        self.assertEqual(ds.xml[0], dsstart)
        self.assertEqual(ds.xml[1], dsvalue)
        self.assertEqual(ds.xml[2], dsend)
        self.assertEqual(ds.json, None)
        self.assertEqual(ds.constructed, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.stored, True)

        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_inner_DSDC(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        parser = sax.make_parser()
        errorHandler = sax.ErrorHandler()

        gjson = json.loads('{"data":{"myrecord":"1"}}')
        el = NexusXMLHandler(self._eFile, parser=parser, globalJSON=gjson)

        parser.setContentHandler(el)
        parser.setErrorHandler(errorHandler)

        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"group": TElementOS, "field": TElement}
        el.withXMLinput = {"datasource": InnerTagDSDC}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        dsstart = '<datasource myname="testdatasource">'
        dsvalue = '<device member="attribute">Something </device>' + \
                  '<record name="myrecord"></record>'
        dsend = '</datasource>'

        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += dsstart
        xml += dsvalue
        xml += dsend
        xml += '</field>'
        xml += '</group>'

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(StringIO(xml))
        parser.parse(inpsrc)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        ds = InnerTagDSDC.instance
        self.assertEqual(len(ds.xml), 3)
        self.assertEqual(ds.xml[0], dsstart)
        self.assertEqual(ds.xml[1], dsvalue)
        self.assertEqual(ds.xml[2], dsend)
        self.assertEqual(ds.json, gjson)
        self.assertEqual(ds.constructed, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.datasources, None)
        self.assertEqual(ds.decoders, None)

        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_inner_DSDC_2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        parser = sax.make_parser()
        errorHandler = sax.ErrorHandler()

        datasources = (lambda: "SOMETHING")
        decoders = (lambda: "SOMETHING2")
        gjson = json.loads('{"data":{"myrecord":"1"}}')
        el = NexusXMLHandler(
            self._eFile, parser=parser, globalJSON=gjson,
            datasources=datasources, decoders=decoders)

        parser.setContentHandler(el)
        parser.setErrorHandler(errorHandler)

        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"group": TElementOS, "field": TElement}
        el.withXMLinput = {"datasource": InnerTagDSDC}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        dsstart = '<datasource myname="testdatasource">'
        dsvalue = '<device member="attribute">Something </device>' + \
                  '<record name="myrecord"></record>'
        dsend = '</datasource>'

        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += dsstart
        xml += dsvalue
        xml += dsend
        xml += '</field>'
        xml += '</group>'

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(StringIO(xml))
        parser.parse(inpsrc)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        ds = InnerTagDSDC.instance
        self.assertEqual(len(ds.xml), 3)
        self.assertEqual(ds.xml[0], dsstart)
        self.assertEqual(ds.xml[1], dsvalue)
        self.assertEqual(ds.xml[2], dsend)
        self.assertEqual(ds.json, gjson)
        self.assertEqual(ds.constructed, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.datasources, datasources)
        self.assertEqual(ds.decoders, decoders)

        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_inner_DS(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        parser = sax.make_parser()
        errorHandler = sax.ErrorHandler()

        datasources = (lambda: "SOMETHING")
        decoders = (lambda: "SOMETHING2")
        gjson = json.loads('{"data":{"myrecord":"1"}}')
        el = NexusXMLHandler(
            self._eFile, parser=parser, globalJSON=gjson,
            datasources=datasources, decoders=decoders)

        parser.setContentHandler(el)
        parser.setErrorHandler(errorHandler)

        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"group": TElementOS, "field": TElement}
        el.withXMLinput = {"datasource": InnerTagDS}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        dsstart = '<datasource myname="testdatasource">'
        dsvalue = '<device member="attribute">Something </device>' + \
                  '<record name="myrecord"></record>'
        dsend = '</datasource>'

        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += dsstart
        xml += dsvalue
        xml += dsend
        xml += '</field>'
        xml += '</group>'

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(StringIO(xml))
        parser.parse(inpsrc)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        ds = InnerTagDS.instance
        self.assertEqual(len(ds.xml), 3)
        self.assertEqual(ds.xml[0], dsstart)
        self.assertEqual(ds.xml[1], dsvalue)
        self.assertEqual(ds.xml[2], dsend)
        self.assertEqual(ds.json, gjson)
        self.assertEqual(ds.constructed, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.datasources, datasources)
        self.assertEqual(ds.decoders, None)

        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)

    # constructor test
    # \brief It tests default settings
    def test_group_field_inner_DC(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        # file handle
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        # element file objects
        self._eFile = EFile([], None, self._nxFile)

        parser = sax.make_parser()
        errorHandler = sax.ErrorHandler()

        datasources = (lambda: "SOMETHING")
        decoders = (lambda: "SOMETHING2")
        gjson = json.loads('{"data":{"myrecord":"1"}}')
        el = NexusXMLHandler(
            self._eFile, parser=parser, globalJSON=gjson,
            datasources=datasources, decoders=decoders)

        parser.setContentHandler(el)
        parser.setErrorHandler(errorHandler)

        self.assertTrue(isinstance(el.initPool, ThreadPool))
        self.assertTrue(isinstance(el.stepPool, ThreadPool))
        self.assertTrue(isinstance(el.finalPool, ThreadPool))
        self.assertEqual(el.triggerPools, {})
        TElement.instance = None
        TElement.strategy = None
        TElement.trigger = None
        TElement.groupTypes = TNObject()
        # ch =
        TNObject("mmyentry1", "NXmmyentry", TElement.groupTypes)
        el.elementClass = {"group": TElementOS, "field": TElement}
        el.withXMLinput = {"datasource": InnerTagDC}
        self.assertTrue('definition' in el.transparentTags)

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "counter", "type": "NX_INT"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        value = '1234'
        dsstart = '<datasource myname="testdatasource">'
        dsvalue = '<device member="attribute">Something </device>' + \
                  '<record name="myrecord"></record>'
        dsend = '</datasource>'

        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a])
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a])
        xml += '<field%s>' % (st)
        xml += value
        xml += dsstart
        xml += dsvalue
        xml += dsend
        xml += '</field>'
        xml += '</group>'

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(StringIO(xml))
        parser.parse(inpsrc)

        self.assertEqual(el.triggerPools, {})

        fl = TElement.instance
        gr = TElementOS.instance
        ds = InnerTagDC.instance
        self.assertEqual(len(ds.xml), 3)
        self.assertEqual(ds.xml[0], dsstart)
        self.assertEqual(ds.xml[1], dsvalue)
        self.assertEqual(ds.xml[2], dsend)
        self.assertEqual(ds.json, gjson)
        self.assertEqual(ds.constructed, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.stored, True)
        self.assertEqual(ds.datasources, None)
        self.assertEqual(ds.decoders, decoders)

        self.assertTrue(isinstance(fl, TElement))
        self.assertTrue(fl.constructed)
        self.assertEqual(len(attr2), len(fl.attrs))
        for a in attr1:
            self.assertEqual(str(attr2[a]), fl.attrs[a])
        self.assertEqual(fl.last, gr)
        self.assertEqual(fl.content, [value])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(fl.linked)
        self.assertTrue(fl.stored)
        self.assertTrue(not fl.h5Object.closed)

        self.assertTrue(isinstance(gr, TElementOS))
        self.assertTrue(gr.constructed)
        self.assertEqual(len(attr1), len(gr.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), gr.attrs[a])
        self.assertEqual(gr.last, self._eFile)
        self.assertEqual(gr.content, [])
        self.assertTrue(
            TElement.groupTypes.child(nxtype="NXmmyentry") is not None)
        self.assertTrue(
            TElement.groupTypes.child(name="mmyentry1") is not None)
        self.assertTrue(gr.linked)
        self.assertTrue(not gr.h5Object.closed)

        el.close()

        self.assertTrue(not fl.h5Object.closed)
        self.assertTrue(not gr.h5Object.closed)

        self._nxFile.close()
        os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
