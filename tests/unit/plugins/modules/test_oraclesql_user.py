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
from ansible_collections.sampatkalyan.oracle_sql.plugins.modules import oraclesql_user


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


def test_user_missing_required_args():
    set_module_args({})
    with pytest.raises(AnsibleFailJson) as ex:
        oraclesql_user.main()
    msg = ex.value.args[0]['msg']
    assert "missing required arguments" in msg or "username" in msg


@patch('cx_Oracle.connect')
def test_create_user_not_existing(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (0,)  # user count = 0
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'connect_string': 'sys/password@localhost:1521/ORCL',
        'username': 'app_user',
        'password': 'secret_password',
        'state': 'present',
        'privileges': ['CREATE SESSION', 'CREATE TABLE']
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_user.main()

    data = result.value.args[0]
    assert data['changed'] is True
    assert "User 'app_user' created successfully" in data['msg']


@patch('cx_Oracle.connect')
def test_update_existing_user(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)  # user count = 1
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'connect_string': 'sys/password@localhost:1521/ORCL',
        'username': 'app_user',
        'password': 'new_password',
        'state': 'present',
        'privileges': ['CREATE SESSION']
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_user.main()

    data = result.value.args[0]
    assert data['changed'] is False
    assert "User 'app_user' exists and updated" in data['msg']


@patch('cx_Oracle.connect')
def test_drop_existing_user(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)  # user exists
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'connect_string': 'sys/password@localhost:1521/ORCL',
        'username': 'app_user',
        'password': 'dummy_password',
        'state': 'absent'
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_user.main()

    data = result.value.args[0]
    assert data['changed'] is True
    assert "User 'app_user' deleted successfully" in data['msg']


@patch('cx_Oracle.connect')
def test_drop_nonexistent_user(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (0,)  # user doesn't exist
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    set_module_args({
        'connect_string': 'sys/password@localhost:1521/ORCL',
        'username': 'app_user',
        'password': 'dummy_password',
        'state': 'absent'
    })

    with pytest.raises(AnsibleExitJson) as result:
        oraclesql_user.main()

    data = result.value.args[0]
    assert data['changed'] is False
    assert "User 'app_user' does not exist" in data['msg']


def test_user_fails_when_cx_oracle_missing(monkeypatch):
    monkeypatch.setattr(oraclesql_user, 'HAS_CX_ORACLE', False)
    set_module_args({
        'connect_string': 'sys/password@localhost:1521/ORCL',
        'username': 'app_user',
        'password': 'dummy_password',
        'state': 'present'
    })
    with pytest.raises(AnsibleFailJson) as ex:
        oraclesql_user.main()
    msg = ex.value.args[0]['msg']
    assert "cx_Oracle" in msg
