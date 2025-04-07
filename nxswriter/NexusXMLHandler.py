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
#

""" SAX parser for interpreting content of  XML configuration string """

from xml import sax
import weakref

from .StreamSet import StreamSet

from .Element import Element
from .FElement import FElement
from .EGroup import EGroup
from .EField import EField
from .EVirtualField import EVirtualField, EVirtualDataMap, EVirtualSourceView
from .EAttribute import EAttribute
from .EStrategy import EStrategy
from .ELink import ELink
from .H5Elements import (
    EDoc, ESymbol, EDimensions, EDim, EFile, EFilter, ESlab, ESlice,
    ESelection)
from .DataSourceFactory import DataSourceFactory
from .ThreadPool import ThreadPool
from .InnerXMLParser import InnerXMLHandler
from .Errors import UnsupportedTagError
from .FetchNameHandler import TNObject


class NexusXMLHandler(sax.ContentHandler):

    """ SAX2 parser
    """

    def __init__(self, fileElement, datasources=None, decoders=None,
                 groupTypes=None, parser=None, globalJSON=None,
                 streams=None, reloadmode=False):
        """ constructor

        :brief: It constructs parser and defines the H5 output file
        :param fileElement: file element
        :type fileElement: :class:`nxswriter.H5Elements.EFile`
        :param decoders: decoder pool
        :type decoders: :class:`nxswriter.DecoderPool.DecoderPool`
        :param datasources: datasource pool
        :type datasources: :class:`nxswriter.DataSourcePool.DataSourcePool`
        :param groupTypes: map of NXclass : name
        :type groupTypes: :class:`nxswriter.FetchNameHandler.TNObject`
        :param parser: instance of sax.xmlreader
        :type parser: :class:`xml.sax.xmlreader.XMLReader`
        :param globalJSON: global json string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param reloadmode: reload mode
        :type reloadmode: :obj: `bool`
        """
        sax.ContentHandler.__init__(self)
        #: (:class:`nxswriter.TNObject`) map of NXclass : name
        self.__groupTypes = TNObject()
        #: (:obj:`bool`) if name fetching required
        self.__fetching = True
        if groupTypes:
            self.__groupTypes = weakref.ref(groupTypes)
            self.__fetching = False

        #: (:obj:`list` <:class:`nxswriter.Element.Element`>) \
        #:      stack with open tag elements
        self.__stack = [fileElement]

        #: (:obj:`str`) traced unsupported tag name
        self.__unsupportedTag = ""
        #: (:obj:`bool`) True if raise exception on unsupported tag
        self.raiseUnsupportedTag = True

        #: (:class:`xml.sax.xmlreader.XMLReader`) xmlreader
        self.__parser = weakref.ref(parser) \
            if parser else (lambda: None)
        #: (:class:`nxswriter.InnerXMLHandler.InnerXMLHandler`) \
        #:     inner xml handler
        self.__innerHandler = None

        #: (:obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>) \
        #:    global json string
        self.__json = dict(globalJSON) \
            if globalJSON is not None else None

        #: (:obj:`dict` <:obj:`str`: :class:`nxswriter.Element.Element` > ) \
        #:     tags with inner xml as its input
        self.withXMLinput = {'datasource': DataSourceFactory,
                             'doc': EDoc}
        # self.withXMLinput = {'doc': EDoc}
        # self.withXMLinput = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) stored attributes
        self.__storedAttrs = None
        #: (:obj:`str`) stored name
        self.__storedName = None

        #: (:obj:`bool`) reload mode
        self.__reloadmode = reloadmode

        #: (:obj:`dict` <:obj:`str`, :obj:`type` > ) \
        #: map of tag names to related classes
        self.elementClass = {
            'group': EGroup, 'field': EField,
            'attribute': EAttribute, 'link': ELink,
            'symbols': Element, 'symbol': ESymbol,
            'dimensions': EDimensions, 'dim': EDim,
            'enumeration': Element, 'item': Element,
            'strategy': EStrategy, 'filter': EFilter,
            'vds': EVirtualField, 'map': EVirtualDataMap,
            'sourceview': EVirtualSourceView,
            'slab': ESlab, 'slice': ESlice, 'selection': ESelection,
        }

        #: (:obj:`list` <:obj:`dict` <:obj:`str`, :obj:`str` > >) \
        #: list of entry group attributes
        self.entryAttrs = []

        #: (:obj:`dict` <:obj:`str`, :obj:`type` > ) \
        #: map of tag names to related classes
        self.withAttr = ['group', 'field', 'vds']

        #: (:obj:`list` <:obj:`str`>) transparent tags
        self.transparentTags = ['definition']

        #: (:class:`nxswriter.ThreadPool.ThreadPool`) \
        #:       thread pool with INIT elements
        self.initPool = ThreadPool(streams=StreamSet(
             weakref.ref(streams) if streams else None))
        # self.initPool = ThreadPool()
        #: (:class:`nxswriter.ThreadPool.ThreadPool`) \
        #:       thread pool with STEP elements
        self.stepPool = ThreadPool(streams=StreamSet(
            weakref.ref(streams) if streams else None))
        # self.stepPool = ThreadPool()
        #: (:class:`nxswriter.ThreadPool.ThreadPool`) \
        #:      thread pool with FINAL elements
        self.finalPool = ThreadPool(streams=StreamSet(
            weakref.ref(streams) if streams else None))
        # self.finalPool = ThreadPool()

        #: (:obj:`dict` \
        #:  <:obj:`str`, :class:`nxswriter.ThreadPool.ThreadPool`> ) \
        #:  map of pool names to related classes
        self.__poolMap = {'INIT': self.initPool,
                          'STEP': self.stepPool,
                          'FINAL': self.finalPool}
        #: (:obj:`dict` <:obj:`str`, \
        #:  :class:`nxswriter.ThreadPool.ThreadPool`> ) \
        #:  collection of thread pool with triggered STEP elements
        self.triggerPools = {}

        #: (:class:`nxswriter.DecoderPool.DecoderPool`) pool with decoders
        self.__decoders = weakref.ref(decoders) if decoders else (lambda: None)

        #: (:class:`nxswriter.DataSourcePool.DataSourcePool`) \
        #:     pool with datasources
        self.__datasources = weakref.ref(datasources) \
            if datasources else (lambda: None)

        #: (:obj:`bool`) if innerparse was running
        self.__inner = False

        #: (:class:`StreamSet` or :class:`tango.LatestDeviceImpl`) stream set
        self._streams = streams

    def __last(self):
        """ the last stack element

        :returns: the last stack element
        :rtype: :class:`nxswriter.Element.Element`
        """
        if self.__stack:
            return self.__stack[-1]
        else:
            return None

    def characters(self, content):
        """ adds the tag content

        :param content: partial content of the tag
        :type content: :obj:`str`
        """
        if self.__inner is True:
            self.__createInnerTag(self.__innerHandler.xml)
            self.__inner = False
        if not self.__unsupportedTag:
            self.__last().content.append(content)

    def startElement(self, name, attrs):
        """ parses the opening tag

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: attribute dictionary
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        """
        if name == 'group' and len(self.__stack) == 1:
            self.entryAttrs.append(dict(attrs))
        if self.__inner is True:
            if hasattr(self.__innerHandler, "xml"):
                self.__createInnerTag(self.__innerHandler.xml)
            self.__inner = False
        if not self.__unsupportedTag:
            if self.__parser() and name in self.withXMLinput:
                self.__storedAttrs = attrs
                self.__storedName = name
                self.__innerHandler = InnerXMLHandler(
                    self.__parser(), self, name, attrs)
                self.__parser().setContentHandler(self.__innerHandler)
                self.__inner = True
            elif name in self.withAttr:
                self.__stack.append(
                    self.elementClass[name](
                        attrs, self.__last(),
                        streams=StreamSet(
                            weakref.ref(self._streams)
                            if self._streams else None),
                        reloadmode=self.__reloadmode))
            elif name in self.elementClass:
                self.__stack.append(
                    self.elementClass[name](
                        attrs, self.__last(),
                        streams=StreamSet(
                            weakref.ref(self._streams)
                            if self._streams else None)))
                if hasattr(self.__datasources(), "canfail") \
                   and self.__datasources().canfail \
                   and hasattr(self.__stack[-1], "setCanFail"):
                    self.__stack[-1].setCanFail()
            elif name not in self.transparentTags:
                if self.raiseUnsupportedTag:
                    if self._streams:
                        self._streams.error(
                            "NexusXMLHandler::startElement() - "
                            "Unsupported tag: %s, %s "
                            % (name, list(attrs.keys())),
                            std=False)

                    raise UnsupportedTagError(
                        "Unsupported tag: %s, %s " %
                        (name, list(attrs.keys())))
                if self._streams:
                    self._streams.warn(
                        "NexusXMLHandler::startElement() - "
                        "Unsupported tag: %s, %s " %
                        (name, list(attrs.keys())))

                self.__unsupportedTag = name

    def endElement(self, name):
        """ parses the closing tag

        :param name: tag name
        :type name: :obj:`str`
        """
        if self.__inner is True:
            self.__createInnerTag(self.__innerHandler.xml)
            self.__inner = False
        if not self.__unsupportedTag and self.__parser() \
                and name in self.withXMLinput:
            pass
        elif not self.__unsupportedTag and name in self.elementClass:
            if hasattr(self.__last(), "store") \
                    and callable(self.__last().store):
                res = self.__last().store()
                if res:
                    self.__addToPool(res, self.__last())
            if hasattr(self.__last(), "createLink") and \
               callable(self.__last().createLink) and not self.__reloadmode:
                self.__last().createLink(self.__groupTypes)
            self.__stack.pop()
        elif name not in self.transparentTags:
            if self.__unsupportedTag == name:
                self.__unsupportedTag = ""

    def __addToPool(self, res, task):
        """ addding to pool

        :param res: strategy or (strategy, trigger)
        :type res: :obj:`str` or (:obj:`str`, :obj:`str`)
        :param task: Element with inner xml
        :type task: :class:`nxswriter.Element.Element`
        """
        trigger = None
        strategy = None
        if res:
            if hasattr(res, "__iter__"):
                strategy = res[0]
                if len(res) > 1:
                    trigger = res[1]
            else:
                strategy = res

        if trigger and strategy == 'STEP':
            if trigger not in self.triggerPools.keys():
                self.triggerPools[trigger] = ThreadPool(
                    streams=StreamSet(
                        weakref.ref(self._streams)
                        if self._streams else None
                    ))
            self.triggerPools[trigger].append(task)
        elif strategy in self.__poolMap.keys():
            self.__poolMap[strategy].append(task)

    def __createInnerTag(self, xml):
        """ creates class instance of the current inner xml

        :param xml: inner xml
        :type xml: :obj:`str`
        """
        if self.__storedName in self.withXMLinput:
            res = None
            inner = self.withXMLinput[self.__storedName](
                self.__storedAttrs, self.__last(),
                streams=StreamSet(
                    weakref.ref(self._streams)
                    if self._streams else None
                ))
            if hasattr(inner, "setDataSources") \
                    and callable(inner.setDataSources):
                inner.setDataSources(self.__datasources())
            if hasattr(inner, "store") and callable(inner.store):
                res = inner.store(xml, self.__json)
            if hasattr(inner, "setDecoders") and callable(inner.setDecoders):
                inner.setDecoders(self.__decoders())
            if res:
                self.__addToPool(res, inner)

    def close(self):
        """ closes the elements

        :brief: It goes through all stack elements closing them
        """
        for s in self.__stack:
            if isinstance(s, FElement) and not isinstance(s, EFile):
                if hasattr(s.h5Object, "close") and callable(s.h5Object.close):
                    s.h5Object.close()
