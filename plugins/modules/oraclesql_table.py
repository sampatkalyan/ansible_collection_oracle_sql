#!/usr/bin/python
# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Your Name <youremail@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sampatkalyan.oracle_sql.oraclesql_table
short_description: Manage Oracle database tables
description:
    - Create, modify, or drop tables in an Oracle database.
    - Manage indexes, constraints, partitions, and other table properties.
    - This module is part of the oracle_sql collection (oracle_sql.sampatkalyan).
version_added: "0.0.1"
options:
    hostname:
        description: The Oracle database host.
        required: true
        type: str
    port:
        description: The Oracle database port.
        required: true
        type: int
    service_name:
        description: The Oracle database service name.
        required: true
        type: str
    user:
        description: The username to connect to the database.
        required: true
        type: str
    password:
        description: The password for the database user.
        required: true
        type: str
    table_name:
        description: The name of the table to manage.
        required: true
        type: str
    state:
        description: The desired state of the table.
        choices: ['present', 'absent', 'modified']
        default: present
        type: str
    columns:
        description: A list of column definitions for the table.
        type: list
        elements: dict
        suboptions:
            name:
                description: The name of the column.
                required: true
                type: str
            type:
                description: The data type of the column.
                required: true
                type: str
            primary_key:
                description: Whether this column is a primary key.
                type: bool
                default: false
            nullable:
                description: Whether this column can contain NULL values.
                type: bool
                default: true
            unique:
                description: Whether this column must contain unique values.
                type: bool
                default: false
            default:
                description: The default value for the column.
                type: str
            check:
                description: A check constraint for the column.
                type: str
            comment:
                description: A comment for the column.
                type: str
    indexes:
        description: A list of index definitions for the table.
        type: list
        elements: dict
        suboptions:
            name:
                description: The name of the index.
                required: true
                type: str
            columns:
                description: The columns to include in the index.
                type: list
                elements: str
                required: true
            unique:
                description: Whether the index is unique.
                type: bool
                default: false
            type:
                description: The type of index.
                choices: ['BTREE', 'BITMAP']
                default: 'BTREE'
                type: str
    foreign_keys:
        description: A list of foreign key constraints for the table.
        type: list
        elements: dict
        suboptions:
            name:
                description: The name of the foreign key constraint.
                required: true
                type: str
            columns:
                description: The columns in this table for the foreign key.
                type: list
                elements: str
                required: true
            reference_table:
                description: The table being referenced by the foreign key.
                required: true
                type: str
            reference_columns:
                description: The columns in the referenced table.
                type: list
                elements: str
                required: true
            on_delete:
                description: The action to take when the referenced row is deleted.
                choices: ['CASCADE', 'SET NULL', 'NO ACTION', 'RESTRICT']
                default: 'NO ACTION'
                type: str
    partitioning:
        description: Partitioning information for the table.
        type: dict
        suboptions:
            type:
                description: The type of partitioning.
                choices: ['RANGE', 'LIST', 'HASH']
                required: true
                type: str
            columns:
                description: The columns used for partitioning.
                type: list
                elements: str
                required: true
            partitions:
                description: The partition definitions.
                type: list
                elements: dict
    tablespace:
        description: The tablespace in which to create the table.
        type: str
    temporary:
        description: Whether this is a temporary table.
        type: bool
        default: false
    parallel:
        description: The degree of parallelism for the table.
        type: int
    compress:
        description: Whether to enable table compression.
        type: bool
        default: false
    row_movement:
        description: Whether to enable row movement for partitioned tables.
        type: bool
        default: false
    gather_stats:
        description: Whether to gather statistics after table creation or modification.
        type: bool
        default: false
    comment:
        description: A comment for the table.
        type: str
requirements:
    - cx_Oracle
author:
    - Andavarapu Sampat Kalyan (@sampatkalyan)
