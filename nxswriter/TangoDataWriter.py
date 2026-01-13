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

""" Tango Data Writer implementation """

import os
import shutil

from xml import sax
import json
import sys
import gc
import weakref
import time

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from .NexusXMLHandler import NexusXMLHandler
from .FetchNameHandler import FetchNameHandler
from .StreamSet import StreamSet
from nxstools import filewriter as FileWriter

from .H5Elements import EFile
from .EGroup import EGroup
from .DecoderPool import DecoderPool
from .DataSourcePool import DataSourcePool
from .Metadata import Metadata, NXSMETA


WRITERS = {}
try:
    from nxstools import h5pywriter as H5PYWriter
    WRITERS["h5py"] = H5PYWriter
except Exception:
    pass

try:
    from nxstools import h5cppwriter as H5CppWriter
    WRITERS["h5cpp"] = H5CppWriter
except Exception:
    pass


try:
    from nxstools import h5rediswriter as H5RedisWriter
    WRITERS["h5redis"] = H5RedisWriter
except Exception:
    pass
DEFAULTWRITERS = ["h5cpp", "h5py", "h5redis"]


#: (:obj:`bool`) tango bug #213 flag related to EncodedAttributes in python3
PYTG_BUG_213 = False
if sys.version_info > (3,):
    unicode = str
    try:
        try:
            import tango
        except Exception:
            import PyTango as tango
        PYTGMAJOR, PYTGMINOR, PYTGPATCH = list(
            map(int, tango.__version__.split(".")[:3]))
        if PYTGMAJOR <= 9:
            if PYTGMAJOR == 9:
                if PYTGMINOR < 2:
                    PYTG_BUG_213 = True
                elif PYTGMINOR == 2 and PYTGPATCH <= 4:
                    PYTG_BUG_213 = True
            else:
                PYTG_BUG_213 = True
    except Exception:
        pass


