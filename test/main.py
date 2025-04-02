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
# \file runtest.py
# the unittest runner
#

try:
    try:
        __import__("tango")
    except Exception:
        __import__("PyTango")
    # if module PyTango avalable
    PYTANGO_AVAILABLE = True
except ImportError as e:
    PYTANGO_AVAILABLE = False
    print("PyTango is not available: %s" % e)

try:
    __import__("h5py")
    # if module pni avalable
    H5PY_AVAILABLE = True
except ImportError as e:
    H5PY_AVAILABLE = False
    print("h5py is not available: %s" % e)

try:
    __import__("pninexus.h5cpp")
    # if module pni avalable
    H5CPP_AVAILABLE = True
except ImportError as e:
    H5CPP_AVAILABLE = False
    print("h5cpp is not available: %s" % e)
except SystemError as e:
    H5CPP_AVAILABLE = False
    print("h5cpp is not available: %s" % e)


import os
import sys
import unittest
import Converters_test
import NTP_test
import Errors_test
import DataSource_test
import ClientSource_test
import PyEvalSource_test
import DBaseSource_test
import DataSourcePool_test
import DataSourceFactory_test
import UTF8decoder_test
import UINT32decoder_test
import VDEOdecoder_test
import DecoderPool_test
import DataHolder_test
import ElementThread_test
import ThreadPool_test
import FetchNameHandler_test
import InnerXMLParser_test
import TNObject_test
import StreamSet_test
import Element_test

if not H5PY_AVAILABLE and not H5CPP_AVAILABLE:
    raise Exception("Please install h5py or h5cpp")

if H5PY_AVAILABLE:
    import EDimensionsH5PY_test
    import ElementH5PY_test
    import H5PYWriter_test
    import FElementWithAttrH5PY_test
    import EStrategyH5PY_test
    import EFieldH5PY_test
    import EVirtualFieldH5PY_test
    import EFieldReshapeH5PY_test
    import EGroupH5PY_test
    import EAttributeH5PY_test
    import ELinkH5PY_test
    import EFileH5PY_test
    import EDocH5PY_test
    import NexusXMLHandlerH5PY_test
    import ClientFieldTagWriterH5PY_test
    import XMLFieldTagWriterH5PY_test
    import EDimH5PY_test
    import ESymbolH5PY_test
    import FElementH5PY_test
    import TangoDataWriterH5PY_test
    import FileWriterH5PY_test
    import NXSFromXMLH5PY_test
if H5CPP_AVAILABLE:
    import EDimensionsH5Cpp_test
    import ElementH5Cpp_test
    import H5CppWriter_test
    import FElementWithAttrH5Cpp_test
    import EStrategyH5Cpp_test
    import EFieldH5Cpp_test
    import EVirtualFieldH5Cpp_test
    import EFieldReshapeH5Cpp_test
    import EGroupH5Cpp_test
    import EAttributeH5Cpp_test
    import ELinkH5Cpp_test
    import EFileH5Cpp_test
    import EDocH5Cpp_test
    import NexusXMLHandlerH5Cpp_test
    import ClientFieldTagWriterH5Cpp_test
    import XMLFieldTagWriterH5Cpp_test
    import EDimH5Cpp_test
    import ESymbolH5Cpp_test
    import FElementH5Cpp_test
    import TangoDataWriterH5Cpp_test
    import FileWriterH5Cpp_test
    import NXSFromXMLH5Cpp_test

if H5CPP_AVAILABLE and H5PY_AVAILABLE:
    import FileWriterH5CppH5PY_test
    import TangoDataWriterH5CppH5PY_test

# list of available databases
DB_AVAILABLE = []

try:
    try:
        import MySQLdb
    except Exception:
        import pymysql
        pymysql.install_as_MySQLdb()
    # connection arguments to MYSQL DB
    args = {}
    args["db"] = 'tango'
    # args["host"] = 'localhost'
    args["read_default_file"] = '/etc/my.cnf'
    # inscance of MySQLdb
    mydb = MySQLdb.connect(**args)
    mydb.close()
    DB_AVAILABLE.append("MYSQL")