'''

EXAMPLES = r'''
- name: Create users table with advanced features
  oracle_sql.sampatkalyan.oraclesql_table:
    hostname: localhost
    port: 1521
    service_name: ORCLCDB
    user: system
    password: oracle
    table_name: users
    state: present
    columns:
      - name: id
        type: NUMBER
        primary_key: true
      - name: username
        type: VARCHAR2(50)
        nullable: false
        unique: true
      - name: email
        type: VARCHAR2(100)
        unique: true
      - name: created_at
        type: DATE
        default: "SYSDATE"
      - name: status
        type: VARCHAR2(20)
        check: "status IN ('active', 'inactive', 'suspended')"
    indexes:
      - name: idx_users_email
        columns: [email]
        unique: true
    foreign_keys:
      - name: fk_users_roles
        columns: [role_id]
        reference_table: roles
        reference_columns: [id]
        on_delete: CASCADE
    partitioning:
      type: RANGE
      columns: [created_at]
      partitions:
        - name: users_2023
          value_less_than: "TO_DATE('2024-01-01', 'YYYY-MM-DD')"
        - name: users_2024
          value_less_than: "TO_DATE('2025-01-01', 'YYYY-MM-DD')"
    tablespace: users_data
    parallel: 4
    compress: true
    row_movement: true
    gather_stats: true
    comment: "Table for storing user information"

- name: Drop users table
  oracle_sql.sampatkalyan.oraclesql_table:
    hostname: localhost
    port: 1521
    service_name: ORCLCDB
    user: system
    password: oracle
    table_name: users
    state: absent
'''

RETURN = r'''
table:
    description: Information about the managed table
    type: dict
    returned: always
    sample: {
        "name": "users",
        "state": "present",
        "columns": [
            {"name": "id", "type": "NUMBER", "primary_key": true},
            {"name": "username", "type": "VARCHAR2(50)", "nullable": false, "unique": true},
            {"name": "email", "type": "VARCHAR2(100)", "unique": true},
            {"name": "created_at", "type": "DATE", "default": "SYSDATE"},
            {"name": "status", "type": "VARCHAR2(20)", "check": "status IN ('active', 'inactive', 'suspended')"}
        ],
        "indexes": [
            {"name": "idx_users_email", "columns": ["email"], "unique": true}
        ],
        "foreign_keys": [
            {"name": "fk_users_roles", "columns": ["role_id"], "reference_table": "roles", "reference_columns": ["id"], "on_delete": "CASCADE"}
        ],
        "partitioning": {
            "type": "RANGE",
            "columns": ["created_at"],
            "partitions": [
                {"name": "users_2023", "value_less_than": "TO_DATE('2024-01-01', 'YYYY-MM-DD')"},
                {"name": "users_2024", "value_less_than": "TO_DATE('2025-01-01', 'YYYY-MM-DD')"}
            ]
        },
        "tablespace": "users_data",
        "parallel": 4,
        "compress": true,
        "row_movement": true,
        "comment": "Table for storing user information"
    }
