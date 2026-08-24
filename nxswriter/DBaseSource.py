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

""" Definitions of DB datasource """

import xml.etree.ElementTree as et
from lxml.etree import XMLParser
import sys

from .Types import NTP

from .DataSources import DataSource
from .Errors import (PackageError, DataSourceSetupError)


#: (:obj:`list<str>`) list of available databases
DB_AVAILABLE = []

try:
    try:
        import MySQLdb
    except Exception:
        import pymysql as MySQLdb
        MySQLdb.install_as_MySQLdb()
    DB_AVAILABLE.append("MYSQL")
except ImportError:
    pass
    # sys.stdout.write("MYSQL not available: %s\n" % e)
    # sys.stdout.flush()

try:
    import psycopg2
    DB_AVAILABLE.append("PGSQL")
except ImportError:
    pass
    # sys.stdout.write("PGSQL not available: %s\n" % e)
    # sys.stdout.flush()

try:
    import cx_Oracle
    DB_AVAILABLE.append("ORACLE")
except ImportError:
    pass
    # sys.stdout.write("ORACLE not available: %s\n" % e)
    # sys.stdout.flush()


class DBaseSource(DataSource):

    """ DataBase data source
    """

    def __init__(self, streams=None, name=None):
        """ constructor

        :brief: It sets all member variables to None
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`tango.LatestDeviceImpl`
        :param name: datasource name
        :type name: :obj:`str`
        """
        DataSource.__init__(self, streams=streams, name=name)
        #: (:obj:`str`) name of the host with the data source
        self.hostname = None
        #: (:obj:`str`) port related to the host
        self.port = None
        #: (:obj:`str`) database query
        self.query = None
        #: (:obj:`str`) DSN string
        self.dsn = None
        #: (:obj:`str`) database type, i.e. MYSQL, PGSQL, ORACLE
        self.dbtype = None
        #: (:obj:`str`) oracle database mode
        self.mode = None
        #: (:obj:`str`) database name
        self.dbname = None
        #: (:obj:`str`) database user
        self.user = None
        #: (:obj:`str`) database password
        self.passwd = None
        #: (:obj:`str`) mysql database configuration file
        self.mycnf = '/etc/my.cnf'
        #: (:obj:`str`) record format, i.e. `SCALAR`, `SPECTRUM`, `IMAGE`
        self.format = None

        #: (:obj:`dict` <:obj:`str`, :obj:`instancemethod`>) map
        self.__dbConnect = {"MYSQL": self.__connectMYSQL,
                            "PGSQL": self.__connectPGSQL,
                            "ORACLE": self.__connectORACLE}

    def __str__(self):
        """ self-description

        :returns: self-describing string
        :rtype: :obj:`str`
        """
        return " %s DB %s with %s " % (
            self.dbtype, self.dbname if self.dbname else "", self.query)

    def setup(self, xml):
        """ sets the parrameters up from xml

        :param xml: datasource parameters
        :type xml: :obj:`str`
        :raises: :exc:`nxswriter.Errors.DataSourceSetupError`
            if :obj:`format` or :obj:`query` is not defined
        """
        if sys.version_info > (3,):
            xml = bytes(xml, "UTF-8")
        root = et.fromstring(xml, parser=XMLParser(collect_ids=False))
        query = root.find("query")
        if query is not None:
            self.format = query.get("format")
            self.query = self._getText(query)

        if not self.format or not self.query:
            if self._streams:
                self._streams.error(
                    "DBaseSource::setup() - "
                    "Database query or its format not defined: %s" % xml,
                    std=False)

            raise DataSourceSetupError(
                "Database query or its format not defined: %s" % xml)

        db = root.find("database")
        if db is not None:
            self.dbname = db.get("dbname")
            self.dbtype = db.get("dbtype")
            self.user = db.get("user")
            self.passwd = db.get("passwd")
            self.mode = db.get("mode")
            mycnf = db.get("mycnf")
            if mycnf:
                self.mycnf = mycnf
            self.hostname = db.get("hostname")
            self.port = db.get("port")
            self.dsn = self._getText(db)

    def __connectMYSQL(self):
        """ connects to MYSQL database

        :returns: open database object
        :rtype: :class:`MySQLdb.connections.Connection`
        """
        args = {}
        if self.mycnf:
            args["read_default_file"] = self.mycnf
        if self.dbname:
            args["db"] = self.dbname
        if self.user:
            args["user"] = self.user
        if self.passwd:
            args["passwd"] = self.passwd
        if self.hostname:
            args["host"] = self.hostname
        if sys.version_info < (3,):
            for k in list(args.keys()):
                args[k] = args[k].encode()

        if self.port:
            args["port"] = int(self.port)
        return MySQLdb.connect(**args)

    def __connectPGSQL(self):
        """ connects to PGSQL database

        :returns: open database object
        :rtype: :class:`psycopg2._psycopg.connection`
        """
        args = {}

        if self.dbname:
            args["database"] = self.dbname
        if self.user:
            args["user"] = self.user
        if self.passwd:
            args["password"] = self.passwd
        if self.hostname:
            args["host"] = self.hostname
        if sys.version_info < (3,):
            for k in list(args.keys()):
                args[k] = args[k].encode()

        if self.port:
            args["port"] = int(self.port)

        return psycopg2.connect(**args)

    def __connectORACLE(self):
        """ connects to ORACLE database

        :returns: open database object
        :rtype: :class:`cx_Oracle.Connection`
        """
        args = {}
        if self.user:
            args["user"] = self.user
        if self.passwd:
            args["password"] = self.passwd
        if self.dsn:
            args["dsn"] = self.dsn
        if self.mode:
            args["mode"] = self.mode
        if sys.version_info < (3,):
            for k in list(args.keys()):
                args[k] = args[k].encode()

        return cx_Oracle.connect(**args)

    def getData(self):
        """ provides access to the data

        :returns: dictionary with collected data
        :rtype: :obj:`dict` <:obj:`str`, any>
        """

        db = None

        if self.dbtype in self.__dbConnect.keys() \
                and self.dbtype in DB_AVAILABLE:
            db = self.__dbConnect[self.dbtype]()
        else:
            if self._streams:
                self._streams.error(
                    "DBaseSource::getData() - "
                    "Support for %s database not available" % self.dbtype,
                    std=False)

            raise PackageError(
                "Support for %s database not available" % self.dbtype)

        if db:
            cursor = db.cursor()
            cursor.execute(self.query)
            if not self.format or self.format == 'SCALAR':
                #  data = copy.deepcopy(cursor.fetchone())
                data = cursor.fetchone()
                dh = {"rank": "SCALAR",
                      "value": data[0],
                      "tangoDType": (NTP.pTt[type(data[0]).__name__]),
                      "shape": [1, 0]}
            elif self.format == 'SPECTRUM':
                data = cursor.fetchall()
                # data = copy.deepcopy(cursor.fetchall())
                if len(data[0]) == 1:
                    ldata = list(el[0] for el in data)
                else:
                    ldata = list(el for el in data[0])
                dh = {"rank": "SPECTRUM",
                      "value": ldata,
                      "tangoDType": (NTP.pTt[type(ldata[0]).__name__]),
                      "shape": [len(ldata), 0]}
            else:
                data = cursor.fetchall()
                # data = copy.deepcopy(cursor.fetchall())
                ldata = list(list(el) for el in data)
                dh = {"rank": "IMAGE",
                      "value": ldata,
                      "tangoDType": NTP.pTt[type(ldata[0][0]).__name__],
                      "shape": [len(ldata), len(ldata[0])]}
            cursor.close()
            db.close()
        return dh
