# Copyright: (c) 2024, Andavarapu Sampat Kalyan <sampatkalyana@gmail.com>
# Apache License 2.0 (see LICENSE or http://www.apache.org/licenses/LICENSE-2.0)

import glob
import os
import re
import yaml
import pytest


MODULES = [
    'oracle_sqlloader',
    'oracle_sqlplus',
    'oraclesql_database',
    'oraclesql_table',
    'oraclesql_user',
]


@pytest.mark.parametrize('mod_name', MODULES)
def test_module_documentation_is_valid_yaml(mod_name):
    path = os.path.join('plugins', 'modules', f'{mod_name}.py')
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    doc_m = re.search(r'DOCUMENTATION\s*=\s*[rR]?[\'"]{3}(.+?)[\'"]{3}', src, re.DOTALL)
    assert doc_m is not None, f"Missing DOCUMENTATION block in {mod_name}"

    doc = yaml.safe_load(doc_m.group(1))
    assert isinstance(doc, dict), f"DOCUMENTATION in {mod_name} must parse into a dict"
    assert doc.get('module') == mod_name, f"Module name mismatch in doc: {doc.get('module')} vs {mod_name}"
    assert 'short_description' in doc, f"Missing short_description in {mod_name}"
    assert 'description' in doc, f"Missing description in {mod_name}"
    assert 'version_added' in doc, f"Missing version_added in {mod_name}"
    assert 'author' in doc, f"Missing author in {mod_name}"
    assert 'options' in doc, f"Missing options in {mod_name}"


@pytest.mark.parametrize('mod_name', MODULES)
def test_module_examples_is_valid_yaml(mod_name):
    path = os.path.join('plugins', 'modules', f'{mod_name}.py')
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    ex_m = re.search(r'EXAMPLES\s*=\s*[rR]?[\'"]{3}(.+?)[\'"]{3}', src, re.DOTALL)
    assert ex_m is not None, f"Missing EXAMPLES block in {mod_name}"

    examples = yaml.safe_load(ex_m.group(1))
    assert isinstance(examples, (list, dict)), f"EXAMPLES in {mod_name} must parse into a valid YAML list or dict"


@pytest.mark.parametrize('mod_name', MODULES)
def test_module_return_is_valid_yaml(mod_name):
    path = os.path.join('plugins', 'modules', f'{mod_name}.py')
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    ret_m = re.search(r'RETURN\s*=\s*[rR]?[\'"]{3}(.+?)[\'"]{3}', src, re.DOTALL)
    assert ret_m is not None, f"Missing RETURN block in {mod_name}"

    ret = yaml.safe_load(ret_m.group(1))
    assert isinstance(ret, dict), f"RETURN in {mod_name} must parse into a dict"


@pytest.mark.parametrize('mod_name', MODULES)
def test_module_metadata_block(mod_name):
    path = os.path.join('plugins', 'modules', f'{mod_name}.py')
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    meta_m = re.search(r'ANSIBLE_METADATA\s*=\s*(\{.+?\n\})', src, re.DOTALL)
    assert meta_m is not None, f"Missing ANSIBLE_METADATA in {mod_name}"

    meta = eval(meta_m.group(1))
    assert meta.get('metadata_version') == '1.1', f"Expected metadata_version 1.1 in {mod_name}, got {meta.get('metadata_version')}"
    assert meta.get('status') == ['preview'], f"Expected status ['preview'] in {mod_name}"
    assert meta.get('supported_by') == 'community', f"Expected supported_by 'community' in {mod_name}"


@pytest.mark.parametrize('mod_name', MODULES)
def test_module_passwords_have_no_log(mod_name):
    path = os.path.join('plugins', 'modules', f'{mod_name}.py')
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    doc_m = re.search(r'DOCUMENTATION\s*=\s*[rR]?[\'"]{3}(.+?)[\'"]{3}', src, re.DOTALL)
    doc = yaml.safe_load(doc_m.group(1))
    options = doc.get('options', {})

    for opt_name, opt_spec in options.items():
        if isinstance(opt_spec, dict) and 'password' in opt_name.lower():
            assert opt_spec.get('no_log') is True, f"Option '{opt_name}' in {mod_name} documentation must have no_log: true"
