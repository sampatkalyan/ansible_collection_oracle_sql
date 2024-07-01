#!/usr/bin/python

# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

from ansible.module_utils.basic import AnsibleModule
import os
import subprocess
import logging
import re
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DOCUMENTATION = '''
---
module: oracle_sqlplus
short_description: Executes Oracle SQL*Plus scripts or raw SQL
description:
    - This module allows you to execute Oracle SQL*Plus scripts or raw SQL.
    - Supports substitution variables and environment variables.
    - Bind variables are supported only for raw SQL execution.
version_added: "2.9"
options:
    username:
        description:
            - The username to connect to the Oracle database.
        required: false
        type: str
    password:
        description:
            - The password to connect to the Oracle database.
        required: false
        type: str
        no_log: true
    database:
        description:
            - The database connect string.
        required: false
        type: str
    script:
        description:
            - The path to the SQL*Plus script to be executed.
        required: false
        type: path
    raw_sql:
        description:
            - The raw SQL query to be executed.
        required: false
        type: str
    substitution_variables:
        description:
            - A list of substitution variables to replace in the SQL script or raw SQL.
        required: false
        type: list
        elements: str
        default: []
    bind_variables:
        description:
            - A dictionary representing bind variables for raw SQL execution.
        required: false
        type: dict
        default: {}
    env_variables:
        description:
            - A dictionary of environment variables to set for SQL*Plus execution.
        required: false
        type: dict
        default: {}
    sysdba:
        description:
            - Connect as SYSDBA.
        required: false
        type: bool
        default: false
    sysoper:
        description:
            - Connect as SYSOPER.
        required: false
        type: bool
        default: false
    silent:
        description:
            - Run SQL*Plus in silent mode.
        required: false
        type: bool
        default: false
    nolog:
        description:
            - Start SQL*Plus without logging in.
        required: false
        type: bool
        default: false
    suppress_login:
        description:
            - Suppress the login banner.
        required: false
        type: bool
        default: false
    markup_mode:
        description:
            - Set markup mode (HTML or XML).
        required: false
        type: str
        choices: ['HTML', 'XML']
    loop:
        description:
            - A list of dictionaries containing SQL files or raw SQL to be executed in a loop.
        required: false
        type: list
        elements: dict
        default: []
    restrict:
        description:
            - Restrict SQL*Plus commands.
        required: false
        type: bool
        default: false
    page_size:
        description:
            - Number of rows to fetch at a time for large result sets.
        required: false
        type: int
        default: 1000
notes:
    - This module has been tested with Oracle 11g, 12c, and 19c.
    - It is strongly recommended to use Ansible Vault for sensitive information like passwords.
requirements:
    - Python 3.6+
    - Oracle Instant Client (sqlplus)
author:
    - Andavarapu Sampat Kalyan (@sampatkalyan)
'''

EXAMPLES = '''
# Execute a SQL*Plus script with substitution variables
- name: Run SQL*Plus script with substitution variables
  oracle_sqlplus:
    script: "/path/to/sqlfile.sql"
    substitution_variables:
      - "value1"
      - "value2"
    env_variables:
      NLS_LANG: "AMERICAN_AMERICA.AL32UTF8"

# Execute raw SQL with bind variables using SQL*Plus
- name: Run raw SQL with bind variables
  oracle_sqlplus:
    raw_sql: "SELECT * FROM mytable WHERE column_name = :myVar"
    bind_variables:
      myVar: "value"
    env_variables:
      NLS_LANG: "AMERICAN_AMERICA.AL32UTF8"

# Execute multiple SQL*Plus scripts and raw SQL in a loop
- name: Run SQL*Plus scripts and raw SQL in a loop
  oracle_sqlplus:
    loop:
      - script: "/path/to/sqlfile1.sql"
        substitution_variables:
          - "value1"
          - "value2"
        env_variables:
          NLS_LANG: "AMERICAN_AMERICA.AL32UTF8"
      - raw_sql: "SELECT * FROM mytable WHERE column_name = :myVar"
        bind_variables:
          myVar: "value"
'''

RETURN = '''
changed:
    description: Indicates whether any changes were made.
    type: bool
    returned: always
original_message:
    description: The original message passed to the module.
    type: str
    returned: always
message:
    description: The output message from the module.
    type: str
    returned: always
sqlplus_output:
    description: The output from sqlplus if sqlplus option is enabled.
    type: str
    returned: always
execution_time:
    description: The time taken for SQL execution.
    type: float
    returned: always
results:
    description: The results of the executed SQL statements.
    type: list
    returned: always
    elements: dict
    contains:
        statement:
            description: The SQL statement that was executed.
            type: str
            returned: always
        output:
            description: The output or result of the SQL statement.
            type: str
            returned: always
        rows_affected:
            description: Number of rows affected by the SQL statement.
            type: int
            returned: for DML statements
'''

def validate_input(module):
    """Validate input parameters."""
    if not module.params['script'] and not module.params['raw_sql'] and not module.params['loop']:
        module.fail_json(msg="Either 'script', 'raw_sql', or 'loop' must be specified")
    if module.params['script'] and module.params['raw_sql']:
        module.fail_json(msg="Specify either 'script' or 'raw_sql', not both")
    if module.params['script'] and not os.path.exists(module.params['script']):
        module.fail_json(msg=f"SQL file {module.params['script']} not found")

