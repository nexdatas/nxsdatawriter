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

""" SAX parser for fetching name attributes of tags """

from xml import sax

import sys
import os
import weakref


from .Errors import XMLSyntaxError


class TNObject(object):

    """ Type Name object
    """

    def __init__(self, name="root", nxtype=None, parent=None):
        """ constructor

        :brief: It sets default values of TNObject
        :param name: name of the object
        :type name: :obj:`str`
        :param nxtype: Nexus type of the object
        :type nxtype: :obj:`str`
        :param parent: object parent
        :type parent: :class:`nxswriter.Element.Element`
        """
        #: (:obj:`str`) object name
        self.name = name
        #: (:obj:`str`) object Nexus type
        self.nxtype = nxtype
        #:  (:class:`nxswriter.Element.Element`) object parent
        self.parent = weakref.ref(parent) if parent else lambda: None
        #: (:obj`:list` <:class:`nxswriter.Element.Element`>) object children
        self.children = []

        if hasattr(self.parent(), "children"):
            self.parent().children.append(self)

    def child(self, name='', nxtype=''):
        """ get child by name or nxtype

        :param name: group name
        :type name: :obj:`str`
        :param nxtype: nexus group type
        :type nxtype: :obj:`str`
        :returns: child instance
        :rtype: :class:`nxswriter.Element.Element`
        """
        if name:
            found = None
            for ch in self.children:
                if ch.name == name.strip():
                    found = ch
                    break
            return found
        elif nxtype:
            found = None
            for ch in self.children:
                if ch.nxtype == nxtype:
                    found = ch
                    break
            return found
        else:
            if len(self.children) > 0:
                return self.children[0]


class FetchNameHandler(sax.ContentHandler):

    """ SAX2 parser
    """

    def __init__(self, streams=None):
        """ constructor

        :brief: It constructs parser handler for fetching group names
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        sax.ContentHandler.__init__(self)

        #: (:class:`TNObject`) tree of TNObjects with names and types
        self.groupTypes = TNObject()
        #: (:class:`TNObject`) current object
        self.__current = self.groupTypes
        #: (:obj:`list` <:obj:`str`>) stack with open tag names
        self.__stack = []
        #: (:obj:`str`) name of attribute tag
        self.__attrName = ""
        #: (:obj:`list` <:obj:`str`>) content of attribute tag
        self.__content = []
        #: (:obj:`bool`) True if inside attribute tag
        self.__attribute = False
        #: (:class:`StreamSet` or :class:`tango.LatestDeviceImpl`) stream set
        self._streams = streams

    def startElement(self, name, attrs):
        """ parses the opening tag

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: attribute dictionary
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        """

        ttype = ""
        tname = ""

        if name == "group":
            if "type" in attrs.keys():
                ttype = attrs["type"]
            if "name" in attrs.keys():
                tname = attrs["name"]
            self.__current = TNObject(tname.strip(), ttype.strip(),
                                      self.__current)
            self.__stack.append(name)
        elif name == "attribute" and (
                not self.__stack or self.__stack[-1] == "group"):
            self.__content = []
            self.__attribute = True
            if "name" in attrs.keys() and attrs["name"] in ["name", "type"]:
                self.__attrName = attrs["name"]

    def characters(self, content):
        """ adds the tag content

        :param content: partial content of the tag
        :type content: :obj:`str`
       """
        if self.__attribute and (
                not self.__stack or self.__stack[-1] == "group"):
            self.__content.append(content)

    def endElement(self, name):
        """ parses an closing tag

        :param name: tag name
        :type name: :obj:`str`
        """
        if name == "group":

            if not self.__current.nxtype or not self.__current.name:
                if self.__current.nxtype and len(self.__current.nxtype) > 2:
                    self.__current.name = self.__current.nxtype[2:]
                else:
                    if self._streams:
                        self._streams.error(
                            "FetchNameHandler::endElement() - "
                            "The group type not defined",
                            std=False)

                    raise XMLSyntaxError("The group type not defined")
            self.__current = self.__current.parent()
            self.__stack.pop()

        if name == "attribute" and (
                not self.__stack or self.__stack[-1] == "group"):
            if self.__attrName:
                content = ("".join(self.__content)).strip()
                if content:
                    if self.__attrName == "name":
                        self.__current.name = content.strip()
                    if self.__attrName == "type":
                        self.__current.nxtype = content.strip()

            self.__attribute = False
            self.__content = []
            self.__attrName = None


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("usage: FetchNameHadler.py  <XMLinput>")

    else:
        #: (:obj:`str`) input XML file
        fi = sys.argv[1]
        if os.path.exists(fi):

            #: (:class:`xml.sax.xmlreader.XMLReader`) parser object
            parser = sax.make_parser()

            #: (:class:`FetchNameHandler`) SAX2 handler object
            handler = FetchNameHandler()
            parser.setContentHandler(handler)
            with open(fi) as fl:
                parser.parse(fl)
            print("GT: %s" % handler.groupTypes)
