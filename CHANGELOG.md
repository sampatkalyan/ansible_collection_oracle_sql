# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.2] - 2026-11-06

### Added
- Comprehensive module options documentation, prerequisites, and compatibility notes in `README.md`.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) running `ansible-test sanity` and `units` across Ansible 2.15–2.17 and Python 3.10–3.12 with pinned actions.
- Package `__init__.py` files under `tests/` hierarchy and added missing `import json` in `test_oracle_sqlplus.py`.
- Comprehensive security audit report in `SECURITY_AUDIT.md`.
- Docker development container configuration (`.devcontainer/Dockerfile` and `.devcontainer/devcontainer.json`) with native Ansible collection path binding.
- Learning and release guide (`DEVCONTAINER_AND_RELEASE_GUIDE.md`).
- `.gitignore` covering Python bytecode, pytest cache artifacts, virtual environments, and editor configurations.

### Changed
- Renamed and moved unit tests from `test/unit/plugin/modules/` to `tests/unit/plugins/modules/test_oracle_sqlplus.py` using `git mv` to adhere to standard Ansible collection layout for `ansible-test`.
- Normalized collection namespace references across `README.md`, module documentation, and test imports to `sampatkalyan.oracle_sql`.
- Updated repository and issue tracker URLs in `galaxy.yml` to the official GitHub repository (`sampatkalyan/ansible_collection_oracle_sql`).

### Fixed
- Corrected reversed FQCN references (`oracle_sql.sampatkalyan` to `sampatkalyan.oracle_sql`) in `oraclesql_database` and `oraclesql_table`.
- Fixed syntax typo (`oraclesql_database::`) in `oraclesql_database` examples.
- Removed inaccurate claim in `README.md` stating the collection includes roles.

### Security
- Documented plaintext credential exposure vulnerabilities in `oracle_sqlplus` (command-line arguments in process list) and `oracle_sqlloader` (returned `cmd` dictionary).
- Added missing `no_log: true` annotations in `DOCUMENTATION` blocks for `password` and `wallet_password` in `oracle_sqlloader` and `password` in `oraclesql_table`.
