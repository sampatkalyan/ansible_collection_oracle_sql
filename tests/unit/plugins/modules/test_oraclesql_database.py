# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import sys
from unittest.mock import patch, MagicMock
import pytest

if 'cx_Oracle' not in sys.modules:
    try:
        __import__('cx_Oracle')
    except ImportError:
        mock_cx = MagicMock()
        mock_cx.DatabaseError = type('DatabaseError', (Exception,), {})
        mock_cx.Error = type('Error', (Exception,), {})
        mock_cx.makedsn = MagicMock(return_value='localhost:1521/ORCL')
        sys.modules['cx_Oracle'] = mock_cx

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.sampatkalyan.oracle_sql.plugins.modules import oraclesql_database


def set_module_args(args):
    payload = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(payload)
    basic._ANSIBLE_PROFILE = 'legacy'


class AnsibleExitJson(SystemExit):
    def __init__(self, kwargs):
        self.args = (kwargs,)
        super().__init__(kwargs)


class AnsibleFailJson(SystemExit):
    def __init__(self, kwargs):
        self.args = (kwargs,)
        super().__init__(kwargs)


def exit_json(*args, **kwargs):
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


@pytest.fixture(autouse=True)
def mock_ansible_module(monkeypatch):
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)


def test_database_missing_required_args():
    set_module_args({})
    with pytest.raises(AnsibleFailJson) as ex:
        oraclesql_database.main()
    msg = ex.value.args[0]['msg']
    assert "missing required arguments" in msg or "db_name" in msg


@patch('cx_Oracle.connect')
def test_create_cdb_database(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'db_name': 'testcdb',
        'state': 'present',
        'db_type': 'CDB',
        'oracle_home': '/u01/app/oracle/product/19.0.0/dbhome_1',
        'oracle_sid': 'testcdb',
        'db_admin_user': 'sys',
        'db_admin_password': 'password'
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_database.main()

    data = result.value.args[0]
    assert data['changed'] is True
    assert data['state'] == 'present'
    assert data['db_type'] == 'CDB'
    mock_cursor.execute.assert_called_with("CREATE DATABASE testcdb ENABLE PLUGGABLE DATABASE")


@patch('cx_Oracle.connect')
def test_create_pdb_database(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'db_name': 'testpdb',
        'state': 'present',
        'db_type': 'PDB',
        'oracle_home': '/u01/app/oracle/product/19.0.0/dbhome_1',
        'oracle_sid': 'testcdb',
        'db_admin_user': 'sys',
        'db_admin_password': 'password'
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_database.main()

    data = result.value.args[0]
    assert data['changed'] is True
    assert data['state'] == 'present'
    assert data['db_type'] == 'PDB'
    mock_cursor.execute.assert_called_with("CREATE PLUGGABLE DATABASE testpdb")


@patch('cx_Oracle.connect')
def test_drop_database(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'db_name': 'testpdb',
        'state': 'absent',
        'db_type': 'PDB',
        'oracle_home': '/u01/app/oracle/product/19.0.0/dbhome_1',
        'oracle_sid': 'testcdb',
        'db_admin_user': 'sys',
        'db_admin_password': 'password'
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_database.main()

    data = result.value.args[0]
    assert data['changed'] is True
    assert data['state'] == 'absent'
    mock_cursor.execute.assert_called_with("DROP PLUGGABLE DATABASE testpdb")


def test_database_fails_when_cx_oracle_missing(monkeypatch):
    monkeypatch.setattr(oraclesql_database, 'HAS_CX_ORACLE', False)
    set_module_args({
        'db_name': 'testcdb',
        'state': 'present',
        'db_type': 'CDB',
        'oracle_home': '/u01/app/oracle/product/19.0.0/dbhome_1',
        'oracle_sid': 'testcdb',
        'db_admin_user': 'sys',
        'db_admin_password': 'password'
    })
    with pytest.raises(AnsibleFailJson) as ex:
        oraclesql_database.main()
    msg = ex.value.args[0]['msg']
    assert "cx_Oracle" in msg
