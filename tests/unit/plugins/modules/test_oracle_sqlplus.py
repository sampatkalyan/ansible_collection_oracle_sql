# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from unittest.mock import patch, MagicMock, mock_open
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.sampatkalyan.oracle_sql.plugins.modules import oracle_sqlplus


def set_module_args(args):
    """Prepare arguments so that they will be picked up during module creation."""
    payload = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(payload)
    basic._ANSIBLE_PROFILE = 'legacy'


class AnsibleExitJson(SystemExit):
    """Exception raised by exit_json and caught by unit tests."""
    def __init__(self, kwargs):
        self.args = (kwargs,)
        super().__init__(kwargs)


class AnsibleFailJson(SystemExit):
    """Exception raised by fail_json and caught by unit tests."""
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
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        yield


def test_module_fail_when_required_args_missing():
    set_module_args({})
    with pytest.raises(AnsibleFailJson) as ex:
        oracle_sqlplus.main()
    assert "Either 'script', 'raw_sql', or 'loop' must be specified" in ex.value.args[0]['msg']


@patch('builtins.open', mock_open(read_data="SELECT 1 FROM DUAL;"))
@patch('os.path.exists', return_value=True)
@patch('subprocess.Popen')
def test_execute_sqlplus_script(mock_popen, mock_exists):
    set_module_args({
        'script': '/path/to/test.sql',
        'username': 'testuser',
        'password': 'testpass',
        'database': 'testdb'
    })

    mock_process = MagicMock()
    mock_process.communicate.return_value = (b'SQL execution successful', b'')
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    with pytest.raises(AnsibleExitJson) as result:
        oracle_sqlplus.main()

    assert result.value.args[0]['changed'] is True
    assert 'SQL execution successful' in result.value.args[0]['sqlplus_output']


@patch('subprocess.Popen')
def test_execute_sqlplus_raw_sql(mock_popen):
    set_module_args({
        'raw_sql': 'SELECT * FROM test_table',
        'username': 'testuser',
        'password': 'testpass',
        'database': 'testdb'
    })

    mock_process = MagicMock()
    mock_process.communicate.return_value = (b'1 row selected', b'')
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    with pytest.raises(AnsibleExitJson) as result:
        oracle_sqlplus.main()

    assert result.value.args[0]['changed'] is True
    assert '1 row selected' in result.value.args[0]['sqlplus_output']


@patch('builtins.open', mock_open(read_data="SELECT 1;"))
@patch('os.path.exists', return_value=True)
@patch('subprocess.Popen')
def test_execute_sqlplus_with_substitution_variables(mock_popen, mock_exists):
    set_module_args({
        'script': '/path/to/test.sql',
        'username': 'testuser',
        'password': 'testpass',
        'database': 'testdb',
        'substitution_variables': ['var1', 'var2']
    })

    mock_process = MagicMock()
    mock_process.communicate.return_value = (b'Substitution variables applied', b'')
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    with pytest.raises(AnsibleExitJson) as result:
        oracle_sqlplus.main()

    assert result.value.args[0]['changed'] is True
    assert 'Substitution variables applied' in result.value.args[0]['sqlplus_output']


@patch('subprocess.Popen')
def test_execute_sqlplus_with_bind_variables(mock_popen):
    set_module_args({
        'raw_sql': 'SELECT * FROM test_table WHERE id = :id',
        'username': 'testuser',
        'password': 'testpass',
        'database': 'testdb',
        'bind_variables': {'id': '1'}
    })

    mock_process = MagicMock()
    mock_process.communicate.return_value = (b'Bind variables applied', b'')
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    with pytest.raises(AnsibleExitJson) as result:
        oracle_sqlplus.main()

    assert result.value.args[0]['changed'] is True
    assert 'Bind variables applied' in result.value.args[0]['sqlplus_output']


@patch('builtins.open', mock_open(read_data="SELECT 1;"))
@patch('os.path.exists', return_value=True)
@patch('subprocess.Popen')
def test_execute_sqlplus_with_sysdba(mock_popen, mock_exists):
    set_module_args({
        'script': '/path/to/test.sql',
        'sysdba': True
    })

    mock_process = MagicMock()
    mock_process.communicate.return_value = (b'Connected as SYSDBA', b'')
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    with pytest.raises(AnsibleExitJson) as result:
        oracle_sqlplus.main()

    assert result.value.args[0]['changed'] is True
    assert 'Connected as SYSDBA' in result.value.args[0]['sqlplus_output']


@patch('builtins.open', mock_open(read_data="SELECT 1;"))
@patch('os.path.exists', return_value=True)
@patch('subprocess.Popen')
def test_execute_sqlplus_failure(mock_popen, mock_exists):
    set_module_args({
        'script': '/path/to/test.sql',
        'username': 'testuser',
        'password': 'testpass',
        'database': 'testdb'
    })

    mock_process = MagicMock()
    mock_process.communicate.return_value = (b'', b'ORA-12345: Test error')
    mock_process.returncode = 1
    mock_popen.return_value = mock_process

    with pytest.raises(AnsibleFailJson) as result:
        oracle_sqlplus.main()

    assert 'ORA-12345: Test error' in result.value.args[0]['msg']


@patch('builtins.open', mock_open(read_data="SELECT 1;"))
@patch('os.path.exists', return_value=True)
@patch('subprocess.Popen')
def test_execute_sqlplus_loop(mock_popen, mock_exists):
    set_module_args({
        'loop': [
            {'script': '/path/to/script1.sql'},
            {'raw_sql': 'SELECT * FROM table2'}
        ],
        'username': 'testuser',
        'password': 'testpass',
        'database': 'testdb'
    })

    mock_process = MagicMock()
    mock_process.communicate.side_effect = [
        (b'Script 1 executed', b''),
        (b'Raw SQL executed', b'')
    ]
    mock_process.returncode = 0
    mock_popen.return_value = mock_process

    with pytest.raises(AnsibleExitJson) as result:
        oracle_sqlplus.main()

    assert result.value.args[0]['changed'] is True
    # In a loop execution, sqlplus_output holds the output of the final executed statement
    assert 'Raw SQL executed' in result.value.args[0]['sqlplus_output']
