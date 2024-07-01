# Oracle SQL*Plus Ansible Collection

This Ansible collection provides modules and roles for interacting with Oracle databases using SQL*Plus.

## Modules

### Oracle SQL*Plus Module

#### Features

- Execute SQL*Plus scripts or raw SQL
- Support for substitution variables and environment variables
- Bind variables support for raw SQL execution
- Various SQL*Plus options (SYSDBA, SYSOPER, silent mode, etc.)

#### Usage

See examples in the Usage section below.

## Installation

```bash
ansible-galaxy collection install andavarapu.oracle_sql
```

## Usage

### Using the Oracle SQL*Plus Module

#### Run SQL*Plus script with substitution variables

```yaml
- name: Run SQL*Plus script with substitution variables
  andavarapu.oracle_sql.oracle_sqlplus:
    script: "/path/to/sqlfile.sql"
    substitution_variables:
      - "value1"
      - "value2"
    env_variables:
      NLS_LANG: "AMERICAN_AMERICA.AL32UTF8"
```

#### Run raw SQL with bind variables

```yaml
- name: Run raw SQL with bind variables
  andavarapu.oracle_sql.oracle_sqlplus:
    raw_sql: "SELECT * FROM mytable WHERE column_name = :myVar"
    bind_variables:
      myVar: "value"
    env_variables:
      NLS_LANG: "AMERICAN_AMERICA.AL32UTF8"
```

## License

Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

## Author

Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
