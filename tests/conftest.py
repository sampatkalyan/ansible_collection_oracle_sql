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

