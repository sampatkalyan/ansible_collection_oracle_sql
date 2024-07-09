#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: oracle_sqlloader
short_description: Load data into Oracle database using SQL*Loader
description:
    - This module uses Oracle SQL*Loader to load data from a file into an Oracle database.
    - It provides various options to control the SQL*Loader operation.
version_added: "1.0.0"
author:
    - "Your Name (@yourgithubhandle)"
options:
    username:
        description:
            - The Oracle database username.
        required: false
        type: str
    password:
        description:
            - The Oracle database password.
        required: false
        type: str
    sid:
        description:
            - The Oracle database SID.
        required: false
        type: str
    host:
        description:
            - The Oracle database host.
        required: false
        type: str
    port:
        description:
            - The Oracle database port.
        required: false
        type: int
    connection_string:
        description:
            - Full Oracle connection string. If provided, it overrides username, password, host, port, and sid.
        required: false
        type: str
    wallet_location:
        description:
            - Location of Oracle Wallet if using Wallet authentication.
        required: false
        type: str
    wallet_password:
        description:
            - Password for Oracle Wallet if required.
        required: false
        type: str
    control_file:
        description:
            - The path to the SQL*Loader control file on the remote host.
        required: true
        type: str
    data_file:
        description:
            - The path to the data file to be loaded on the remote host.
        required: true
        type: str
    log_file:
        description:
            - The path where the log file should be created on the remote host.
        required: true
        type: str
    bad_file:
        description:
            - The path where the bad file should be created on the remote host.
        required: true
        type: str
    direct:
        description:
            - Use direct path load.
        type: bool
        default: false
    parallel:
        description:
            - Use parallel load.
        type: bool
        default: false
    skip:
        description:
            - Number of records to skip before loading.
        type: int
    load:
        description:
            - Number of records to load.
        type: int
    silent:
        description:
            - Control SQL*Loader feedback.
        type: str
        choices: ['ALL', 'ERRORS', 'FEEDBACK', 'HEADER']
    errors:
        description:
            - Maximum number of errors to allow.
        required: false
        type: int
    rows:
        description:
            - Number of rows to read from the input file.
        required: false
        type: int
    bindsize:
        description:
            - Maximum size (in bytes) of the bind array.
        required: false
        type: str
    readsize:
        description:
            - Size (in bytes) of the read buffer.
        required: false
        type: str
    external_table:
        description:
            - Use external table for loading.
        required: false
        type: str
        choices: ['NOT_USED', 'GENERATE_ONLY', 'EXECUTE']
    columnarrayrows:
        description:
            - Number of rows to allocate for column arrays.
        required: false
        type: int
    parfile:
        description:
            - Specify a parameter file to use.
        required: false
        type: str
    scratch_dir:
        description:
            - Specify a scratch directory for SQL*Loader to use.
        required: false
        type: str
    discard_file:
        description:
            - Specify a discard file.
        required: false
        type: str
    charset:
        description:
            - Character set for SQL*Loader.
        required: false
        type: str
requirements:
    - python >= 2.7
    - cx_Oracle
notes:
    - Requires Oracle SQL*Loader to be installed on the target machine.
    - The user running this module must have appropriate permissions to execute SQL*Loader.
    - All file paths should be on the remote host where SQL*Loader will be executed.
'''

EXAMPLES = r'''
- name: Load data into Oracle database
  oracle_sqlloader:
    username: system
    password: oracle
    sid: ORCL
    host: localhost
    port: 1521
    control_file: /path/on/remote/host/control.ctl
    data_file: /path/on/remote/host/data.csv
    log_file: /path/on/remote/host/load.log
    bad_file: /path/on/remote/host/bad.bad
    direct: true
    parallel: false
    skip: 10
    load: 1000
    silent: 'ERRORS'

- name: Load data using wallet authentication
  oracle_sqlloader:
    connection_string: '@mydb'
    wallet_location: /path/to/wallet
    wallet_password: walletpass
    control_file: /path/on/remote/host/control.ctl
    data_file: /path/on/remote/host/data.csv
    log_file: /path/on/remote/host/load.log
    bad_file: /path/on/remote/host/bad.bad
    external_table: 'EXECUTE'
    charset: 'WE8MSWIN1252'
'''

RETURN = r'''
changed:
    description: Indicates if the database was modified
    type: bool
    returned: always
message:
    description: Informational message about the operation
    type: str
    returned: always
stdout:
    description: Standard output of the SQL*Loader command
    type: str
    returned: always
stderr:
    description: Standard error of the SQL*Loader command
    type: str
    returned: always
records_loaded:
    description: Number of records successfully loaded
    type: int
    returned: on success
records_rejected:
    description: Number of records rejected due to data errors
    type: int
    returned: on success
rc:
    description: Return code of the SQL*Loader command
    type: int
    returned: always
cmd:
    description: The command used to run SQL*Loader
    type: str
    returned: always