def execute_sqlplus(module, result):
    """Execute SQL*Plus command."""
    username = module.params['username']
    password = module.params['password']
    database = module.params['database']
    script = module.params['script']
    raw_sql = module.params['raw_sql']
    substitution_variables = module.params['substitution_variables']
    bind_variables = module.params['bind_variables']
    env_variables = module.params['env_variables']
    sysdba = module.params['sysdba']
    sysoper = module.params['sysoper']
    silent = module.params['silent']
    nolog = module.params['nolog']
    suppress_login = module.params['suppress_login']
    markup_mode = module.params['markup_mode']
    restrict = module.params['restrict']
    page_size = module.params['page_size']

    if script:
        with open(script, 'r') as file:
            sql_script = file.read()
    else:
        sql_script = raw_sql

    # Replace substitution variables
    for i, value in enumerate(substitution_variables, start=1):
        subst_var = f'&{i}'
        sql_script = sql_script.replace(subst_var, str(value))

    # Handle bind variables for raw SQL
    if raw_sql and bind_variables:
        for var, value in bind_variables.items():
            sql_script = sql_script.replace(f":{var}", f"'{value}'")

    # Construct SQL*Plus command
    sqlplus_cmd = ['sqlplus']
    if silent:
        sqlplus_cmd.append('-S')
    if nolog:
        sqlplus_cmd.append('/NOLOG')
    if suppress_login:
        sqlplus_cmd.append('-s')
    if markup_mode:
        sqlplus_cmd.extend(['-M', markup_mode])
    if restrict:
        sqlplus_cmd.append('-R')

    if username and password and database:
        conn_str = f"{username}/{password}@{database}"
    else:
        conn_str = '/ as sysdba' if sysdba else '/ as sysoper' if sysoper else ''

    sqlplus_cmd.append(conn_str)

    # Prepare environment variables
    env = os.environ.copy()
    env.update(env_variables)


    # Execute SQL script using SQL*Plus
    start_time = datetime.now()
    process = subprocess.Popen(sqlplus_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate(input=sql_script.encode())
    end_time = datetime.now()

    if process.returncode != 0:
        module.fail_json(msg=f"SQL*Plus execution failed: {stderr.decode('utf-8').strip()}")

    result['sqlplus_output'] = stdout.decode('utf-8').strip()
    result['execution_time'] = (end_time - start_time).total_seconds()
    result['changed'] = True

    # Parse output for more detailed results
    result['results'].extend(parse_sqlplus_output(result['sqlplus_output'], page_size))

def parse_sqlplus_output(output, page_size):
    """Parse SQL*Plus output for more structured results."""
    results = []
    current_statement = ""
    current_output = []
    rows_affected = 0

    for line in output.split('\n'):
        if line.strip().upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE", "MERGE")):
            if current_statement:
                results.append({
                    'statement': current_statement,
                    'output': '\n'.join(current_output),
                    'rows_affected': rows_affected
                })
            current_statement = line
            current_output = []
            rows_affected = 0
        elif "rows selected" in line.lower() or "rows affected" in line.lower():
            match = re.search(r'(\d+) rows', line)
            if match:
                rows_affected = int(match.group(1))
        else:
            current_output.append(line)

        if len(current_output) >= page_size:
            results.append({
                'statement': current_statement,
                'output': '\n'.join(current_output[:page_size]),
                'rows_affected': rows_affected
            })
            current_output = current_output[page_size:]

    if current_statement:
        results.append({
            'statement': current_statement,
            'output': '\n'.join(current_output),
            'rows_affected': rows_affected
        })

    return results

def run_module():
    module_args = dict(
        username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        database=dict(type='str', required=False),
        script=dict(type='path', required=False),
        raw_sql=dict(type='str', required=False),
        substitution_variables=dict(type='list', elements='str', required=False, default=[]),
        bind_variables=dict(type='dict', required=False, default={}),
        env_variables=dict(type='dict', required=False, default={}),
        sysdba=dict(type='bool', required=False, default=False),
        sysoper=dict(type='bool', required=False, default=False),
        silent=dict(type='bool', required=False, default=False),
        nolog=dict(type='bool', required=False, default=False),
        suppress_login=dict(type='bool', required=False, default=False),
        markup_mode=dict(type='str', required=False, choices=['HTML', 'XML']),
        loop=dict(type='list', elements='dict', required=False, default=[]),
        restrict=dict(type='bool', required=False, default=False),
        page_size=dict(type='int', required=False, default=1000)
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        sqlplus_output='',
        execution_time=0,
        results=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        validate_input(module)
        
        if module.params['loop']:
            for item in module.params['loop']:
                temp_params = module.params.copy()
                temp_params.update(item)
                temp_module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
                temp_module.params = temp_params
                execute_sqlplus(temp_module, result)
        else:
            execute_sqlplus(module, result)

        result['message'] = 'SQL execution completed successfully'
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.error(error_message)
        module.fail_json(msg=error_message, **result)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()