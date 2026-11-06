# Oracle SQL Ansible Collection

This Ansible collection provides modules for interacting with Oracle databases.

> **Status**: Alpha (v0.0.3) — APIs may change in future releases.

## Modules

| Module | Description | Requirements |
|--------|-------------|-------------|
| `oracle_sqlplus` | Execute SQL\*Plus scripts or raw SQL | Oracle Instant Client (sqlplus on PATH) |
| `oracle_sqlloader` | Load data into Oracle using SQL\*Loader | Oracle Instant Client (sqlldr on PATH) |
| `oraclesql_database` | Manage Oracle databases (CDB/PDB) | cx\_Oracle Python library |
| `oraclesql_table` | Manage Oracle database tables | cx\_Oracle Python library |
| `oraclesql_user` | Manage Oracle database users | cx\_Oracle Python library |

## Installation

```bash
ansible-galaxy collection install sampatkalyan.oracle_sql
```

## Requirements

- **Ansible** >= 2.15.0
- **Python** >= 3.6 on the control node
- **Oracle Instant Client** with SQL\*Plus and/or SQL\*Loader on the target host (for `oracle_sqlplus` and `oracle_sqlloader` modules)
- **cx\_Oracle** Python library (for `oraclesql_database`, `oraclesql_table`, and `oraclesql_user` modules)

## Module Reference

### `oracle_sqlplus`

Execute Oracle SQL\*Plus scripts or raw SQL statements.

#### Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `username` | str | no | — | The username to connect to the Oracle database. |
| `password` | str | no | — | The password to connect to the Oracle database. *(no\_log)* |
| `database` | str | no | — | The database connect string. |
| `script` | path | no | — | The path to the SQL\*Plus script to be executed. |
| `raw_sql` | str | no | — | The raw SQL query to be executed. |
| `substitution_variables` | list(str) | no | `[]` | Substitution variables to replace in the SQL script or raw SQL. |
| `bind_variables` | dict | no | `{}` | Bind variables for raw SQL execution. |
| `env_variables` | dict | no | `{}` | Environment variables to set for SQL\*Plus execution. |
| `sysdba` | bool | no | `false` | Connect as SYSDBA. |
| `sysoper` | bool | no | `false` | Connect as SYSOPER. |
| `silent` | bool | no | `false` | Run SQL\*Plus in silent mode. |
| `nolog` | bool | no | `false` | Start SQL\*Plus without logging in. |
| `suppress_login` | bool | no | `false` | Suppress the login banner. |
| `markup_mode` | str | no | — | Set markup mode. Choices: `HTML`, `XML`. |
| `loop` | list(dict) | no | `[]` | List of SQL files or raw SQL to execute in a loop. |
| `restrict` | bool | no | `false` | Restrict SQL\*Plus commands. |
| `page_size` | int | no | `1000` | Number of rows to fetch at a time for large result sets. |

> **Note**: One of `script`, `raw_sql`, or `loop` must be specified. `script` and `raw_sql` are mutually exclusive.

#### Examples

```yaml
# Run SQL*Plus script with substitution variables
- name: Run SQL*Plus script with substitution variables
  sampatkalyan.oracle_sql.oracle_sqlplus:
    script: "/path/to/sqlfile.sql"
    substitution_variables:
      - "value1"
      - "value2"
    env_variables:
      NLS_LANG: "AMERICAN_AMERICA.AL32UTF8"

# Run raw SQL with bind variables
- name: Run raw SQL with bind variables
  sampatkalyan.oracle_sql.oracle_sqlplus:
    raw_sql: "SELECT * FROM mytable WHERE column_name = :myVar"
    bind_variables:
      myVar: "value"
    env_variables:
      NLS_LANG: "AMERICAN_AMERICA.AL32UTF8"

# Run multiple SQL statements in a loop
- name: Run SQL*Plus scripts and raw SQL in a loop
  sampatkalyan.oracle_sql.oracle_sqlplus:
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
```

### `oracle_sqlloader`

Load data into Oracle databases using SQL\*Loader.

#### Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `username` | str | no | — | The Oracle database username. |
| `password` | str | no | — | The Oracle database password. *(no\_log)* |
| `sid` | str | no | — | The Oracle database SID. |
| `host` | str | no | — | The Oracle database host. |
| `port` | int | no | — | The Oracle database port. |
| `connection_string` | str | no | — | Full connection string (overrides username/password/host/port/sid). |
| `wallet_location` | str | no | — | Location of Oracle Wallet for authentication. |
| `wallet_password` | str | no | — | Password for Oracle Wallet. *(no\_log)* |
| `control_file` | str | **yes** | — | Path to the SQL\*Loader control file. |
| `data_file` | str | **yes** | — | Path to the data file to load. |
| `log_file` | str | **yes** | — | Path for the log file. |
| `bad_file` | str | **yes** | — | Path for the bad records file. |
| `direct` | bool | no | `false` | Use direct path load. |
| `parallel` | bool | no | `false` | Use parallel load. |
| `skip` | int | no | — | Number of records to skip. |
| `load` | int | no | — | Number of records to load. |
| `silent` | str | no | — | Control feedback. Choices: `ALL`, `ERRORS`, `FEEDBACK`, `HEADER`. |
| `errors` | int | no | — | Maximum number of errors to allow. |
| `rows` | int | no | — | Number of rows to read. |
| `bindsize` | str | no | — | Maximum bind array size (bytes). |
| `readsize` | str | no | — | Read buffer size (bytes). |
| `external_table` | str | no | — | External table mode. Choices: `NOT_USED`, `GENERATE_ONLY`, `EXECUTE`. |
| `columnarrayrows` | int | no | — | Column array row count. |
| `parfile` | str | no | — | Parameter file path. |
| `scratch_dir` | str | no | — | Scratch directory for SQL\*Loader. |
| `discard_file` | str | no | — | Discard file path. |
| `charset` | str | no | — | Character set for SQL\*Loader. |
| `date_cache` | int | no | — | Date cache size (entries). |
| `degree_of_parallelism` | int | no | — | Degree of parallelism. |
| `direct_path_lock_wait` | bool | no | — | Wait for table locks during direct path load. |
| `empty_lobs_are_null` | bool | no | — | Treat empty LOBs as NULL. |
| `multithreading` | bool | no | — | Enable multithreading. |
| `no_index_errors` | bool | no | — | Tolerate indexing errors during direct path load. |
| `skip_index_maintenance` | bool | no | — | Skip index maintenance. |
| `skip_unusable_indexes` | bool | no | — | Skip unusable indexes. |
| `streamsize` | str | no | — | Data stream size (client to server). |
| `trim` | str | no | — | Trimming behavior. Choices: `LTRIM`, `RTRIM`, `BOTH`, `NOTRIM`. |

### `oraclesql_database`

Manage Oracle Container Databases (CDB) and Pluggable Databases (PDB).

#### Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `db_name` | str | **yes** | — | Name of the Oracle database. |
| `state` | str | **yes** | — | Desired state. Choices: `present`, `absent`. |
| `db_type` | str | **yes** | — | Database type. Choices: `CDB`, `PDB`. |
| `oracle_home` | str | **yes** | — | Path to Oracle Home directory. |
| `oracle_sid` | str | **yes** | — | Oracle System Identifier (SID). |
| `db_admin_user` | str | **yes** | — | Administrative user for database operations. |
| `db_admin_password` | str | **yes** | — | Password for the administrative user. *(no\_log)* |

### `oraclesql_table`

Create, modify, or drop tables in an Oracle database. Supports indexes, constraints, partitions, and other table properties.

#### Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `hostname` | str | **yes** | — | Oracle database host. |
| `port` | int | **yes** | — | Oracle database port. |
| `service_name` | str | **yes** | — | Oracle database service name. |
| `user` | str | **yes** | — | Username to connect. |
| `password` | str | **yes** | — | Password for connection. *(no\_log)* |
| `table_name` | str | **yes** | — | Name of the table to manage. |
| `state` | str | no | `present` | Desired state. Choices: `present`, `absent`, `modified`. |
| `columns` | list(dict) | no | — | Column definitions (name, type, primary\_key, nullable, unique, default, check, comment). |
| `indexes` | list(dict) | no | — | Index definitions (name, columns, unique, type). |
| `foreign_keys` | list(dict) | no | — | Foreign key constraints. |
| `partitioning` | dict | no | — | Partitioning configuration (type, columns, partitions). |
| `tablespace` | str | no | — | Tablespace for the table. |
| `temporary` | bool | no | `false` | Create as temporary table. |
| `parallel` | int | no | — | Degree of parallelism. |
| `compress` | bool | no | — | Enable table compression. |
| `row_movement` | bool | no | — | Enable row movement for partitioned tables. |
| `gather_stats` | bool | no | `false` | Gather statistics after operation. |
| `comment` | str | no | — | Table comment. |

### `oraclesql_user`

Manage Oracle database users (create, update, delete) and their privileges.

#### Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `connect_string` | str | **yes** | — | Oracle connection string. |
| `username` | str | **yes** | — | Username to manage. |
| `password` | str | **yes** | — | Password for the user. *(no\_log)* |
| `state` | str | **yes** | — | Desired state. Choices: `present`, `absent`. |
| `privileges` | list | no | — | List of privileges to grant. |

## Supported Versions

The `oracle_sqlplus` module has been tested with Oracle 11g, 12c, and 19c (per module documentation). Other modules list no specific version testing.

## License

Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

## Author

Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