class TangoDataWriter(object):

    """ NeXuS data writer
    """

    def __init__(self, server=None):
        """ constructor

        :brief: It initialize the data writer for the H5 output file
        :param server: Tango server
        :type server: :class:`tango.LatestDeviceImpl`
        """
        #: (:obj:`str`) output file name and optional nexus parent path
        self.__parent = ""
        #: (:obj:`str`) output file name
        self.__fileName = ""
        #: (:obj:`str`) output file name prefix
        self.__fileprefix = ""
        #: (:obj:`str`) output file name extension
        self.__fileext = ""
        #: (:obj:`dict` <:obj:`str` , :obj:`any`>) open file parameters
        self.__pars = {}
        #: (:obj:`str`) XML string with file settings
        self.__xmlsettings = ""
        #: (:obj:`str`) global JSON string with data records
        self.__json = "{}"
        #: (:obj:`str`) nexus parent path of (name, type)
        self.__parents = []
        #: (:obj:`int`) maximal number of threads
        self.numberOfThreads = 100
        # self.numberOfThreads = 1
        #: (:obj:`float`) maximal element record time in sec
        self.maxElementRuntime = 0.0
        #: (:obj:`float`) maximal record time in sec
        self.maxRecordRuntime = 0.0

        #: (:class:`ThreadPool.ThreadPool`) thread pool with INIT elements
        self.__initPool = None
        #: (:class:`ThreadPool.ThreadPool`) thread pool with STEP elements
        self.__stepPool = None
        #: (:class:`ThreadPool.ThreadPool`) thread pool with FINAL elements
        self.__finalPool = None
        #: (:obj:`dict`< :obj:`str`, \
        #:  :class:`nxswriter.ThreadPool.ThreadPool` >) \
        #:     collection of thread pool with triggered STEP elements
        self.__triggerPools = {}
        #: (:obj:`list` <:obj:`dict` <:obj:`str`, :obj:`str` > >) \
        #: list of entry group attributes
        self.__entryAttrs = []
        #: (:class:`nxswriter.FileWriter.FTGroup`) H5 file handle
        self.__nxRoot = None
        #: (:obj: `list` <:class:`nxswriter.FileWriter.FTGroup` >)
        #      group path of H5 file handles
        self.__nxPath = []
        #: (:class:`nxswriter.FileWriter.FTFile`) H5 file handle
        self.__nxFile = None
        #: (:class:`nxswriter.H5Elements.EFile`) element file objects
        self.__eFile = None
        #: (:obj:`bool`) default value of canfail flag
        self.__defaultCanFail = True

        #: (:obj:`str`) writer type
        self.writer = None
        for wr in DEFAULTWRITERS:
            if wr in WRITERS.keys():
                self.writer = wr
                break

        #: (:obj:`str`) metadata output
        self.metadataOutput = ''
        #: (:obj:`int`) steps per file
        self.stepsperfile = 0

        #: (:obj:`int`) current file id
        self.__currentfileid = 0
        #: (:class:`nxswriter.DecoderPool.DecoderPool`) pool with decoders
        self.__decoders = DecoderPool()

        #: (:class:`nxswriter.DataSourcePool.DataSourcePool`) \
        #:      pool with datasources
        self.__datasources = DataSourcePool()

        #: (:class:`nxswriter.FetchNameHandler.FetchNameHandler`) \
        #:       group name parser
        self.__fetcher = None

        #: (:obj:`str`) adding logs
        self.addingLogs = True
        #: (:obj:`int`) counter for open entries
        self.__entryCounter = 0
        #: (:class:`nxswriter.FileWriter.FTGroup`) group with Nexus log Info
        self.__logGroup = None

        #: (:obj:`list` < :obj:`str`>) file names
        self.__filenames = []
        #: (:obj:`dict` < :obj:`str`, :obj:`str`>) file time stamps
        self.__filetimes = {}

        #: (:class:`StreamSet` or :class:`tango.LatestDeviceImpl`) stream set
        self._streams = StreamSet(weakref.ref(server) if server else None)

        #: (:obj:`bool`) skip acquisition flag
        self.skipacquisition = False
        if PYTG_BUG_213:
            self._streams.error(
                "TangoDataWriter::TangoDataWriter() - "
                "Reading Encoded Attributes for python3 and tango < 9.2.5"
                " is not supported ")

    def __setWriter(self, writer):
        """ set method for  writer module name

        :param jsonstring: value of  writer module name
        :type jsonstring: :obj:`str`
        """
        if '?' in writer:
            writer, params = writer.split('?')
        if not writer:
            for wr in DEFAULTWRITERS:
                if wr in WRITERS.keys():
                    writer = wr
                    break
        wrmodule = WRITERS[writer.lower()]
        FileWriter.setwriter(wrmodule)
        return wrmodule

    def __getCanFail(self):
        """ get method for the global can fail flag

        :returns: global can fail flag
        :rtype: :obj:`bool`
        """
        return self.__datasources.canfail

    def __setCanFail(self, canfail):
        """ set method for the global can fail flag

        :param canfail: the global can fail flag
        :type canfail: :obj:`bool`
        """
        self.__datasources.canfail = canfail

    #: the global can fail flag
    canfail = property(__getCanFail, __setCanFail,
                       doc='(:obj:`bool`) the global can fail flag')

    def __getDefaultCanFail(self):
        """ get method for the global can fail flag

        :returns: global can fail flag
        :rtype: :obj:`bool`
        """
        return self.__defaultCanFail

    def __setDefaultCanFail(self, canfail):
        """ set method for the global can fail flag

        :param canfail: the global can fail flag
        :type canfail: :obj:`bool`
        """
        self.__defaultCanFail = canfail
        self.__datasources.canfail = canfail

    #: the global can fail flag
    defaultCanFail = property(
        __getDefaultCanFail, __setDefaultCanFail,
        doc='(:obj:`bool`) default value of the global can fail flag')

    def __getJSON(self):
        """ get method for jsonrecord attribute

        :returns: value of jsonrecord
        :rtype: :obj:`str`
        """
        return self.__json

    def __setJSON(self, jsonstring):
        """ set method for jsonrecord attribute

        :param jsonstring: value of jsonrecord
        :type jsonstring: :obj:`str`
        """

        self.__decoders.appendUserDecoders(json.loads(jsonstring))
        self.__datasources.appendUserDataSources(json.loads(jsonstring))
        self.__json = jsonstring

    def __delJSON(self):
        """  del method for jsonrecord attribute
        """

        del self.__json

    #: the json data string
    jsonrecord = property(__getJSON, __setJSON, __delJSON,
                          doc='(:obj:`str`) the json data string')

    def __getCurrentFileID(self):
        """ get method for jsonrecord attribute

        :returns: value of jsonrecord
        :rtype: :obj:`str`
        """
        return self.__currentfileid

    #: the json data string
    currentfileid = property(__getCurrentFileID,
                             doc='(:obj:`str`) the current file id')

    def __getXML(self):
        """ get method for xmlsettings attribute

        :returns: value of jsonrecord
        :rtype: :obj:`str`
        """
        return self.__xmlsettings

    def __setXML(self, xmlset):
        """ set method for xmlsettings attribute

        :param xmlset: xml settings
        :type xmlset: :obj:`str`
        """
        self.__fetcher = FetchNameHandler(streams=self._streams)
        if sys.version_info > (3,):
            sax.parseString(xmlset, self.__fetcher)
        else:
            if isinstance(xmlset, unicode):
                sax.parseString(xmlset.encode('utf-8'), self.__fetcher)
            else:
                sax.parseString(xmlset, self.__fetcher)
        self.__xmlsettings = xmlset

    def __delXML(self):
        """ del method for xmlsettings attribute
        """
        del self.__xmlsettings

    #: the xmlsettings
    xmlsettings = property(__getXML, __setXML, __delXML,
                           doc='(:obj:`str`) the xml settings')

    def __getFileName(self):
        """ get method for parent attribute

        :returns: value of parent nexus path
        :rtype: :obj:`str`
        """
        return self.__parent

    def __setFileName(self, parent):
        """ set method for parent attribute

        :param parent: parent nexus path
        :type parent: :obj:`str`
        """
        parent = parent or ""
        lparent = str(parent).split(":/")
        if len(lparent) >= 3:
            fileName = lparent[1]
            nxpath = ":/".join(lparent[2:])
        elif len(lparent) == 2:
            fileName = lparent[0]
            nxpath = lparent[1]
        elif len(lparent) == 1:
            fileName = lparent[0]
            nxpath = ""

        spath = nxpath.split("/")
        parents = []
        for dr in spath:
            if dr.strip():
                w = dr.split(':')
                if len(w) == 1:
                    if len(w[0]) > 2 and w[0][:2] == 'NX':
                        w.insert(0, w[0][2:])
                    else:
                        w.append("NX" + w[0])
                parents.append((w[0], w[1]))
        self.__fileName = fileName
        self.__parents = parents
        self.__parent = parent

    def __delFileName(self):
        """ del method for parent attribute
        """
        del self.__parent

    #: the parent nexus path
    fileName = property(__getFileName, __setFileName, __delFileName,
                        doc='(:obj:`str`) file name and optional nexus path')

    def getFile(self):
        """ the H5 file handle

        :returns: the H5 file handle
        :rtype: :class:`nxswriter.FileWriter.FTFile`
        """
        return self.__nxFile

    def openFile(self):
        """ the H5 file opening

        :brief: It opens the H5 file
        """

        try:
            self.closeFile()
        except Exception:
            self._streams.warn(
                "TangoDataWriter::openFile() - File cannot be closed")

        wrmodule = self.__setWriter(self.writer)
        self.__nxFile = None
        self.__eFile = None
        self.__initPool = None
        self.__stepPool = None
        self.__finalPool = None
        self.__triggerPools = {}
        self.__currentfileid = 0

        self.__pars = self.__getParams(self.writer)
        pars = dict(self.__pars)
        pars["writer"] = wrmodule
        if os.path.isfile(self.__fileName):
            self.__nxFile = FileWriter.open_file(
                self.__fileName, False, **pars)
        else:
            self.__nxFile = FileWriter.create_file(
                self.__fileName, **pars)
        self.__fileprefix, self.__fileext = os.path.splitext(
            str(self.__fileName))
        self.__nxRoot = self.__nxFile.root()
        self.__nxRoot.stepsperfile = self.stepsperfile
        self.__nxRoot.currentfileid = self.__currentfileid

        #: element file objects
        self.__eFile = EFile([], None, self.__nxRoot)

        last = self.__eFile
        for gname, gtype in self.__parents:
            last = EGroup(
                {"name": gname, "type": gtype},
                last,
                reloadmode=True)
            self.__nxPath.append(last)

        if self.addingLogs:
            name = "nexus_logs"
            if not self.__nxRoot.exists(name):
                ngroup = self.__nxRoot.create_group(name)
            else:
                ngroup = self.__nxRoot.open(name)
            name = "configuration"
            error = True
            counter = 1
            cname = name
            while error:
                cname = name if counter == 1 else \
                    ("%s_%s" % (name, counter))
                if not ngroup.exists(cname):
                    error = False
                else:
                    counter += 1
            self.__logGroup = ngroup.create_group(cname)
            vfield = self.__logGroup.create_field(
                "python_version", "string")
            vfield.write(str(sys.version))
            vfield.close()

    def __getParams(self, url):
        """ fetch parameters from url

        :param url: url string, i.e. something?key1=value1&key2=value2&...
        :type url: :obj:`str`
        :returns: dictionary of parameters
        :rtype: :obj:`dict` < :obj:`str`,  :obj:`str`>
        """
        pars = {}
        if '?' in url:
            _, params = url.split('?')
            if params:
                parlist = params.split('&')
                for par in parlist:
                    if "=" in par:
                        ky, vl = par.split('=')
                        if ky:
                            if ky == "swmr":
                                vl = True if vl.lower() == "true" else False
                            pars[ky] = vl
        if "swmr" in pars and pars["swmr"] and "libver" not in pars:
            pars["libver"] = "latest"
        return pars

    def openEntry(self):
        """ opens the data entry corresponding to a new XML settings

        :brief: It parse the XML settings, creates thread pools
                and runs the INIT pool.
        """
        tt0 = time.time()
        if self._streams:
            self._streams.debug("openEntry: INIT")
        if self.xmlsettings:
            # flag for INIT mode
            self.__datasources.counter = -1
            self.__datasources.nxroot = self.__nxRoot
            errorHandler = sax.ErrorHandler()
            parser = sax.make_parser()
            if self._streams:
                self._streams.debug("openEntry: Create NexusXMLHnadler")
            handler = NexusXMLHandler(
                self.__nxPath[-1] if self.__nxPath else self.__eFile,
                self.__datasources,
                self.__decoders, self.__fetcher.groupTypes,
                parser, json.loads(self.jsonrecord),
                self._streams,
                self.skipacquisition
            )
            parser.setContentHandler(handler)
            parser.setErrorHandler(errorHandler)
            inpsrc = sax.InputSource()
            if sys.version_info > (3,):
                inpsrc.setByteStream(StringIO(self.xmlsettings))
            else:
                if isinstance(self.xmlsettings, unicode):
                    inpsrc.setByteStream(
                        StringIO(self.xmlsettings.encode('utf-8')))
                else:
                    inpsrc.setByteStream(StringIO(self.xmlsettings))

            if self._streams:
                self._streams.debug("openEntry: Parse NexusXMLHnadler")
            parser.parse(inpsrc)

            self.__initPool = handler.initPool
            self.__stepPool = handler.stepPool
            self.__finalPool = handler.finalPool
            self.__triggerPools = handler.triggerPools

            self.__entryAttrs = handler.entryAttrs

            self.__initPool.numberOfThreads = self.numberOfThreads
            self.__stepPool.numberOfThreads = self.numberOfThreads
            self.__finalPool.numberOfThreads = self.numberOfThreads

            self.__initPool.maxRuntime = self.maxElementRuntime
            self.__stepPool.maxRuntime = self.maxElementRuntime
            self.__finalPool.maxRuntime = self.maxElementRuntime

            for pool in self.__triggerPools.keys():
                self.__triggerPools[pool].numberOfThreads = \
                    self.numberOfThreads
                self.__triggerPools[pool].maxRuntime = \
                    self.maxElementRuntime

            if self._streams:
                self._streams.debug("openEntry: SET JSON")
            self.__initPool.setJSON(json.loads(self.jsonrecord))
            if self._streams:
                self._streams.debug("openEntry: RUN INIT")
            tt1 = time.time()
            if not self.skipacquisition:
                self.__initPool.runAndWait()
                self.__initPool.checkErrors()
            tt2 = time.time()
            if self._streams:
                self._streams.debug("openEntry: ADD LOGS")
            self.skipacquisition = False
            if self.addingLogs:
                self.__entryCounter += 1
                if not self.__logGroup.is_valid:
                    self.__logGroup.reopen()
                lfield = self.__logGroup.create_field(
                    "nexus__entry__%s_xml" % str(self.__entryCounter),
                    "string")
                lfield.write(self.xmlsettings)
                lfield.close()
            tt3 = time.time()
            if self._streams:
                self._streams.debug("openEntry: FLUSH")
            if self.__nxFile and hasattr(self.__nxFile, "flush"):
                self.__nxFile.flush()
            if self.stepsperfile > 0:
                self.__filenames = []
                self.__filetimes = {}
                self.__nextfile()
            elif "swmr" in self.__pars.keys() and self.__pars["swmr"]:
                self.__nxFile.reopen(readonly=False, **self.__pars)
            tt4 = time.time()
        else:
            tt4 = time.time()
            tt1 = tt4
            tt2 = tt4
            tt3 = tt4
        if self._streams:
            self._streams.debug("openEntry: PREPARE")
        if self.__nxFile and hasattr(self.__nxFile, "prepare"):
            # print("START")
            self.__nxFile.prepare()
        tt5 = time.time()
        if self._streams:
            dt = tt5 - tt0
            dt1 = tt1 - tt0
            dt2 = tt2 - tt1
            dt3 = tt3 - tt2
            dt4 = tt4 - tt3
            dt5 = tt5 - tt4
            message = "openEntry: END TotalTime = %ss, " \
                "ParseXMLTime=%ss, INITRunTime=%ss, " \
                "AddLogsTime=%ss, FlushTime=%ss, " \
                "PrepateTime=%ss" % (dt, dt1, dt2, dt3, dt4, dt5)
            if dt and self.maxRecordRuntime and \
                    dt > self.maxRecordRuntime:
                self._streams.warn(message)
            else:
                self._streams.debug(message)

    def __nextfile(self):
        self.__nxFile.close()
        self.__currentfileid += 1
        self.__nxRoot.currentfileid = self.__currentfileid
        self.__filenames.append("%s_%05d%s" % (
            self.__fileprefix,
            self.__currentfileid,
            self.__fileext)
        )
        shutil.copy2(self.__fileName, self.__filenames[-1])
        self.__filetimes[self.__filenames[-1]] = self.__nxFile.currenttime()
        self.__nxFile.name = self.__filenames[-1]
        self.__nxFile.reopen(readonly=False, **self.__pars)

    def __previousfile(self):
        self.__nxFile.close()
        self.__currentfileid -= 1
        self.__nxRoot.currentfileid = self.__currentfileid
        self.__filenames.pop()
        self.__nxFile.name = self.__filenames[-1]
        self.__nxFile.reopen(readonly=False, **self.__pars)

    def __removefile(self):
        if self.__filenames:
            filename = self.__filenames.pop()
            self.__nxFile.close()
            self.__currentfileid -= 1
            self.__nxRoot.currentfileid = self.__currentfileid
            os.remove(filename)
            self.__nxFile.name = self.__filenames[-1]
            self.__nxFile.reopen(readonly=False, **self.__pars)

    def record(self, jsonstring=None):
        """ runs threads form the STEP pool

        :brief: It runs threads from the STEP pool
        :param jsonstring: local JSON string with data records
        :type jsonstring: :obj:`str`
        """
        st = time.time()
        # flag for STEP mode
        if self.__datasources.counter > 0:
            self.__datasources.counter += 1
        else:
            self.__datasources.counter = 1

        localJSON = None
        if jsonstring:
            localJSON = json.loads(jsonstring)

        if self.__stepPool:
            self._streams.info(
                "TangoDataWriter::record() - Default trigger",
                False
            )
            self.__stepPool.setJSON(json.loads(self.jsonrecord), localJSON)
            if not self.skipacquisition:
                self.__stepPool.runAndWait()
                self.__stepPool.checkErrors()

        triggers = None
        if localJSON and 'triggers' in localJSON.keys():
            triggers = localJSON['triggers']

        if hasattr(triggers, "__iter__"):
            for pool in triggers:
                if pool in self.__triggerPools.keys():
                    self._streams.info(
                        "TangoDataWriter:record() - Trigger: %s" % pool,
                        False
                    )
                    self.__triggerPools[pool].setJSON(
                        json.loads(self.jsonrecord), localJSON)
                    if not self.skipacquisition:
                        self.__triggerPools[pool].runAndWait()
                        self.__triggerPools[pool].checkErrors()

        if self.__nxFile and hasattr(self.__nxFile, "flush"):
            self.__nxFile.flush()
        if self.__nxFile and hasattr(self.__nxFile, "start") and \
           self.__datasources.counter == 1:
            # print("START")
            self.__nxFile.start()
        if self.stepsperfile > 0:
            if (self.__datasources.counter) % self.stepsperfile == 0:
                self.__nextfile()
        self.skipacquisition = False
        dt = time.time() - st
        if dt and self.maxRecordRuntime and dt > self.maxRecordRuntime:
            mess = "TangoDataWriter.record() - " \
                "The maximal record time for #%s exceeded: %s s (%s s) " \
                % (self.__datasources.counter, dt, self.maxRecordRuntime)
            if self._streams:
                self._streams.warn(mess)

    def __updateNXRoot(self):
        fname = self.__filenames[-1]
        self.__nxRoot.attributes.create(
            "file_name", "string",
            overwrite=True)[...] = fname
        if fname in self.__filetimes and len(self.__filenames) > 1:
            self.__nxRoot.attributes.create(
                "file_time", "string",
                overwrite=True)[...] = str(self.__filetimes[fname])

    def closeEntry(self):
        """ closes the data entry

        :brief: It runs threads from the FINAL pool and
                removes the thread pools
        """
        # flag for FINAL mode
        if self.stepsperfile > 0:
            os.remove(self.__fileName)
            if (self.__datasources.counter) % self.stepsperfile == 0:
                self.__removefile()

        self.__datasources.counter = -2
        self.__datasources.canfail = self.defaultCanFail

        if self.addingLogs and self.__logGroup:
            self.__logGroup.close()
            # self.__logGroup = None

        if self.__finalPool:
            self.__finalPool.setJSON(json.loads(self.jsonrecord))
            if not self.skipacquisition:
                self.__finalPool.runAndWait()
            if self.stepsperfile > 0:
                self.__updateNXRoot()
                while len(self.__filenames) > 1:
                    self.__previousfile()
                    if not self.skipacquisition:
                        self.__finalPool.runAndWait()
                    self.__updateNXRoot()
            if not self.skipacquisition:
                self.__finalPool.checkErrors()
        self.skipacquisition = False

        if self.__initPool:
            self.__initPool.close()
        self.__initPool = None

        if self.__stepPool:
            self.__stepPool.close()
        self.__stepPool = None

        if self.__finalPool:
            self.__finalPool.close()
        self.__finalPool = None

        if self.__triggerPools:
            for pool in self.__triggerPools.keys():
                self.__triggerPools[pool].close()
            self.__triggerPools = {}

        if self.addingLogs and self.__logGroup:
            self.__logGroup.close()

        if self.__nxFile and hasattr(self.__nxFile, "flush"):
            self.__nxFile.flush()
        if self.__nxFile and hasattr(self.__nxFile, "finish"):
            self.__nxFile.finish()

        if NXSMETA and self.__nxRoot:
            args = {}
            if self.metadataOutput and \
               'file' in self.metadataOutput.split(","):
                for ad in self.__entryAttrs:
                    nm = ad.get("name", None)
                    tp = ad.get("type", None)
                    if nm and tp in ["NXentry"]:
                        args["output"] = "%s.%s.json" % (
                            self.__fileName, ad["name"])
                        args["args"] = [self.__fileName]
                        args["entrynames"] = nm
                        mdata = Metadata(self.__nxRoot).get(**args)
                        if mdata:
                            if args["output"]:
                                with open(args["output"], "w") as fl:
                                    fl.write(mdata)
        gc.collect()

    def closeFile(self):
        """ the H5 file closing

        :brief: It closes the H5 file
        """
        self.__currentfileid = 0
        if self.__nxRoot:
            self.__nxRoot.currentfileid = self.__currentfileid

        if self.__initPool:
            self.__initPool.close()
            self.__initPool = None

        if self.__stepPool:
            self.__stepPool.close()
            self.__stepPool = None

        if self.__finalPool:
            self.__finalPool.close()
            self.__finalPool = None

        if self.__triggerPools:
            for pool in self.__triggerPools.keys():
                self.__triggerPools[pool].close()
            self.__triggerPools = {}

        if self.__nxRoot:
            self.__nxRoot.close()
        if self.__nxFile:
            self.__nxFile.close()

        if self.addingLogs and self.__logGroup:
            self.__logGroup.close()

        self.__nxPath = []
        self.__nxRoot = None
        self.__nxFile = None
        self.__eFile = None
        self.__logGroup = None
        gc.collect()