'''

import cx_Oracle
from ansible.module_utils.basic import AnsibleModule

def create_table(cursor, table_info):
    columns = []
    for col in table_info['columns']:
        col_def = f"{col['name']} {col['type']}"
        if not col.get('nullable', True):
            col_def += " NOT NULL"
        if col.get('default'):
            col_def += f" DEFAULT {col['default']}"
        if col.get('check'):
            col_def += f" CHECK ({col['check']})"
        columns.append(col_def)
    
    primary_key = next((col['name'] for col in table_info['columns'] if col.get('primary_key')), None)
    if primary_key:
        columns.append(f"CONSTRAINT pk_{table_info['name']} PRIMARY KEY ({primary_key})")
    
    query = f"CREATE {'TEMPORARY ' if table_info.get('temporary') else ''}TABLE {table_info['name']} ({', '.join(columns)})"
    
    if table_info.get('tablespace'):
        query += f" TABLESPACE {table_info['tablespace']}"
    if table_info.get('partitioning'):
        part_info = table_info['partitioning']
        query += f" PARTITION BY {part_info['type']}({', '.join(part_info['columns'])}) ("
        partitions = []
        for part in part_info['partitions']:
            if part_info['type'] == 'RANGE':
                partitions.append(f"PARTITION {part['name']} VALUES LESS THAN ({part['value_less_than']})")
            elif part_info['type'] == 'LIST':
                partitions.append(f"PARTITION {part['name']} VALUES ({', '.join(part['values'])})")
            elif part_info['type'] == 'HASH':
                partitions.append(f"PARTITION {part['name']}")
        query += ', '.join(partitions) + ")"
    if table_info.get('compress'):
        query += " COMPRESS"
    if table_info.get('parallel'):
        query += f" PARALLEL {table_info['parallel']}"
    if table_info.get('row_movement'):
        query += " ENABLE ROW MOVEMENT"
    
    cursor.execute(query)
    
    for col in table_info['columns']:
        if col.get('comment'):
            cursor.execute(f"COMMENT ON COLUMN {table_info['name']}.{col['name']} IS '{col['comment']}'")
    
    if table_info.get('comment'):
        cursor.execute(f"COMMENT ON TABLE {table_info['name']} IS '{table_info['comment']}'")

def drop_table(cursor, table_name):
    cursor.execute(f"DROP TABLE {table_name} PURGE")

def table_exists(cursor, table_name):
    query = "SELECT table_name FROM user_tables WHERE table_name = :name"
    cursor.execute(query, name=table_name.upper())
    return cursor.fetchone() is not None

def get_existing_columns(cursor, table_name):
    query = """
    SELECT column_name, data_type, data_length, nullable, data_precision, data_scale, data_default, comments
    FROM user_tab_columns
    LEFT JOIN user_col_comments USING (table_name, column_name)
    WHERE table_name = :name
    """
    cursor.execute(query, name=table_name.upper())
    return {row[0]: {
        'type': f"{row[1]}({row[2]})" if row[1] in ('VARCHAR2', 'CHAR') else (
            f"{row[1]}({row[4]},{row[5]})" if row[1] == 'NUMBER' and row[4] is not None else row[1]
        ),
        'nullable': row[3] == 'Y',
        'default': row[6],
        'comment': row[7]
    } for row in cursor.fetchall()}

def get_existing_constraints(cursor, table_name):
    query = """
    SELECT constraint_name, constraint_type, column_name, search_condition, r_constraint_name
    FROM user_constraints
    JOIN user_cons_columns USING (constraint_name, table_name)
    WHERE table_name = :name
    """
    cursor.execute(query, name=table_name.upper())
    return {row[0]: {
        'type': 'PRIMARY KEY' if row[1] == 'P' else ('UNIQUE' if row[1] == 'U' else ('CHECK' if row[1] == 'C' else 'FOREIGN KEY')),
        'column': row[2],
        'condition': row[3],
        'reference': row[4]
    } for row in cursor.fetchall()}

def get_existing_indexes(cursor, table_name):
    query = """
    SELECT index_name, index_type, uniqueness, column_name
    FROM user_indexes
    JOIN user_ind_columns USING (index_name, table_name)
    WHERE table_name = :name
    """
    cursor.execute(query, name=table_name.upper())
    indexes = {}
    for row in cursor.fetchall():
        if row[0] not in indexes:
            indexes[row[0]] = {
                'type': 'BITMAP' if row[1] == 'BITMAP' else 'BTREE',
                'unique': row[2] == 'UNIQUE',
                'columns': []
            }
        indexes[row[0]]['columns'].append(row[3])
    return indexes

def modify_table(cursor, table_name, desired_state):
    existing_columns = get_existing_columns(cursor, table_name)
    existing_constraints = get_existing_constraints(cursor, table_name)
    existing_indexes = get_existing_indexes(cursor, table_name)
    
    # Modify columns
    for col in desired_state['columns']:
        if col['name'] not in existing_columns:
            query = f"ALTER TABLE {table_name} ADD {col['name']} {col['type']}"
            if not col.get('nullable', True):
                query += " NOT NULL"
            if col.get('default'):
                query += f" DEFAULT {col['default']}"
            cursor.execute(query)
        else:
            existing_col = existing_columns[col['name']]
            if existing_col['type'] != col['type'] or existing_col['nullable'] != col.get('nullable', True):
                nullable_str = "NULL" if col.get('nullable', True) else "NOT NULL"
                cursor.execute(f"ALTER TABLE {table_name} MODIFY {col['name']} {col['type']} {nullable_str}")
            if existing_col['default'] != col.get('default'):
                if col.get('default'):
                    cursor.execute(f"ALTER TABLE {table_name} MODIFY {col['name']} DEFAULT {col['default']}")
                else:
                    cursor.execute(f"ALTER TABLE {table_name} MODIFY {col['name']} DEFAULT NULL")
            if existing_col['comment'] != col.get('comment'):
                cursor.execute(f"COMMENT ON COLUMN {table_name}.{col['name']} IS '{col.get('comment', '')}'")
    
    # Remove columns that are not in the desired state
    for col_name in existing_columns:
        if col_name not in [col['name'] for col in desired_state['columns']]:
            cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {col_name}")

    # Manage constraints
    desired_constraints = {f"pk_{table_name}": {'type': 'PRIMARY KEY', 'column': next((col['name'] for col in desired_state['columns'] if col.get('primary_key')), None)}}
    for col in desired_state['columns']:
        if col.get('unique'):
            desired_constraints[f"uk_{table_name}_{col['name']}"] = {'type': 'UNIQUE', 'column': col['name']}
        if col.get('check'):
            desired_constraints[f"ck_{table_name}_{col['name']}"] = {'type': 'CHECK', 'column': col['name'], 'condition': col['check']}

    for constraint in existing_constraints.values():
        if constraint['type'] in ['PRIMARY KEY', 'UNIQUE', 'CHECK']:
            if constraint['column'] not in [col['name'] for col in desired_state['columns']] or \
               constraint['type'] not in [c['type'] for c in desired_constraints.values()] or \
               (constraint['type'] == 'CHECK' and constraint['condition'] != next((c['condition'] for c in desired_constraints.values() if c['type'] == 'CHECK' and c['column'] == constraint['column']), None)):
                cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {constraint['name']}")

    for constraint_name, constraint in desired_constraints.items():
        if constraint['column'] and constraint_name not in existing_constraints:
            if constraint['type'] == 'PRIMARY KEY':
                cursor.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} PRIMARY KEY ({constraint['column']})")
            elif constraint['type'] == 'UNIQUE':
                cursor.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} UNIQUE ({constraint['column']})")
            elif constraint['type'] == 'CHECK':
                cursor.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} CHECK ({constraint['condition']})")

    # Manage indexes
    for index in desired_state.get('indexes', []):
        if index['name'] not in existing_indexes:
            unique = "UNIQUE " if index.get('unique') else ""
            index_type = f"BITMAP " if index.get('type') == 'BITMAP' else ""
            columns = ", ".join(index['columns'])
            cursor.execute(f"CREATE {unique}{index_type}INDEX {index['name']} ON {table_name} ({columns})")
        else:
            existing_index = existing_indexes[index['name']]
            if existing_index['unique'] != index.get('unique', False) or \
               existing_index['type'] != index.get('type', 'BTREE') or \
               existing_index['columns'] != index['columns']:
                cursor.execute(f"DROP INDEX {index['name']}")
                unique = "UNIQUE " if index.get('unique') else ""
                index_type = f"BITMAP " if index.get('type') == 'BITMAP' else ""
                columns = ", ".join(index['columns'])
                cursor.execute(f"CREATE {unique}{index_type}INDEX {index['name']} ON {table_name} ({columns})")

    for index_name in existing_indexes:
        if index_name not in [idx['name'] for idx in desired_state.get('indexes', [])]:
            cursor.execute(f"DROP INDEX {index_name}")

    # Manage foreign keys
    for fk in desired_state.get('foreign_keys', []):
        fk_name = fk['name']
        if fk_name not in existing_constraints:
            columns = ", ".join(fk['columns'])
            ref_columns = ", ".join(fk['reference_columns'])
            on_delete = f" ON DELETE {fk['on_delete']}" if fk.get('on_delete') else ""
            cursor.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {fk_name} FOREIGN KEY ({columns}) "
                           f"REFERENCES {fk['reference_table']} ({ref_columns}){on_delete}")
        else:
            # For simplicity, we're dropping and recreating foreign keys if they exist
            # A more sophisticated approach would compare the existing and desired states
            cursor.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT {fk_name}")
            columns = ", ".join(fk['columns'])
            ref_columns = ", ".join(fk['reference_columns'])
            on_delete = f" ON DELETE {fk['on_delete']}" if fk.get('on_delete') else ""
            cursor.execute(f"ALTER TABLE {table_name} ADD CONSTRAINT {fk_name} FOREIGN KEY ({columns}) "
                           f"REFERENCES {fk['reference_table']} ({ref_columns}){on_delete}")

    # Update table properties
    if desired_state.get('tablespace'):
        cursor.execute(f"ALTER TABLE {table_name} MOVE TABLESPACE {desired_state['tablespace']}")
    if desired_state.get('parallel'):
        cursor.execute(f"ALTER TABLE {table_name} PARALLEL {desired_state['parallel']}")
    if desired_state.get('compress') is not None:
        cursor.execute(f"ALTER TABLE {table_name} {'COMPRESS' if desired_state['compress'] else 'NOCOMPRESS'}")
    if desired_state.get('row_movement') is not None:
        cursor.execute(f"ALTER TABLE {table_name} {'ENABLE' if desired_state['row_movement'] else 'DISABLE'} ROW MOVEMENT")
    
    # Update table comment
    if desired_state.get('comment'):
        cursor.execute(f"COMMENT ON TABLE {table_name} IS '{desired_state['comment']}'")

    # Note: Modifying partitioning scheme is complex and often requires recreating the table
    # This implementation doesn't handle partition modifications for existing tables

def gather_table_stats(cursor, table_name):
    cursor.execute(f"BEGIN DBMS_STATS.GATHER_TABLE_STATS(ownname => USER, tabname => '{table_name}'); END;")

def run_module():
    module_args = dict(
        hostname=dict(type='str', required=True),
        port=dict(type='int', required=True),
        service_name=dict(type='str', required=True),
        user=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        table_name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent', 'modified']),
        columns=dict(type='list', elements='dict', options=dict(
            name=dict(type='str', required=True),
            type=dict(type='str', required=True),
            primary_key=dict(type='bool', default=False),
            nullable=dict(type='bool', default=True),
            unique=dict(type='bool', default=False),
            default=dict(type='str'),
            check=dict(type='str'),
            comment=dict(type='str')
        )),
        indexes=dict(type='list', elements='dict', options=dict(
            name=dict(type='str', required=True),
            columns=dict(type='list', elements='str', required=True),
            unique=dict(type='bool', default=False),
            type=dict(type='str', choices=['BTREE', 'BITMAP'], default='BTREE')
        )),
        foreign_keys=dict(type='list', elements='dict', options=dict(
            name=dict(type='str', required=True),
            columns=dict(type='list', elements='str', required=True),
            reference_table=dict(type='str', required=True),
            reference_columns=dict(type='list', elements='str', required=True),
            on_delete=dict(type='str', choices=['CASCADE', 'SET NULL', 'NO ACTION', 'RESTRICT'], default='NO ACTION')
        )),
        partitioning=dict(type='dict', options=dict(
            type=dict(type='str', choices=['RANGE', 'LIST', 'HASH'], required=True),
            columns=dict(type='list', elements='str', required=True),
            partitions=dict(type='list', elements='dict')
        )),
        tablespace=dict(type='str'),
        temporary=dict(type='bool', default=False),
        parallel=dict(type='int'),
        compress=dict(type='bool'),
        row_movement=dict(type='bool'),
        gather_stats=dict(type='bool', default=False),
        comment=dict(type='str')
    )

    result = dict(
        changed=False,
        table=dict()
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    hostname = module.params['hostname']
    port = module.params['port']
    service_name = module.params['service_name']
    user = module.params['user']
    password = module.params['password']
    table_name = module.params['table_name']
    state = module.params['state']

    try:
        dsn = cx_Oracle.makedsn(hostname, port, service_name=service_name)
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        cursor = connection.cursor()

        if state == 'present':
            if not table_exists(cursor, table_name):
                if not module.check_mode:
                    create_table(cursor, module.params)
                result['changed'] = True
            else:
                if not module.check_mode:
                    modify_table(cursor, table_name, module.params)
                result['changed'] = True
        elif state == 'absent':
            if table_exists(cursor, table_name):
                if not module.check_mode:
                    drop_table(cursor, table_name)
                result['changed'] = True
        elif state == 'modified':
            if table_exists(cursor, table_name):
                if not module.check_mode:
                    modify_table(cursor, table_name, module.params)
                result['changed'] = True
            else:
                module.fail_json(msg=f"Table {table_name} does not exist", **result)

        if not module.check_mode:
            connection.commit()
            if module.params['gather_stats']:
                gather_table_stats(cursor, table_name)

        result['table'] = module.params

    except cx_Oracle.Error as error:
        module.fail_json(msg=str(error), **result)

    finally:
        if 'connection' in locals():
            connection.close()

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()