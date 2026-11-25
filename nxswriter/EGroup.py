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

""" Definitions of group tag evaluation classes """


from .FElement import FElementWithAttr
from .Errors import (XMLSettingSyntaxError)


class EGroup(FElementWithAttr):

    """ group H5 tag element
    """

    def __init__(self, attrs, last, streams=None,
                 reloadmode=False):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param reloadmode: reload mode
        :type reloadmode: :obj:`bool`
        """
        FElementWithAttr.__init__(self, "group", attrs, last, streams=streams,
                                  reloadmode=reloadmode)
        if self._lastObject() is not None:
            if ("type" in attrs.keys()) and ("name" in attrs.keys()):
                gname = attrs["name"]
            elif "type" in attrs.keys():
                gname = attrs["type"][2:]
            else:
                if self._streams:
                    self._streams.error(
                        "EGroup::__init__() - The group type not defined",
                        std=False)

                raise XMLSettingSyntaxError("The group type not defined")
            if self._reloadmode:
                names = [kd.name for kd in self._lastObject()]
                if gname in names:
                    self.h5Object = self._lastObject().open(gname)
                    return
            try:
                #: (:class:`nxswriter.FileWriter.FTGroup`) \
                #:      stored H5 file object (defined in base class)
                self.h5Object = self._lastObject().create_group(
                    gname, attrs["type"])
            except Exception as e:
                atype = attrs["type"].encode()
                if self._streams:
                    self._streams.debug(str(e))
                    self._streams.error(
                        "EGroup::__init__() - "
                        "The group '%s' of '%s' type cannot be created. \n"
                        "Please remove the old file, change the file name "
                        "or change the group name." %
                        (gname, atype),
                        std=False)

                raise XMLSettingSyntaxError(
                    "The group '%s' of '%s' type cannot be created. \n"
                    "Please remove the old file, change the file name "
                    "or change the group name." %
                    (gname, atype))

        else:
            if self._streams:
                self._streams.error(
                    "EGroup::__init__() - "
                    "File object for the last element does not exist",
                    std=False)

            raise XMLSettingSyntaxError(
                "File object for the last element does not exist")
        self._setAttributes(["name", "type"])

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj:`str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """

        self._createAttributes()