except Exception:
    try:
        import MySQLdb
        from os.path import expanduser
        home = expanduser("~")
        # connection arguments to MYSQL DB
        args2 = {
            # 'host': u'localhost',
            'db': u'tango',
            'read_default_file': u'%s/.my.cnf' % home,
            'use_unicode': True}
        # inscance of MySQLdb
        mydb = MySQLdb.connect(**args2)
        mydb.close()
        DB_AVAILABLE.append("MYSQL")

    except ImportError as e:
        print("MYSQL not available: %s" % e)
    except Exception as e:
        print("MYSQL not available: %s" % e)
    except Exception:
        print("MYSQL not available")


try:
    import psycopg2
    # connection arguments to PGSQL DB
    args = {}
    args["database"] = 'mydb'
    # inscance of psycog2
    pgdb = psycopg2.connect(**args)
    pgdb.close()
    DB_AVAILABLE.append("PGSQL")
except ImportError as e:
    print("PGSQL not available: %s" % e)
except Exception as e:
    print("PGSQL not available: %s" % e)
except Exception:
    print("PGSQL not available")


try:
    import cx_Oracle
    # pwd
    with open('%s/pwd' % os.path.dirname(Converters_test.__file__)) as fl:
        passwd = fl.read()[:-1]

    # connection arguments to ORACLE DB
    args = {}
    args["dsn"] = "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)" \
                  "(HOST=dbsrv01.desy.de)" \
                  "(PORT=1521))(LOAD_BALANCE=yes)" \
                  "(CONNECT_DATA=(SERVER=DEDICATED)" \
                  "(SERVICE_NAME=desy_db.desy.de)(FAILOVER_MODE=(TYPE=NONE)" \
                  "(METHOD=BASIC)(RETRIES=180)(DELAY=5))))"
    args["user"] = "read"
    args["password"] = passwd
    # inscance of cx_Oracle
    ordb = cx_Oracle.connect(**args)
    ordb.close()
    DB_AVAILABLE.append("ORACLE")
except ImportError as e:
    print("ORACLE not available: %s" % e)
except Exception as e:
    print("ORACLE not available: %s" % e)
except Exception:
    print("ORACLE not available")

if "MYSQL" in DB_AVAILABLE:
    if H5PY_AVAILABLE:
        import DBFieldTagWriterH5PY_test
    if H5CPP_AVAILABLE:
        import DBFieldTagWriterH5Cpp_test
    import MYSQLSource_test

if "PGSQL" in DB_AVAILABLE:
    import PGSQLSource_test

if "ORACLE" in DB_AVAILABLE:
    import ORACLESource_test


if PYTANGO_AVAILABLE:
    import TgDevice_test
    import DataSourceDecoders_test
    import TangoSource_test
    import TgMember_test
    import TgGroup_test
    import ProxyTools_test
    if H5PY_AVAILABLE:
        import TangoFieldTagWriterH5PY_test
        import TangoFieldTagServerH5PY_test
        import ClientFieldTagServerH5PY_test
        import XMLFieldTagServerH5PY_test
        import TangoFieldTagAsynchH5PY_test
        import ClientFieldTagAsynchH5PY_test
        import XMLFieldTagAsynchH5PY_test
        import NXSDataWriterH5PY_test
        import PyEvalTangoSourceH5PY_test
    if H5CPP_AVAILABLE:
        import TangoFieldTagWriterH5Cpp_test
        import TangoFieldTagServerH5Cpp_test
        import ClientFieldTagServerH5Cpp_test
        import XMLFieldTagServerH5Cpp_test
        import TangoFieldTagAsynchH5Cpp_test
        import ClientFieldTagAsynchH5Cpp_test
        import XMLFieldTagAsynchH5Cpp_test
        import NXSDataWriterH5Cpp_test
        import PyEvalTangoSourceH5Cpp_test

    if "MYSQL" in DB_AVAILABLE:
        if H5PY_AVAILABLE:
            import DBFieldTagServerH5PY_test
            import DBFieldTagAsynchH5PY_test
        if H5CPP_AVAILABLE:
            import DBFieldTagServerH5Cpp_test
            import DBFieldTagAsynchH5Cpp_test


#: (:obj:`bool`) tango Bug #213 flag
PYTG_BUG_213 = False
if sys.version_info > (3,):
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


