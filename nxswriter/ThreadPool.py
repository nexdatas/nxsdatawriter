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

""" Provides a pool with element threads """


from .ElementThread import ElementThread
from .Errors import ThreadError

import queue as Queue


class ThreadPool(object):

    """ Pool with threads
    """

    def __init__(self, numberOfThreads=None, streams=None, maxruntime=0):
        """ constructor

        :brief: It cleans the member variables
        :param numberOfThreads: number of threads
        :type numberOfThreads: :obj:`int`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param maxruntime: maxruntime
        :type maxruntime: :obj:`int`
        """

        #: (:obj:`int`) maximal number of threads
        self.numberOfThreads = numberOfThreads or -1
        #: (:class:`Queue.Queue`) queue of the appended elements
        self.__elementQueue = Queue.Queue()
        #: (:obj:`list` <:class:`nxswriter.Element.Element`>) \
        #:    list of the appended elements
        self.__elementList = []
        #: (:obj:`list` <:class:`nxswriter.ElementThread.ElementThread`>) \
        #:     list of the threads related to the appended elements
        self.__threadList = []

        #: (:class:`StreamSet` or :class:`tango.LatestDeviceImpl`) stream set
        self._streams = streams

        #: (:obj:`float`) maximal runtime
        self.maxRuntime = maxruntime

    def append(self, elem):
        """ appends the thread element

        :param elem: the thread element
        :type elem: :class:`nxswriter.Element.Element`
        """
        self.__elementList.append(elem)

    def setJSON(self, globalJSON, localJSON=None):
        """ sets the JSON string to threads

        :param globalJSON: the static JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>
        :param localJSON: the dynamic JSON string
        :type localJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        :returns: self object
        :rtype: :class:`ThreadPool`
        """

        for el in self.__elementList:
            if hasattr(el.source, "setJSON") and callable(el.source.setJSON):
                el.source.setJSON(globalJSON, localJSON)
        return self

    def run(self):
        """ thread runner

        :brief: It runs the threads from the pool
        """

        self.__threadList = []
        self.__elementQueue = Queue.Queue()

        for eth in self.__elementList:
            self.__elementQueue.put(eth)

        if self.numberOfThreads < 1:
            self.numberOfThreads = len(self.__elementList)

        for i in range(min(self.numberOfThreads, len(self.__elementList))):
            th = ElementThread(i, self.__elementQueue)
            self.__threadList.append(th)
            th.start()

    def join(self, timeout=None):
        """ waits for all thread from the pool

        :param timeout: the maximal waiting time
        :type timeout: :obj:`int`
        """

        for th in self.__threadList:
            if th.is_alive():
                th.join(timeout)

    def runAndWait(self):
        """ runner with waiting

        :brief: It runs and waits the threads from the pool
        """

        self.run()
        self.join()

    def checkErrors(self):
        """ checks errors from threads
        """

        errors = []
        for el in self.__elementList:
            if hasattr(el, "runtime") and \
               el.runtime and self.maxRuntime > 0 \
               and el.runtime > self.maxRuntime:
                path = ""
                if hasattr(el.h5Object, "path"):
                    path = str(el.h5Object.path)
                elif hasattr(el.h5Object, "path"):
                    path = str(el.h5Object.name)
                mess = "ThreadPool::checkErrors() - The maximal " \
                    "element record time (%s s) exceeded: %s s : %s " \
                    % (self.maxRuntime, el.runtime, path)
                if self._streams:
                    self._streams.warn(mess)

            if el.error:
                if isinstance(el.error, tuple):
                    serror = str(tuple([str(e) for e in el.error]))
                else:
                    serror = str(el.error)

                mess = "ThreadPool::checkErrors() - %s" % serror
                if hasattr(el, "canfail") and el.canfail:
                    if hasattr(el, "markFailed"):
                        el.markFailed(serror)
                    if self._streams:
                        self._streams.warn(mess)
                else:
                    errors.append(el.error)
                    if self._streams:
                        self._streams.error(mess, std=False)
        if errors:
            raise ThreadError("Problems in storing data: %s" % str(errors))

    def close(self):
        """ closer

        :brief: It close the threads from the pool
        """

        for el in self.__elementList:
            if hasattr(el.h5Object, "close"):
                el.h5Object.close()
        self.__threadList = []
        self.__elementList = []
        self.__elementQueue = None
