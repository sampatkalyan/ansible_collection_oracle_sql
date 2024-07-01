import pytest
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
#import ansible.module_utils.oracle_sqlplus as oracle_sqlplus
from unittest.mock import patch, MagicMock
from ansible_collections.andavarapu.oracle_sql.plugins.modules import oracle_sqlplus

def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)

class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass

class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass

def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)

def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)

@pytest.fixture
def mock_module(monkeypatch):
    monkeypatch.setattr(basic, "AnsibleModule", MagicMock())
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)

def test_module_fail_when_required_args_missing(mock_module):
    with pytest.raises(AnsibleFailJson) as ex:
        set_module_args({})
        oracle_sqlplus.main()
    assert "Either 'script', 'raw_sql', or 'loop' must be specified" in str(ex.value)

@patch('subprocess.Popen')
def test_execute_sqlplus_script(mock_popen, mock_module):
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
    
    assert result.value.args[0]['changed'] == True
    assert 'SQL execution successful' in result.value.args[0]['sqlplus_output']

@patch('subprocess.Popen')
def test_execute_sqlplus_raw_sql(mock_popen, mock_module):
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
    
    assert result.value.args[0]['changed'] == True
    assert '1 row selected' in result.value.args[0]['sqlplus_output']

@patch('subprocess.Popen')
def test_execute_sqlplus_with_substitution_variables(mock_popen, mock_module):
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
    
    assert result.value.args[0]['changed'] == True
    assert 'Substitution variables applied' in result.value.args[0]['sqlplus_output']

@patch('subprocess.Popen')
def test_execute_sqlplus_with_bind_variables(mock_popen, mock_module):
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
    
    assert result.value.args[0]['changed'] == True
    assert 'Bind variables applied' in result.value.args[0]['sqlplus_output']

@patch('subprocess.Popen')
def test_execute_sqlplus_with_sysdba(mock_popen, mock_module):
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
    
    assert result.value.args[0]['changed'] == True
    assert 'Connected as SYSDBA' in result.value.args[0]['sqlplus_output']

@patch('subprocess.Popen')
def test_execute_sqlplus_failure(mock_popen, mock_module):
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
    
    assert 'SQL*Plus execution failed' in str(result.value)
    assert 'ORA-12345: Test error' in str(result.value)

@patch('subprocess.Popen')
def test_execute_sqlplus_loop(mock_popen, mock_module):
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
    
    assert result.value.args[0]['changed'] == True
    assert 'Script 1 executed' in result.value.args[0]['sqlplus_output']
    assert 'Raw SQL executed' in result.value.args[0]['sqlplus_output']