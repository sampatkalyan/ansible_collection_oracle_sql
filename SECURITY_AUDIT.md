# Security Audit: Credential Handling and Secret Leakage

**Repository**: `ansible_collection_oracle_sql` (`sampatkalyan.oracle_sql`)
**Audit Date**: November 2026
**Auditor**: Automated Code Review & Security Analysis
**Scope**: `plugins/modules/oracle_sqlplus.py` and related collection modules (`oracle_sqlloader.py`, `oraclesql_database.py`, `oraclesql_table.py`, `oraclesql_user.py`).

---

## 1. Executive Summary

This audit assesses how credentials, connection strings, and sensitive data are received, processed, and transmitted to subprocesses or external libraries across the collection, with primary focus on `oracle_sqlplus`.

Multiple security issues were identified ranging from **Critical** (credentials exposed on command line visible in process table) to **Medium** (credentials returned in module output or leaked through exception messages).

---

## 2. Mechanism Analysis: How Credentials Reach SQL*Plus

In `plugins/modules/oracle_sqlplus.py`:

| Channel | Used for Credentials? | Details |
|---|---|---|
| **Command-Line Arguments (`argv`)** | **YES** | Plaintext `username/password@database` is constructed as a string and appended directly to `sqlplus_cmd` (lines 286–291), then executed via `subprocess.Popen(sqlplus_cmd, ...)` (line 300). |
| **Standard Input (`stdin`)** | **NO** (SQL only) | Only the SQL script content or `raw_sql` string is sent over `stdin` via `process.communicate(input=sql_script.encode())` (line 301). Credentials are not sent over stdin. |
| **Environment Variables (`env`)** | **NO** (Indirect) | `env_variables` dict is merged into `os.environ.copy()` and passed to `subprocess.Popen(..., env=env)` (lines 294–300). If users specify credentials in custom environment variables, they exist in the subprocess environment. |
| **Temporary Files** | **NO** | The module does not create temporary files on disk. Scripts are read directly into memory from the provided `script` path (line 258) or passed in memory. |

---

## 3. Findings

### Finding 1: Plaintext Credentials Exposed via Process Arguments (`ps`)
- **Severity**: **CRITICAL**
- **File**: `plugins/modules/oracle_sqlplus.py`
- **Lines**: 286–291, 300
- **Description**:
  Lines 286–291 construct the connection string:
  ```python
  if username and password and database:
      conn_str = f"{username}/{password}@{database}"
  else:
      conn_str = '/ as sysdba' if sysdba else '/ as sysoper' if sysoper else ''

  sqlplus_cmd.append(conn_str)
  ```
  This command list is executed via `subprocess.Popen(sqlplus_cmd, ...)`.
- **Impact**:
  On multi-user Unix/Linux hosts, any local user or non-privileged process running `ps -ef`, `ps aux`, inspecting `/proc/<pid>/cmdline`, or querying OS process tables on Windows (`tasklist`, `Get-Process`, Process Explorer) can observe the database password in plaintext during SQL*Plus execution.
- **Recommendation**:
  Invoke SQL*Plus with the `/NOLOG` flag and send the connection command via `stdin` before executing the user's SQL script:
  ```text
  CONNECT username/password@database
  ```
  This keeps credentials inside standard input and out of process argument lists.

---

### Finding 2: Plaintext Password Returned in Result `cmd` (`oracle_sqlloader`)
- **Severity**: **HIGH**
- **File**: `plugins/modules/oracle_sqlloader.py`
- **Lines**: 405–417, 457, 471
- **Description**:
  The module builds the command line including the plaintext password:
  ```python
  conn = f"{module.params['username']}/{module.params['password']}@{module.params['host']}:{module.params['port']}/{module.params['sid']}"
  cmd = ['sqlldr', f'userid={conn}', ...]
  ```
  It then records the exact command string in the returned dictionary:
  ```python
  result['cmd'] = ' '.join(cmd)
  ...
  module.exit_json(**result)
  ```
  And on failure (line 308):
  ```python
  module.fail_json(msg="SQL*Loader failed", rc=proc.returncode, stdout=stdout, stderr=stderr, cmd=' '.join(cmd))
  ```
- **Impact**:
  Ansible displays module return values in execution output when running with `-v` / `-vvv` or registers them into playbook variables. Anyone with access to Ansible controller logs, CI logs, or AWX/Automation Controller job outputs will see the password. Furthermore, `cmd` exposes credentials in `ps` just like Finding 1.
- **Recommendation**:
  Redact or omit credentials from `result['cmd']` (e.g., `f"userid={username}/******@{host}..."`). Avoid passing credentials on the CLI; use a parameter file (`parfile`) with restricted file permissions or Oracle Wallet.

---

### Finding 3: Password Exposure via SQL Error Messages (`oraclesql_user`)
- **Severity**: **MEDIUM**
- **File**: `plugins/modules/oraclesql_user.py`
- **Lines**: 28, 47, 52
- **Description**:
  In `plugins/modules/oraclesql_user.py`, SQL statements are formatted with plaintext passwords:
  ```python
  query = f"CREATE USER {username} IDENTIFIED BY {password}"
  execute_sql_query(module, connection, query)
  ```
  If execution fails, `execute_sql_query` catches `DatabaseError` and outputs:
  ```python
  module.fail_json(msg=f"Failed to execute SQL query: {query}. Error: {e}")
  ```
