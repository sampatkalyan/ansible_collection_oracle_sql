# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

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
from ansible_collections.sampatkalyan.oracle_sql.plugins.modules import oraclesql_table


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


def test_table_missing_required_args():
    set_module_args({})
    with pytest.raises(AnsibleFailJson) as ex:
        oraclesql_table.main()
    msg = ex.value.args[0]['msg']
    assert "missing required arguments" in msg or "table_name" in msg


@patch('cx_Oracle.makedsn', return_value='localhost:1521/ORCL')
@patch('cx_Oracle.connect')
def test_create_table_when_not_exists(mock_connect, mock_makedsn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # table_exists query returns None (table does not exist)
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'hostname': 'localhost',
        'port': 1521,
        'service_name': 'ORCL',
        'user': 'system',
        'password': 'password',
        'table_name': 'employees',
        'state': 'present',
        'columns': [
            {'name': 'id', 'type': 'NUMBER', 'primary_key': True},
            {'name': 'name', 'type': 'VARCHAR2(100)', 'nullable': False}
        ]
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_table.main()

    data = result.value.args[0]
    assert data['changed'] is True
    assert data['table']['table_name'] == 'employees'
    mock_conn.commit.assert_called_once()


@patch('cx_Oracle.makedsn', return_value='localhost:1521/ORCL')
@patch('cx_Oracle.connect')
def test_drop_table_when_exists(mock_connect, mock_makedsn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # table_exists returns a row (table exists)
    mock_cursor.fetchone.return_value = ('EMPLOYEES',)
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'hostname': 'localhost',
        'port': 1521,
        'service_name': 'ORCL',
        'user': 'system',
        'password': 'password',
        'table_name': 'employees',
        'state': 'absent'
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_table.main()

    data = result.value.args[0]
    assert data['changed'] is True
    mock_cursor.execute.assert_any_call("DROP TABLE employees PURGE")


@patch('cx_Oracle.makedsn', return_value='localhost:1521/ORCL')
@patch('cx_Oracle.connect')
def test_modify_nonexistent_table_fails(mock_connect, mock_makedsn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # table_exists returns None (table does not exist)
    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'hostname': 'localhost',
        'port': 1521,
        'service_name': 'ORCL',
        'user': 'system',
        'password': 'password',
        'table_name': 'nonexistent_table',
        'state': 'modified'
    })

    with pytest.raises(AnsibleFailJson) as result:
        oraclesql_table.main()

    assert "Table nonexistent_table does not exist" in result.value.args[0]['msg']


def test_table_fails_when_cx_oracle_missing(monkeypatch):
    monkeypatch.setattr(oraclesql_table, 'HAS_CX_ORACLE', False)
    set_module_args({
        'hostname': 'localhost',
        'port': 1521,
        'service_name': 'ORCL',
        'user': 'system',
        'password': 'password',
        'table_name': 'users',
        'state': 'present'
    })
    with pytest.raises(AnsibleFailJson) as ex:
        oraclesql_table.main()
    msg = ex.value.args[0]['msg']
    assert "cx_Oracle" in msg