'''

import os
import re
import subprocess

from ansible.module_utils.basic import AnsibleModule

def run_sqlloader(module, cmd):
    """
    Run the SQL*Loader command and return the results.
    """
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            module.fail_json(msg="SQL*Loader failed", rc=proc.returncode, stdout=stdout, stderr=stderr, cmd=' '.join(cmd))
        return stdout, stderr, proc.returncode
    except Exception as e:
        module.fail_json(msg=str(e), cmd=' '.join(cmd))

def parse_log_file(log_file):
    """
    Parse the SQL*Loader log file to extract relevant information.
    """
    records_loaded = 0
    records_rejected = 0
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            content = f.read()
            loaded_match = re.search(r'(\d+) Rows successfully loaded', content)
            if loaded_match:
                records_loaded = int(loaded_match.group(1))
            rejected_match = re.search(r'(\d+) Rows not loaded due to data errors', content)
            if rejected_match:
                records_rejected = int(rejected_match.group(1))
    
    return records_loaded, records_rejected

def main():
    module_args = dict(
        username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        sid=dict(type='str', required=False),
        host=dict(type='str', required=False),
        port=dict(type='int', required=False),
        connection_string=dict(type='str', required=False),
        wallet_location=dict(type='str', required=False),
        wallet_password=dict(type='str', required=False, no_log=True),
        control_file=dict(type='str', required=True),
        data_file=dict(type='str', required=True),
        log_file=dict(type='str', required=True),
        bad_file=dict(type='str', required=True),
        direct=dict(type='bool', default=False),
        parallel=dict(type='bool', default=False),
        skip=dict(type='int'),
        load=dict(type='int'),
        silent=dict(type='str', choices=['ALL', 'ERRORS', 'FEEDBACK', 'HEADER']),
        errors=dict(type='int'),
        rows=dict(type='int'),
        bindsize=dict(type='str'),
        readsize=dict(type='str'),
        external_table=dict(type='str', choices=['NOT_USED', 'GENERATE_ONLY', 'EXECUTE']),
        columnarrayrows=dict(type='int'),
        parfile=dict(type='str'),
        scratch_dir=dict(type='str'),
        discard_file=dict(type='str'),
        charset=dict(type='str'),
    )

    result = dict(
        changed=False,
        message='',
        stdout='',
        stderr='',
        rc=0,
        cmd='',
        records_loaded=0,
        records_rejected=0
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        result['changed'] = True
        result['message'] = 'Check mode: SQL*Loader operation would be performed'
        module.exit_json(**result)

    # Check if files exist on remote host
    for file_param in ['control_file', 'data_file']:
        if not os.path.exists(module.params[file_param]):
            module.fail_json(msg=f"File not found on remote host: {module.params[file_param]}")

    # Check if directories for log and bad files exist
    for file_param in ['log_file', 'bad_file']:
        directory = os.path.dirname(module.params[file_param])
        if not os.path.exists(directory):
            module.fail_json(msg=f"Directory not found on remote host for {file_param}: {directory}")

    if module.params['connection_string']:
        conn = module.params['connection_string']
    else:
        conn = f"{module.params['username']}/{module.params['password']}@{module.params['host']}:{module.params['port']}/{module.params['sid']}"

    cmd = [
        'sqlldr',
        f'userid={conn}',
        f'control={module.params["control_file"]}',
        f'data={module.params["data_file"]}',
        f'log={module.params["log_file"]}',
        f'bad={module.params["bad_file"]}'
    ]

    if module.params['wallet_location']:
        cmd.append(f"wallet_location={module.params['wallet_location']}")
    if module.params['wallet_password']:
        cmd.append(f"wallet_password={module.params['wallet_password']}")
    if module.params['direct']:
        cmd.append('direct=true')
    if module.params['parallel']:
        cmd.append('parallel=true')
    if module.params['skip']:
        cmd.append(f'skip={module.params["skip"]}')
    if module.params['load']:
        cmd.append(f'load={module.params["load"]}')
    if module.params['silent']:
        cmd.append(f'silent={module.params["silent"]}')
    if module.params['errors']:
        cmd.append(f'errors={module.params["errors"]}')
    if module.params['rows']:
        cmd.append(f'rows={module.params["rows"]}')
    if module.params['bindsize']:
        cmd.append(f'bindsize={module.params["bindsize"]}')
    if module.params['readsize']:
        cmd.append(f'readsize={module.params["readsize"]}')
    if module.params['external_table']:
        cmd.append(f'external_table={module.params["external_table"]}')
    if module.params['columnarrayrows']:
        cmd.append(f'columnarrayrows={module.params["columnarrayrows"]}')
    if module.params['parfile']:
        cmd.append(f'parfile={module.params["parfile"]}')
    if module.params['scratch_dir']:
        cmd.append(f'scratch_dir={module.params["scratch_dir"]}')
    if module.params['discard_file']:
        cmd.append(f'discard={module.params["discard_file"]}')
    if module.params['charset']:
        cmd.append(f'charset={module.params["charset"]}')

    result['cmd'] = ' '.join(cmd)

    stdout, stderr, rc = run_sqlloader(module, cmd)
    
    result['changed'] = True
    result['message'] = 'SQL*Loader executed successfully'
    result['stdout'] = stdout
    result['stderr'] = stderr
    result['rc'] = rc

    records_loaded, records_rejected = parse_log_file(module.params['log_file'])
    result['records_loaded'] = records_loaded
    result['records_rejected'] = records_rejected

    module.exit_json(**result)

if __name__ == '__main__':
    main()