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

""" Definitions of file tag evaluation classes """

import numpy
import sys

from .DataHolder import DataHolder
from .Element import Element
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)


class FElement(Element):

    """ NeXuS runnable tag element
    tag element corresponding to one of H5 objects
    """

    def __init__(self, name, attrs, last, h5object=None, streams=None):
        """ constructor

        :param name: tag name
        :type name: :obj: `str`
        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param h5object: H5 file object
        :type h5object: :class:`nxswriter.FileWriter.FTObject`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        """
        Element.__init__(self, name, attrs, last, streams=streams)
        #: (:class:`nxswriter.FileWriter.FTObject`) stored H5 file object
        self.h5Object = h5object
        #: (:class:`nxswriter.DataSources.DataSource`) data source
        self.source = None
        #: (:obj:`str`) notification of error in the run method
        self.error = None
        #: (:obj:`float`) runtime
        self.runtime = 0
        #: (:obj:`bool`) flag for devices for which is allowed to failed
        self.canfail = False
        #: (:obj:`bool`) scalar type
        self._scalar = False

    def run(self):
        """ runner

        :brief: During its thread run it fetches the data from the source
        """
        if self.source:
            self.source.getData()

    @classmethod
    def _reshape(cls, dsShape, rank, extends, extraD, exDim):
        """ recalculates shape

        :param dsShape: origin shape of the object
        :type dsShape: :obj:`list` <:obj:`int` >
        :param rank: rank of the object
        :type rank: : obj:`str` or obj:`int`
        :param extends: If True extends the shape up to rank value
        :type extends: :obj:`bool`
        :param exDim: grows growing dimension + 1
        :type exDim: :obj:`int`
        :param extraD: True if the object grows
        :type extraD: :obj:`bool`
        :returns: shape of the  h5 field
        :rtype: :obj:`list` <:obj:`int` >

        """
        shape = []
        if dsShape:
            for s in dsShape:
                if s and extends:
                    shape.append(s)
                elif not extends and s and s > 0:
                    shape.append(s)

            while extends and len(shape) < int(rank):
                shape.append(0)
            if extraD:
                shape.insert(exDim - 1, 0)
        return shape

    def __fetchShape(self, value, rank):
        """ fetches shape from value and rank

        :param rank: rank of the object
        :type rank: : obj:`str` or obj:`int`
        :param value: value of the object
        :type value: : obj:`str`
        :returns: shape of the value
        :rtype: :obj:`list` <:obj:`int` >
        """
        if not rank or int(rank) == 0:
            return [1]
        elif int(rank) == 1:
            spec = value.split()
            return [len(spec)]
        elif int(rank) == 2:
            lines = value.split("\n")
            image = [ln.split() for ln in lines]
            return [len(image), len(image[0])]
        else:
            if self._streams:
                self._streams.error(
                    "FElement::__fetchShape() "
                    "- Case with not supported rank = %s" % rank,
                    std=False)

            raise XMLSettingSyntaxError(
                "Case with not supported rank = %s" % rank)

    @classmethod
    def _getExtra(cls, grows, extraD=False):
        """ provides growing dimension

        :param grows: growing dimension
        :type grows: :obj:`int`
        :param extraD: True if the object grows
        :type extraD: :obj:`bool`
        :returns: growing dimension
        :rtype: :obj:`int`
        """
        if extraD:
            if grows and grows > 1:
                exDim = grows
            else:
                exDim = 1
        else:
            exDim = 0
        return exDim

    def _findShape(self, rank, lengths=None, extraD=False,
                   grows=None, extends=False, checkData=False):
        """ creates shape object from rank and lengths variables
            raises XMLSettingSyntaxError: if shape cannot be found


        :param rank: rank of the object
        :type rank: :obj:`str`
        :param lengths: dictionary with dimensions as a string data ,
                        e.g. {"1":"34","2":"40"}
        :type lengths:  :obj:`dict` <:obj:`str`, :obj:`str`>
        :param extraD: if the object grows
        :type extraD: :obj:`bool`
        :param grows: growing dimension
        :type grows: :obj:`int`
        :param extends: If True extends the shape up to rank value
        :type extends: :obj:`bool`
        :returns shape: of the object
        :rtype: :obj:`list` <:obj:`int` >
        """
        self._scalar = False
        shape = []
        exDim = self._getExtra(grows, extraD)
        if int(rank) > 0:
            try:
                for i in range(int(rank)):
                    si = str(i + 1)
                    if lengths and si in lengths.keys() \
                            and lengths[si] is not None:
                        if int(lengths[si]) > 0:
                            shape.append(int(lengths[si]))
                    else:
                        raise XMLSettingSyntaxError(
                            "Dimensions not defined")
                if len(shape) < int(rank):
                    raise XMLSettingSyntaxError(
                        "Too small dimension number")

                if extraD:
                    shape.insert(exDim - 1, 0)
            except Exception:
                if sys.version_info > (3,):
                    val = ("".join(self.content)).strip()
                else:
                    val = ("".join(self.content)).strip().encode("utf-8")
                found = False
                if checkData and self.source and self.source.isValid():
                    data = self.source.getData()
                    if isinstance(data, dict):
                        dh = DataHolder(streams=self._streams, **data)
                        shape = self._reshape(dh.shape, rank, extends,
                                              extraD, exDim)
                        if shape is not None:
                            found = True

                if val and not found:
                    shape = self.__fetchShape(val, rank)
                    if shape is not None:
                        found = True

                if not found:
                    nm = "unnamed"
                    if "name" in self._tagAttrs.keys():
                        nm = self._tagAttrs["name"] + " "
                    raise XMLSettingSyntaxError(
                        "Wrongly defined %s shape: %s" %
                        (nm, str(self.source) if self.source else val))

        elif extraD:
            shape = [0]

        if shape == []:
            self._scalar = True
        return shape

    def setMessage(self, exceptionMessage=None):
        """ creates the error message

        :param exceptionMessage: additional message of exception
        :type  exceptionMessage: :obj:`str`
        :returns: error message
        :rtype: :obj:`str`
        """
        if hasattr(self.h5Object, "path"):
            name = self.h5Object.path
        elif hasattr(self.h5Object, "name"):
            name = self.h5Object.name
        else:
            name = "unnamed object"
        if self.source:
            dsource = str(self.source)
        else:
            dsource = "unknown datasource"

        message = ("Data for %s not found. DATASOURCE:%s"
                   % (name, dsource), exceptionMessage)
        return message


