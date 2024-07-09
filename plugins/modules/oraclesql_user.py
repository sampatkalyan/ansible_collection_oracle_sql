#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import cx_Oracle

def connect_to_oracle(module):
    """
    Establishes a connection to Oracle database using cx_Oracle library.
    """
    try:
        connection = cx_Oracle.connect(module.params['connect_string'])
        return connection
    except cx_Oracle.DatabaseError as e:
        module.fail_json(msg=f"Failed to connect to Oracle: {e}")

def execute_sql_query(module, connection, query, params=None):
    """
    Executes a SQL query on the Oracle database and handles exceptions.
    """
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor
    except cx_Oracle.DatabaseError as e:
        module.fail_json(msg=f"Failed to execute SQL query: {query}. Error: {e}")

def create_or_update_user(module, connection):
    """
    Creates or updates an Oracle SQL user based on module parameters.
    """
    username = module.params['username']
    password = module.params['password']
    state = module.params['state']
    privileges = module.params['privileges']

    if state == 'present':
        # Check if the user already exists
        query = "SELECT COUNT(*) FROM dba_users WHERE username = :username"
        cursor = execute_sql_query(module, connection, query, {'username': username})
        user_exists = cursor.fetchone()[0]

        if user_exists == 0:
            # User does not exist, create it
            query = f"CREATE USER {username} IDENTIFIED BY {password}"
            execute_sql_query(module, connection, query)
            module.exit_json(changed=True, msg=f"User '{username}' created successfully")
        else:
            # User exists, update password and privileges if needed
            query = f"ALTER USER {username} IDENTIFIED BY {password}"
            execute_sql_query(module, connection, query)

            if privileges:
                for privilege in privileges:
                    query = f"GRANT {privilege} TO {username}"
                    execute_sql_query(module, connection, query)

            module.exit_json(changed=False, msg=f"User '{username}' exists and updated")

    elif state == 'absent':
        # Delete the user if it exists
        query = f"SELECT COUNT(*) FROM dba_users WHERE username = :username"
        cursor = execute_sql_query(module, connection, query, {'username': username})
        user_exists = cursor.fetchone()[0]

        if user_exists > 0:
            # User exists, delete it
            query = f"DROP USER {username} CASCADE"
            execute_sql_query(module, connection, query)
            module.exit_json(changed=True, msg=f"User '{username}' deleted successfully")
        else:
            # User does not exist
            module.exit_json(changed=False, msg=f"User '{username}' does not exist")

def main():
    module_args = {
        'connect_string': {'type': 'str', 'required': True},
        'username': {'type': 'str', 'required': True},
        'password': {'type': 'str', 'required': True, 'no_log': True},
        'state': {'type': 'str', 'required': True, 'choices': ['present', 'absent']},
        'privileges': {'type': 'list'},
        # Add more parameters as needed
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    connection = connect_to_oracle(module)

    try:
        create_or_update_user(module, connection)

    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    main()
