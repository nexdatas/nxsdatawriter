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
# \file DBaseSourceTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time


from nxswriter.DataSources import DataSource
from nxswriter.DBaseSource import DBaseSource
from nxswriter.Errors import DataSourceSetupError

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class DBaseSourceTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        try:
            self.__seed = int(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = int(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)

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

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, None)
        self.assertEqual(ds.dsn, None)
        self.assertEqual(ds.dbtype, None)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, None)

    # __str__ test
    # \brief It tests default settings
    def test_str_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dbtype = "MYSQL"
        dbname = "tango"
        query = "select * from devices;"

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.__str__(), " %s DB %s with %s " % (None, "", None))

        ds = DBaseSource()
        ds.dbtype = dbtype
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), " %s DB %s with %s "
                         % (dbtype, "", None))

        ds = DBaseSource()
        ds.dbtype = dbtype
        ds.dbname = dbname
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), " %s DB %s with %s "
                         % (dbtype, dbname, None))

        ds = DBaseSource()
        ds.dbtype = dbtype
        ds.dbname = dbname
        ds.query = query
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), " %s DB %s with %s "
                         % (dbtype, dbname, query))

    # setup test
    # \brief It tests default settings
    def test_setup_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        dbtype = "MYSQL"
        dbtypeO = "ORACLE"
        # dbtypeP = "PGSQL"
        dbname = "tango"
        query = "select pid from devices;"
        format = "SPECTRUM"
        dsn = "()"
        hostname = 'haso228.desy.de'
        port = '10000'
        mode = 'SYSDBAL'
        user = 'jkotan'
        passwd = 'secret'
        mycnf = '/etc/mysql/my.cnf'

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.setup, "<datasource/>")
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, None)
        self.assertEqual(ds.dsn, None)
        self.assertEqual(ds.dbtype, None)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, None)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><query/></datasource>")
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, '')
        self.assertEqual(ds.dsn, None)
        self.assertEqual(ds.dbtype, None)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, None)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><query format='%s' /></datasource>" % format)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, '')
        self.assertEqual(ds.dsn, None)
        self.assertEqual(ds.dbtype, None)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(
            DataSourceSetupError, ds.setup,
            "<datasource><query>%s</query></datasource>" % query)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, None)
        self.assertEqual(ds.dbtype, None)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, None)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "</datasource>" % (format, query)), None)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, None)
        self.assertEqual(ds.dbtype, None)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbtype='%s'>%s</database></datasource>"
                     % (format, query, dbtypeO, dsn)), None)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, dsn)
        self.assertEqual(ds.dbtype, dbtypeO)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query><database/>"
                     "</datasource>" % (format, query)), None)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, '')
        self.assertEqual(ds.dbtype, None)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbname='%s'/></datasource>"
                     % (format, query, dbname)), None)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, '')
        self.assertEqual(ds.dbtype, None)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, dbname)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbname='%s' dbtype='%s'/></datasource>"
                     % (format, query, dbname, dbtype)), None)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, '')
        self.assertEqual(ds.dbtype, dbtype)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, dbname)
        self.assertEqual(ds.user, None)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbname='%s' dbtype='%s' user='%s'/>"
                     "</datasource>"
                     % (format, query, dbname, dbtype, user)), None)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, '')
        self.assertEqual(ds.dbtype, dbtype)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, dbname)
        self.assertEqual(ds.user, user)
        self.assertEqual(ds.passwd, None)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbname='%s' dbtype='%s' user='%s' "
                     "passwd='%s' hostname='%s'/></datasource>"
                     % (format, query, dbname, dbtype, user, passwd,
                        hostname)), None)
        self.assertEqual(ds.hostname, hostname)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, '')
        self.assertEqual(ds.dbtype, dbtype)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, dbname)
        self.assertEqual(ds.user, user)
        self.assertEqual(ds.passwd, passwd)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbname='%s' dbtype='%s' user='%s' "
                     "passwd='%s' hostname='%s' port='%s'/></datasource>"
                     % (format, query, dbname, dbtype, user, passwd,
                        hostname, port)), None)
        self.assertEqual(ds.hostname, hostname)
        self.assertEqual(ds.port, port)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dsn, '')
        self.assertEqual(ds.dbtype, dbtype)
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.dbname, dbname)
        self.assertEqual(ds.user, user)
        self.assertEqual(ds.passwd, passwd)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')
        self.assertEqual(ds.format, format)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbname='%s' dbtype='%s' user='%s' "
                     "passwd='%s' hostname='%s' port='%s' mycnf='%s'/>"
                     "</datasource>"
                     % (format, query, dbname, dbtype, user, passwd,
                        hostname, port, mycnf)), None)
        self.assertEqual(ds.format, format)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dbname, dbname)
        self.assertEqual(ds.dbtype, dbtype)
        self.assertEqual(ds.hostname, hostname)
        self.assertEqual(ds.port, port)
        self.assertEqual(ds.dsn, '')
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.user, user)
        self.assertEqual(ds.passwd, passwd)
        self.assertEqual(ds.mycnf, mycnf)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbname='%s' dbtype='%s' user='%s' "
                     "passwd='%s' hostname='%s' port='%s' mycnf='%s'/>"
                     "</datasource>"
                     % (format, query, dbname, dbtype,
                        user, passwd, hostname, port, mycnf)), None)
        self.assertEqual(ds.format, format)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dbname, dbname)
        self.assertEqual(ds.dbtype, dbtype)
        self.assertEqual(ds.hostname, hostname)
        self.assertEqual(ds.port, port)
        self.assertEqual(ds.dsn, '')
        self.assertEqual(ds.mode, None)
        self.assertEqual(ds.user, user)
        self.assertEqual(ds.passwd, passwd)
        self.assertEqual(ds.mycnf, mycnf)

        ds = DBaseSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(
            ds.setup("<datasource><query format='%s'>%s</query>"
                     "<database dbtype='%s' user='%s' passwd='%s' "
                     "mode='%s'>%s</database></datasource>"
                     % (format, query, dbtypeO, user, passwd,
                        mode, dsn)), None)
        self.assertEqual(ds.format, format)
        self.assertEqual(ds.query, query)
        self.assertEqual(ds.dbname, None)
        self.assertEqual(ds.dbtype, dbtypeO)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.dsn, dsn)
        self.assertEqual(ds.mode, mode)
        self.assertEqual(ds.user, user)
        self.assertEqual(ds.passwd, passwd)
        self.assertEqual(ds.mycnf, '/etc/my.cnf')


if __name__ == '__main__':
    unittest.main()
