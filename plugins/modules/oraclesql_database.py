#!/usr/bin/python
# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import cx_Oracle

DOCUMENTATION = '''
---
module: oracle_sql.sampatkalyan.oraclesql_database
short_description: Manage Oracle databases (CDB and PDB).
description:
    - Manage Oracle databases including creating and dropping both Container Databases (CDB) and Pluggable Databases (PDB).
version_added: "0.0.1"
options:
    db_name:
        description:
            - Name of the Oracle database.
        required: true
    state:
        description:
            - State of the database (`present` or `absent`).
        choices: ['present', 'absent']
        required: true
    db_type:
        description:
            - Type of the database (`CDB` or `PDB`).
        choices: ['CDB', 'PDB']
        required: true
    oracle_home:
        description:
            - Path to the Oracle Home directory.
        required: true
    oracle_sid:
        description:
            - Oracle System Identifier (SID) for the database.
        required: true
    db_admin_user:
        description:
            - Administrative user for database operations.
        required: true
    db_admin_password:
        description:
            - Password for the administrative user.
        required: true
        no_log: true
requirements:
    - cx_Oracle
author:
    - Andavarapu Sampat Kalyan (@sampatkalyan)
'''

EXAMPLES = '''
# Create a CDB Oracle database
- name: Create a CDB Oracle database
  oracle_sql.sampatkalyan.oraclesql_database:
    db_name: cdbtest
    state: present
    db_type: CDB
    oracle_home: /u01/app/oracle/product/19.0.0/dbhome_1
    oracle_sid: cdbtest
    db_admin_user: sys
    db_admin_password: Oracle_123

# Drop a PDB Oracle database
- name: Drop a PDB Oracle database
  oracle_sql.sampatkalyan.oraclesql_database::
    db_name: pdbtest
    state: absent
    db_type: PDB
    oracle_home: /u01/app/oracle/product/19.0.0/dbhome_1
    oracle_sid: cdbtest
    db_admin_user: sys
    db_admin_password: Oracle_123
'''

RETURN = '''
changed:
    description: Whether the state of the database was changed.
    type: bool
msg:
    description: Message describing the result of the operation.
    type: str
db_name:
    description: Name of the Oracle database affected by the operation.
    type: str
state:
    description: State of the database after the operation ('present' or 'absent').
    type: str
db_type:
    description: Type of the database affected (CDB or PDB).
    type: str
'''

def run_sql_command(module, conn_str, sql_commands):
    try:
        with cx_Oracle.connect(conn_str) as connection:
            with connection.cursor() as cursor:
                for sql in sql_commands:
                    cursor.execute(sql)
            connection.commit()
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        module.fail_json(msg=error.message, code=error.code)

def create_database(module, db_type, db_name, oracle_home, oracle_sid, db_admin_user, db_admin_password):
    if db_type == 'CDB':
        sql_commands = [f"CREATE DATABASE {db_name} ENABLE PLUGGABLE DATABASE"]
    elif db_type == 'PDB':
        sql_commands = [f"CREATE PLUGGABLE DATABASE {db_name}"]
    
    conn_str = f"{db_admin_user}/{db_admin_password}@{oracle_sid}"
    run_sql_command(module, conn_str, sql_commands)
    module.exit_json(changed=True, msg=f"{db_type} {db_name} created.", db_name=db_name, state='present', db_type=db_type)

def drop_database(module, db_type, db_name, oracle_home, oracle_sid, db_admin_user, db_admin_password):
    if db_type == 'CDB':
        sql_commands = [f"DROP DATABASE {db_name}"]
    elif db_type == 'PDB':
        sql_commands = [f"DROP PLUGGABLE DATABASE {db_name}"]
    
    conn_str = f"{db_admin_user}/{db_admin_password}@{oracle_sid}"
    run_sql_command(module, conn_str, sql_commands)
    module.exit_json(changed=True, msg=f"{db_type} {db_name} dropped.", db_name=db_name, state='absent', db_type=db_type)

def main():
    module_args = dict(
        db_name=dict(type='str', required=True),
        state=dict(type='str', required=True, choices=['present', 'absent']),
        db_type=dict(type='str', required=True, choices=['CDB', 'PDB']),
        oracle_home=dict(type='str', required=True),
        oracle_sid=dict(type='str', required=True),
        db_admin_user=dict(type='str', required=True),
        db_admin_password=dict(type='str', required=True, no_log=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        documentation=DOCUMENTATION,
        examples=EXAMPLES
    )

    db_name = module.params['db_name']
    state = module.params['state']
    db_type = module.params['db_type']
    oracle_home = module.params['oracle_home']
    oracle_sid = module.params['oracle_sid']
    db_admin_user = module.params['db_admin_user']
    db_admin_password = module.params['db_admin_password']

    if state == 'present':
        create_database(module, db_type, db_name, oracle_home, oracle_sid, db_admin_user, db_admin_password)
    elif state == 'absent':
        drop_database(module, db_type, db_name, oracle_home, oracle_sid, db_admin_user, db_admin_password)

if __name__ == '__main__':
    main()