if __name__ == "__main__":

    # Create a TDW object
    #: (:class:`TangoDataWriter`) instance of TangoDataWriter
    tdw = TangoDataWriter()
    tdw.fileName = 'test.h5'

    tdw.numberOfThreads = 1

    #: (:obj:`str`) xml file name
    xmlf = "../XMLExamples/MNI.xml"
    #    xmlf = "../XMLExamples/test.xml"

    print("usage: TangoDataWriter.py  <XMLfile1>  "
          "<XMLfile2>  ...  <XMLfileN>  <H5file>")

    #: (:obj:`str`) No arguments
    argc = len(sys.argv)
    if argc > 2:
        tdw.fileName = sys.argv[argc - 1]

    if argc > 1:
        print("opening the H5 file")
        tdw.openFile()

        for i in range(1, argc - 1):
            xmlf = sys.argv[i]

            #: (:obj:`str`) xml string
            with open(xmlf, 'r') as fl:
                xml = fl.read()
            tdw.xmlsettings = xml

            print("opening the data entry ")
            tdw.openEntry()

            print("recording the H5 file")
            tdw.record('{"data": {"emittance_x": 0.8} , '
                       ' "triggers":["trigger1", "trigger2"] }')

            print("sleeping for 1s")
            time.sleep(1)
            print("recording the H5 file")
            tdw.record('{"data": {"emittance_x": 1.2}, '
                       ' "triggers":["trigger2"] }')

            print("sleeping for 1s")
            time.sleep(1)
            print("recording the H5 file")
            tdw.record('{"data": {"emittance_x": 1.1}  , '
                       ' "triggers":["trigger1"] }')

            print("sleeping for 1s")
            time.sleep(1)
            print("recording the H5 file")
            tdw.record('{"data": {"emittance_x": 0.7} }')

            print("closing the data entry ")
            tdw.closeEntry()

        print("closing the H5 file")
        tdw.closeFile()