class FElementWithAttr(FElement):

    """ NeXuS runnable tag element with attributes
        tag element corresponding to one of H5 objects with attributes
    """

    def __init__(self, name, attrs, last, h5object=None, streams=None,
                 reloadmode=False):
        """ constructor

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param h5object: H5 file object
        :type h5object: :class:`nxswriter.FileWriter.FTObject`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param reloadmode: reload mode
        :type reloadmode: :obj:`bool`
        """

        FElement.__init__(self, name, attrs, last, h5object, streams=streams)
        #: (:obj:`dict` <:obj:`str`, (:obj:`str`, :obj:`str`, :obj:`tuple`)>  \
        #:     or :obj:`dict` <:obj:`str`, (:obj:`str`, :obj:`str`) > ) \
        #:     dictionary with attribures from sepatare attribute tags
        #:     written as (name, value, shape)
        self.tagAttributes = {}
        #: (:obj:`dict` <:obj:`str`, h5object>) h5 instances
        self.__h5Instances = {}
        #: (:obj:`bool`) reload mode
        self._reloadmode = reloadmode

    def _setValue(self, rank, val):
        """ creates DataHolder with given rank and value

        :param rank: data rank
        :type rank: :obj:`int`
        :param val: data value
        :type value: any
        :returns: data holder
        :rtype: :class:`nxswriter.DataHolder.DataHolder`
        """
        dh = None
        if not rank or rank == 0:
            dh = DataHolder("SCALAR", val, "DevString", [1, 0],
                            streams=self._streams)
        elif rank == 1:
            spec = val.split()
            dh = DataHolder("SPECTRUM", spec, "DevString",
                            [len(spec), 0],
                            streams=self._streams)
        elif rank == 2:
            lines = str(val).split("\n")
            image = [ln.split() for ln in lines]
            dh = DataHolder("IMAGE", image, "DevString",
                            [len(image), len(image[0])],
                            streams=self._streams)
        else:
            if self._streams:
                self._streams.error(
                    "FElement::_createAttributes() - "
                    "Case with not supported rank = %s" % rank,
                    std=False)

            raise XMLSettingSyntaxError(
                "Case with not supported rank = %s", rank)
        return dh

    def _createAttributes(self):
        """ creates h5 attributes

        :brief: It creates attributes instances which have been
                stored in tagAttributes dictionary
        """
        for key in self.tagAttributes.keys():
            if key not in ["name", "type"]:
                if sys.version_info > (3,):
                    ekey = key
                else:
                    ekey = key.encode()
                if self._reloadmode:
                    fat = None
                    for at in self.h5Object.attributes:
                        if at.name == key:
                            self.__h5Instances[ekey] = fat = at
                            break
                    if fat:
                        fat = None
                        continue

                if len(self.tagAttributes[key]) < 3:
                    if sys.version_info > (3,):
                        if ekey not in self.__h5Instances:
                            self.__h5Instances[ekey] \
                                = self.h5Object.attributes.create(
                                    ekey,
                                    NTP.nTnp[self.tagAttributes[key][0]])
                        dh = DataHolder(
                            "SCALAR", self.tagAttributes[key][1].strip(),
                            "DevString", [1, 0],
                            streams=self._streams)
                    else:
                        if sys.version_info > (3,):
                            if ekey not in self.__h5Instances:
                                self.__h5Instances[ekey] \
                                    = self.h5Object.attributes.create(
                                        ekey,
                                        NTP.nTnp[self.tagAttributes[key][0]])
                            dh = DataHolder(
                                "SCALAR", self.tagAttributes[key][1].strip(),
                                "DevString", [1, 0],
                                streams=self._streams)
                        else:
                            if ekey not in self.__h5Instances:
                                self.__h5Instances[ekey] \
                                    = self.h5Object.attributes.create(
                                        ekey,
                                        NTP.nTnp[
                                            self.tagAttributes[key][
                                                0]].encode())
                            dh = DataHolder(
                                "SCALAR",
                                self.tagAttributes[key][1].strip().encode(),
                                "DevString", [1, 0],
                                streams=self._streams)

                    self.__h5Instances[ekey][...] = \
                        dh.cast(self.__h5Instances[ekey].dtype)
                else:
                    shape = self.tagAttributes[key][2]
                    if sys.version_info > (3,):
                        if ekey not in self.__h5Instances.keys():
                            self.__h5Instances[ekey] \
                                = self.h5Object.attributes.create(
                                    ekey,
                                    NTP.nTnp[self.tagAttributes[key][0]],
                                    shape)
                        val = self.tagAttributes[key][1].strip()
                    else:
                        if ekey not in self.__h5Instances.keys():
                            self.__h5Instances[ekey] \
                                = self.h5Object.attributes.create(
                                    ekey,
                                    NTP.nTnp[
                                        self.tagAttributes[key][0]].encode(),
                                    shape)
                        val = self.tagAttributes[key][1].strip().encode()
                    if val:
                        rank = len(shape)
                        hsp = self.__h5Instances[ekey].shape
                        if (hsp == ()) and \
                           self.__h5Instances[ekey].dtype in ['string', 'str']:
                            dh = self._setValue(0, val)
                        else:
                            dh = self._setValue(rank, val)
                        self.__h5Instances[ekey][...] = dh.cast(
                            self.__h5Instances[ekey].dtype)

    def _setAttributes(self, excluded=None):
        """ creates attributes

        :brief: It creates attributes in h5Object

        :param excluded: names of excluded attributes
        :type excluded: :obj:`list` <:obj:`str`>
        """
        excluded = excluded or []
        for key in self._tagAttrs.keys():
            if key not in excluded:
                if sys.version_info > (3,):
                    ekey = key
                else:
                    ekey = key.encode()
                if key in NTP.aTn.keys():
                    if sys.version_info > (3,):
                        h5att = self.h5Object.attributes.create(
                            ekey,
                            NTP.nTnp[NTP.aTn[key]].encode(),
                            overwrite=True
                        )
                    else:
                        h5att = self.h5Object.attributes.create(
                            ekey,
                            NTP.nTnp[NTP.aTn[key]],
                            overwrite=True
                        )
                    if sys.version_info < (3,) and \
                       hasattr(self._tagAttrs[key], "encode"):
                        try:
                            h5att[...] = NTP.convert[
                                self.h5Object.attributes[
                                    ekey].dtype
                            ](self._tagAttrs[key].strip().encode())
                        except Exception:
                            h5att[...] = self._tagAttrs[key].strip().encode()
                    else:
                        try:
                            h5att[...] = NTP.convert[
                                self.h5Object.attributes[
                                    ekey].dtype
                            ](self._tagAttrs[key])
                        except Exception:
                            h5att[...] = self._tagAttrs[key]

                elif key in NTP.aTnv.keys():
                    try:
                        dh = self._setValue(1, self._tagAttrs[key])
                        shape = (dh.shape[0],)
                        if sys.version_info > (3,):
                            self.h5Object.attributes.create(
                                ekey,
                                NTP.nTnp[NTP.aTnv[key]],
                                shape,
                                overwrite=True
                            )[...] = dh.cast(NTP.nTnp[NTP.aTnv[key]])
                        else:
                            self.h5Object.attributes.create(
                                ekey,
                                NTP.nTnp[NTP.aTnv[key]].encode(),
                                shape,
                                overwrite=True
                            )[...] = dh.cast(NTP.nTnp[NTP.aTnv[key]].encode())
                    except Exception:
                        sarr = self._tagAttrs[key].split()
                        if sys.version_info > (3,):
                            self.h5Object.attributes.create(
                                ekey,
                                NTP.nTnp[NTP.aTnv[key]],
                                (len(sarr),),
                                overwrite=True
                            )[...] = numpy.array(sarr)
                        else:
                            self.h5Object.attributes.create(
                                ekey,
                                NTP.nTnp[NTP.aTnv[key]].encode(),
                                (len(sarr),),
                                overwrite=True
                            )[...] = numpy.array(sarr)
                else:
                    if sys.version_info > (3,):
                        self.h5Object.attributes.create(
                            ekey, "string", overwrite=True)[...] \
                            = self._tagAttrs[key].strip()
                    else:
                        try:
                            vl = self._tagAttrs[key].strip().encode()
                        except Exception:
                            vl = self._tagAttrs[key].strip().encode("utf-8")
                        self.h5Object.attributes.create(
                            ekey, "string", overwrite=True)[...] = vl

    def h5Attribute(self, name):
        """ provides attribute h5 object

        :param name: attribute name
        :type name: :obj:`str`
        :returns: instance of the attribute object if created
        :rtype: :class:`nxswriter.FileWriter.FTObject`
        """
        return self.__h5Instances.get(name)
