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

""" Definitions of link tag evaluation classes """

import sys
import weakref

from .FElement import FElement
from .Errors import (XMLSettingSyntaxError)
from .DataHolder import DataHolder

from nxstools import filewriter as FileWriter


class ELink(FElement):

    """ link H5 tag element
    """

    def __init__(self, attrs, last, streams=None):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        FElement.__init__(self, "link", attrs, last, streams=streams)
        #: (:class:`nxswriter.FileWriter.FTLink`) \
        #:     stored H5 file object (defined in base class)
        self.h5Object = None
        #: (:obj:`str`) strategy, i.e. INIT, STEP, FINAL
        self.strategy = None
        #: (:obj:`str`) trigger for asynchronous writting
        self.trigger = None
        self.__groupTypes = lambda: None
        self.__target = None
        self.__name = None

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj:`str`
        :param globalJSON: global JSON string
        :returns: (strategy, trigger)
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        :rtype: (:obj:`str`, :obj:`str`)
        """

        if "name" in self._tagAttrs.keys():
            if self.source:
                if self.source.isValid():
                    return self.strategy, self.trigger

    def run(self):
        """ runner

        :brief: During its thread run it fetches the data from the source
        """
        aname = self._tagAttrs["name"]
        try:
            if aname is not None:
                if self.source:
                    dt = self.source.getData()
                    dh = None
                    if dt:
                        dh = DataHolder(streams=self._streams, **dt)
                    if not dh:
                        message = self.setMessage("Data without value")
                        self.error = message
                    elif dh.value:
                        target = dh.cast('string')
                        self.createLink(self.__groupTypes, target)
        except Exception:
            message = self.setMessage(sys.exc_info()[1].__str__())
            self.error = message
        #            self.error = sys.exc_info()
        finally:
            if self.error and self._streams:
                if self.canfail:
                    self._streams.warn("Link::run() - %s  " % str(self.error))
                else:
                    self._streams.error("Link::run() - %s  " % str(self.error))

    def createLink(self, groupTypes=None, target=None):
        """ creates the link the H5 file

        :param groupTypes: dictionary with type:name group pairs
        :type groupTypes: :obj:`dict` <:obj:`str` ,  :obj:`str` >
        :param target: NeXus target path
        :type target: :obj: `str`
        """
        if groupTypes is not None:
            if not hasattr(groupTypes, "__call__"):
                groupTypes = weakref.ref(groupTypes)
            if groupTypes():
                self.__groupTypes = groupTypes
        if "name" in self._tagAttrs.keys():
            self.__setTarget(target)
            if self.__target:
                name = self._tagAttrs["name"]
                try:
                    self.h5Object = FileWriter.link(
                        self.__target,
                        self._lastObject(),
                        name)
                except Exception:
                    if self._streams:
                        self._streams.error(
                            "ELink::createLink() - "
                            "The link '%s' to '%s' type cannot be created"
                            % (name, self.__target),
                            std=False)
                    raise XMLSettingSyntaxError(
                        "The link '%s' to '%s' type cannot be created"
                        % (name, self.__target))
        else:
            if self._streams:
                self._streams.error("ELink::createLink() - No name or type",
                                    std=False)

            raise XMLSettingSyntaxError("No name or type")

    def __setTarget(self, target=None):
        """sets the link target

        :param target: NeXus target path
        :type target: :obj: `str`
        """
        if target is None and "target" in self._tagAttrs.keys():
            target = self._tagAttrs["target"]
        if target is None and ("".join(self.content)).strip():
            target = ("".join(self.content)).strip()
        if target is not None:
            if ':/' not in str(target) \
               and self.__groupTypes is not None and \
               self.__groupTypes() is not None:
                self.__target = (self.__typesToNames(
                    target, self.__groupTypes()))
            else:
                self.__target = str(target)

    def __typesToNames(self, text, groupTypes):
        """ converts types to Names using groupTypes dictionary

        :param text: original directory
        :type text: :obj: `str`
        :param groupTypes: tree of TNObject with name:nxtype
        :type groupTypes: :obj:`dict` <:obj:`str` ,  :obj:`str` >
        :returns: directory defined by group names
        :rtype: :obj: `str`
        """
        sp = str(text).split("/")
        res = ""
        ch = groupTypes
        valid = True if ch.name == "root" else False
        for gr in sp[:-1]:
            if len(gr) > 0:
                sgr = gr.split(":")
                if len(sgr) > 1:
                    res = "/".join([res, sgr[0]])
                    if valid:
                        ch = ch.child(name=sgr[0])
                        if not ch:
                            valid = False
                else:
                    if valid:
                        c = ch.child(nxtype=sgr[0])
                        if c:
                            res = "/".join([res, c.name])
                            ch = c
                        else:
                            c = ch.child(name=sgr[0])
                            if c:
                                res = "/".join([res, sgr[0]])
                                ch = c
                            else:
                                res = "/".join([res, sgr[0]])
                                valid = False
                    else:
                        if self._streams:
                            self._streams.error(
                                "ELink::__typesToNames() - "
                                "Link creation problem: %s cannot be found"
                                % str(res + "/" + sgr[0]),
                                std=False)

                        raise XMLSettingSyntaxError(
                            "Link creation problem: %s cannot be found"
                            % str(res + "/" + sgr[0]))
        res = res + "/" + sp[-1]

        return res