# main function
def main():

    # test suit
    suite = unittest.TestSuite()

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(Element_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(StreamSet_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(Converters_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(NTP_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(Errors_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSource_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ClientSource_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(PyEvalSource_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DBaseSource_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourcePool_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceFactory_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(UTF8decoder_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(UINT32decoder_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(VDEOdecoder_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DecoderPool_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataHolder_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ElementThread_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ThreadPool_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FetchNameHandler_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(InnerXMLParser_test))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(TNObject_test))

    if H5PY_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EDimH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ElementH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(H5PYWriter_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EStrategyH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                FElementWithAttrH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EFieldH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EVirtualFieldH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EFieldReshapeH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EGroupH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ELinkH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EAttributeH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EFileH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EDocH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                NexusXMLHandlerH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                ClientFieldTagWriterH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                XMLFieldTagWriterH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EDimensionsH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ESymbolH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(FElementH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                TangoDataWriterH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                FileWriterH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                NXSFromXMLH5PY_test))

    if H5CPP_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EDimH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ElementH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(H5CppWriter_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EStrategyH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                FElementWithAttrH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EFieldH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EVirtualFieldH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EFieldReshapeH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EGroupH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ELinkH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EAttributeH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EFileH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(EDocH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                NexusXMLHandlerH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                ClientFieldTagWriterH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                XMLFieldTagWriterH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                EDimensionsH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                ESymbolH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                FElementH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                TangoDataWriterH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                FileWriterH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                NXSFromXMLH5Cpp_test))

    if H5CPP_AVAILABLE and H5PY_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                FileWriterH5CppH5PY_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(
                TangoDataWriterH5CppH5PY_test))

    if "MYSQL" in DB_AVAILABLE:
        if H5PY_AVAILABLE:
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    DBFieldTagWriterH5PY_test))
        if H5CPP_AVAILABLE:
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    DBFieldTagWriterH5Cpp_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(MYSQLSource_test))

    if "PGSQL" in DB_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(PGSQLSource_test))

    if "ORACLE" in DB_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ORACLESource_test))

    if PYTANGO_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TgDevice_test))
        if not PYTG_BUG_213:
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    DataSourceDecoders_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoSource_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TgMember_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TgGroup_test))
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ProxyTools_test))

        if H5PY_AVAILABLE:
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    NXSDataWriterH5PY_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    ClientFieldTagServerH5PY_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    XMLFieldTagAsynchH5PY_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    TangoFieldTagWriterH5PY_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    TangoFieldTagServerH5PY_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    TangoFieldTagAsynchH5PY_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    PyEvalTangoSourceH5PY_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    ClientFieldTagAsynchH5PY_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    XMLFieldTagServerH5PY_test))

        if H5CPP_AVAILABLE:
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    NXSDataWriterH5Cpp_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    ClientFieldTagServerH5Cpp_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    XMLFieldTagAsynchH5Cpp_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    TangoFieldTagWriterH5Cpp_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    TangoFieldTagServerH5Cpp_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    TangoFieldTagAsynchH5Cpp_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    PyEvalTangoSourceH5Cpp_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    ClientFieldTagAsynchH5Cpp_test))
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(
                    XMLFieldTagServerH5Cpp_test))

        if "MYSQL" in DB_AVAILABLE:
            if H5PY_AVAILABLE:
                suite.addTests(
                    unittest.defaultTestLoader.loadTestsFromModule(
                        DBFieldTagServerH5PY_test))
                suite.addTests(
                    unittest.defaultTestLoader.loadTestsFromModule(
                        DBFieldTagAsynchH5PY_test))
            if H5CPP_AVAILABLE:
                suite.addTests(
                    unittest.defaultTestLoader.loadTestsFromModule(
                        DBFieldTagServerH5Cpp_test))
                suite.addTests(
                    unittest.defaultTestLoader.loadTestsFromModule(
                        DBFieldTagAsynchH5Cpp_test))

    # test runner
    runner = unittest.TextTestRunner()

    # test result
    result = runner.run(suite).wasSuccessful()
    sys.exit(not result)


if __name__ == "__main__":
    main()
