import sys
from unittest.mock import MagicMock

# Windows compatibility shims for POSIX modules required by ansible.module_utils.basic
for mod_name in ['grp', 'pwd', 'fcntl', 'termios']:
    if mod_name not in sys.modules:
        try:
            __import__(mod_name)
        except ImportError:
            mock_mod = MagicMock()
            sys.modules[mod_name] = mock_mod

# Fallback cx_Oracle mock for test environments lacking Oracle client
if 'cx_Oracle' not in sys.modules:
    try:
        __import__('cx_Oracle')
    except ImportError:
        mock_cx = MagicMock()
        mock_cx.DatabaseError = type('DatabaseError', (Exception,), {})
        mock_cx.Error = type('Error', (Exception,), {})
        mock_cx.makedsn = MagicMock(return_value='localhost:1521/ORCL')
        sys.modules['cx_Oracle'] = mock_cx