- **Impact**:
  If user creation or alteration fails (e.g., password does not satisfy Oracle password complexity rules, tablespace quota issue, or permission error), the failed SQL statement containing the plaintext password is included in `msg` and emitted in Ansible failure logs.
- **Recommendation**:
  Mask or sanitize sensitive queries before including them in error messages:
  ```python
  safe_query = re.sub(r'IDENTIFIED BY \S+', 'IDENTIFIED BY ******', query)
  module.fail_json(msg=f"Failed to execute SQL query: {safe_query}. Error: {e}")
  ```

---

### Finding 4: Module Parameters Dictionary Returned in Result (`oraclesql_table`)
- **Severity**: **MEDIUM**
- **File**: `plugins/modules/oraclesql_table.py`
- **Lines**: 568, 616, 625
- **Description**:
  Line 616 assigns all module parameters directly into the result dictionary:
  ```python
  result['table'] = module.params
  ...
  module.exit_json(**result)
  ```
  `module.params` includes `password`.
- **Impact**:
  Although Ansible core filters parameters marked with `no_log=True` in standard result output, returning raw parameter dictionaries into custom subkeys can bypass certain output filters or leak passwords into registered variables and debug tasks.
- **Recommendation**:
  Do not copy `module.params` into `result['table']`. Construct the table descriptor explicitly, omitting `password`, `user`, and other connection parameters.

---

### Finding 5: Missing `no_log` on Suboptions in `loop` Parameter (`oracle_sqlplus`)
- **Severity**: **MEDIUM**
- **File**: `plugins/modules/oracle_sqlplus.py`
- **Lines**: 372, 395–401
- **Description**:
  The `loop` option is defined as:
  ```python
  loop=dict(type='list', elements='dict', required=False, default=[])
  ```
  In lines 396–401, `temp_params.update(item)` merges loop items into module parameters. If a playbook specifies `password` inside a loop element, Ansible's argument parser cannot know that the sub-key `password` within `loop` is sensitive because `loop` lacks an explicit sub-argument spec (`options=...`).
- **Impact**:
  Playbook task invocations passing per-item passwords in `loop` can have passwords printed in task logs unless the user sets `no_log: true` at the task level.
- **Recommendation**:
  Either specify full `options` dictionary for `loop` with `no_log=True` on sensitive keys or recommend using task-level `loop:` in Ansible playbooks instead of an internal module-level `loop` argument.

---

### Finding 6: SQL Injection via Naive Bind and Substitution Replacement (`oracle_sqlplus`)
- **Severity**: **LOW / FUNCTIONAL RISK**
- **File**: `plugins/modules/oracle_sqlplus.py`
- **Lines**: 264–272
- **Description**:
  Bind variables are substituted into `raw_sql` using string replacement:
  ```python
  if raw_sql and bind_variables:
      for var, value in bind_variables.items():
          sql_script = sql_script.replace(f":{var}", f"'{value}'")
  ```
  Substitution variables are similarly replaced:
  ```python
  for i, value in enumerate(substitution_variables, start=1):
      subst_var = f'&{i}'
      sql_script = sql_script.replace(subst_var, str(value))
  ```
- **Impact**:
  This does not provide true database bind variable isolation. Values containing single quotes or SQL control sequences can lead to syntax errors or unintended SQL command execution.
- **Recommendation**:
  Document that `bind_variables` in `oracle_sqlplus` performs client-side string substitution, or consider escaping single quotes (`value.replace("'", "''")`).

---

### Finding 7: Inconsistent Parameter Logic when Database is Omitted (`oracle_sqlplus`)
- **Severity**: **LOW**
- **File**: `plugins/modules/oracle_sqlplus.py`
- **Lines**: 286–290
- **Description**:
  Line 286 requires all three of `username`, `password`, and `database` to be non-empty:
  ```python
  if username and password and database:
      conn_str = f"{username}/{password}@{database}"
  else:
      conn_str = '/ as sysdba' if sysdba else '/ as sysoper' if sysoper else ''
  ```
- **Impact**:
  If a user specifies `username` and `password` without `database` (intending a local Oracle connection using `ORACLE_SID`), `conn_str` silently falls back to `""` or `'/'`, dropping the supplied username and password completely.
- **Recommendation**:
  Support `username` and `password` without `database`:
  ```python
  if username and password:
      conn_str = f"{username}/{password}@{database}" if database else f"{username}/{password}"
  ```

---

## 4. Summary of Parameter `no_log` Coverage Across Modules

| Module | Parameter | In `argument_spec` `no_log`? | In `DOCUMENTATION` `no_log`? | Status |
|---|---|---|---|---|
| `oracle_sqlplus` | `password` | **Yes** (line 359) | **Yes** (line 44) | OK |
| `oracle_sqlplus` | `loop` (nested `password`) | **No** (no suboptions) | **No** | Needs task-level `no_log` |
| `oracle_sqlloader` | `password` | **Yes** (line 335) | Missing (`no_log: true`) | Doc mismatch |
| `oracle_sqlloader` | `wallet_password` | **Yes** (line 341) | Missing (`no_log: true`) | Doc mismatch |
| `oraclesql_database` | `db_admin_password` | **Yes** (line 145) | **Yes** (line 57) | OK |
| `oraclesql_table` | `password` | **Yes** (line 526) | Missing (`no_log: true`) | Doc mismatch |
| `oraclesql_user` | `password` | **Yes** (line 81) | No DOCUMENTATION block | Doc missing |
