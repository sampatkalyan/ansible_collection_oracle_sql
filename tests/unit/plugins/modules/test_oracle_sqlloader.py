# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from unittest.mock import patch, MagicMock, mock_open
import pytest

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.sampatkalyan.oracle_sql.plugins.modules import oracle_sqlloader


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


def test_sqlloader_missing_required_args():
    set_module_args({})
    with pytest.raises(AnsibleFailJson) as ex:
        oracle_sqlloader.main()
    msg = ex.value.args[0]['msg']
    assert "missing required arguments" in msg or "control_file" in msg


def test_sqlloader_check_mode():
    set_module_args({
        '_ansible_check_mode': True,
        'control_file': '/tmp/test.ctl',
        'data_file': '/tmp/test.dat',
        'log_file': '/tmp/test.log',
        'bad_file': '/tmp/test.bad'
    })
    with pytest.raises(AnsibleExitJson) as result:
        oracle_sqlloader.main()
    assert result.value.args[0]['changed'] is True
    assert 'Check mode' in result.value.args[0]['message']


@patch('os.path.exists', return_value=False)
def test_sqlloader_file_not_found(mock_exists):
    set_module_args({
        'control_file': '/tmp/nonexistent.ctl',
        'data_file': '/tmp/test.dat',
        'log_file': '/tmp/test.log',
        'bad_file': '/tmp/test.bad'
    })
    with pytest.raises(AnsibleFailJson) as result:
        oracle_sqlloader.main()
    assert 'File not found on remote host' in result.value.args[0]['msg']


@patch('os.path.exists', return_value=True)
@patch('subprocess.Popen')
def test_sqlloader_success(mock_popen, mock_exists):
    set_module_args({
        'username': 'system',
        'password': 'password',
        'host': 'localhost',
        'port': 1521,
        'sid': 'ORCL',
        'control_file': '/tmp/test.ctl',
        'data_file': '/tmp/test.dat',
        'log_file': '/tmp/test.log',
        'bad_file': '/tmp/test.bad',
        'direct': True,
        'parallel': True
    })

    log_content = "100 Rows successfully loaded.\n0 Rows not loaded due to data errors."
    mock_proc = MagicMock()
    mock_proc.communicate.return_value = (b'Commit point reached', b'')
    mock_proc.returncode = 0
    mock_popen.return_value = mock_proc

    with patch('builtins.open', mock_open(read_data=log_content)):
        with pytest.raises(AnsibleExitJson) as result:
            oracle_sqlloader.main()

    data = result.value.args[0]
    assert data['changed'] is True
    assert data['rc'] == 0
    assert 'direct=true' in data['cmd']
    assert 'parallel=true' in data['cmd']
    assert data['records_loaded'] == 100
    assert data['records_rejected'] == 0


@patch('os.path.exists', return_value=True)
@patch('subprocess.Popen')
def test_sqlloader_failure(mock_popen, mock_exists):
    set_module_args({
        'connection_string': '@mydb',
        'control_file': '/tmp/test.ctl',
        'data_file': '/tmp/test.dat',
        'log_file': '/tmp/test.log',
        'bad_file': '/tmp/test.bad'
    })

    mock_proc = MagicMock()
    mock_proc.communicate.return_value = (b'', b'SQL*Loader-100: Syntax error')
    mock_proc.returncode = 1
    mock_popen.return_value = mock_proc

    with pytest.raises(AnsibleFailJson) as result:
        oracle_sqlloader.main()

    assert 'SQL*Loader failed' in result.value.args[0]['msg']
    assert result.value.args[0]['rc'] == 1
