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

""" Implementation of element thread for tag evaluation """

from threading import Thread
import time

import queue as Queue


class ElementThread(Thread):

    """ single thread element

    """

    def __init__(self, index, queue):
        """ constructor

        :brief: It creates ElementThread from the runnable element
        :param index: the current thread index
        :type index: :obj:`int`
        :param queue: queue with tasks
        :type queue: :class:`Queue.Queue`
        """
        Thread.__init__(self)
        #: (:obj:`int`) thread index
        self.index = index
        #: (:class:`Queue.Queue`) queue with runnable elements
        self.__queue = queue

    def run(self):
        """ runner

        :brief: It runs the defined thread
        """
        full = True
        while full:
            try:
                elem = self.__queue.get(block=False)
                if hasattr(elem, "run") and callable(elem.run):
                    elem.error = None
                    elem.runtime = 0
                    st = time.time()
                    elem.run()
                    elem.runtime = time.time() - st

            except Queue.Empty:
                full = False
