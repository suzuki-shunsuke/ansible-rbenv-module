#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: rbenv
short_description: Run rbenv command
options:
  bare:
    description:
    - the "--bare" option of "versions" and "virtualenvs" subcommand
    required: false
    type: bool
    default: true
  expanduser:
    description:
    - whether the environment variable RBENV_ROOT and "rbenv_root" option are filtered by os.path.expanduser
    required: false
    type: bool
    default: true
  force:
    description:
    - the "-f/--force" option of rbenv install
    required: false
    type: bool
    default: false
  list:
    description:
    - -l/--list option of rbenv install command
    required: false
    type: bool
    default: false
  rbenv_root:
    description:
    - RBENV_ROOT
    required: false
    type: str
    default: null
  skip_aliases:
    description:
    - the "-s/--skip-aliases" option of rbenv virtualenvs
    required: false
    type: bool
    default: true
  skip_existing:
    description:
    - the "-s/--skip-existing" option of rbenv install
    required: false
    type: bool
    default: true
  subcommand:
    description:
    - rbenv subcommand
    choices: ["install", "uninstall", "versions", "global"]
    required: false
    default: install
  version:
    description:
    - A ruby version name
    type: str
    required: false
    default: null
  versions:
    description:
    - ruby version names
    type: list
    required: false
    default: null
requirements:
- rbenv
author: "Suzuki Shunsuke"
'''

EXAMPLES = '''
- name: rbenv install --list
  rbenv:
    list: yes
    rbenv_root: "~/.rbenv"
  register: result
  failed_when: result.failed or result.changed
- debug:
  var: result.versions
- name: rbenv global
  rbenv:
    subcommand: global
    rbenv_root: "~/.rbenv"
  register: result
  failed_when: result.failed or result.changed
- debug:
  var: result
- name: rbenv install --skip-existing 2.4.0
  rbenv:
    version: 2.4.0
    rbenv_root: "~/.rbenv"
- name: rbenv versions --bare --skip-aliases
  rbenv:
    subcommand: versions
    rbenv_root: "~/.rbenv"
  register: result
  failed_when: result.failed or result.changed
- debug:
  var: result.versions
- name: rbenv versions --skip-aliases
  rbenv:
    subcommand: versions
    rbenv_root: "~/.rbenv"
    bare: no
  register: result
  failed_when: result.failed or result.changed
- debug:
  var: result.versions
- name: rbenv versions --bare
  rbenv:
    subcommand: versions
    rbenv_root: "~/.rbenv"
    skip_aliases: no
  register: result.versions
  failed_when: result.failed or result.changed
- debug:
  var: result
- name: rbenv global 2.4.0
  rbenv:
    subcommand: global
    version: 2.4.0
    rbenv_root: "~/.rbenv"
  register: result
- debug:
  var: result.version
- name: rbenv global
  rbenv:
    subcommand: global
    rbenv_root: "~/.rbenv"
  register: result
  failed_when: result.failed or result.changed
- debug:
  var: result.versions
- name: rbenv uninstall --force 2.3.1
  rbenv:
    subcommand: uninstall
    version: 2.3.1
  environment:
    RBENV_ROOT: "~/.rbenv"
  register: result
- name: install rake on ruby 2.4.0
  gem:
    name: rake
    executable: "~/.rbenv/versions/2.4.0/bin/gem"
'''

RETURNS = '''
version:
  description: the return value of `rbenv global`
  returned: success
  type: str
  sample: 2.4.0
versions:
  description: the return value of `rbenv install --list` or `rbenv versions`
  returned: success
  type: list
  sample:
  - 2.4.0
  - 2.3.0
'''

import os  # noqa E402

from ansible.module_utils.basic import AnsibleModule  # noqa E402


def wrap_get_func(func):
    def wrap(module, *args, **kwargs):
        result, data = func(module, *args, **kwargs)
        if result:
            module.exit_json(**data)
        else:
            module.fail_json(**data)

    return wrap


def get_install_list(module, cmd_path, **kwargs):
    """ rbenv install --list
    """
    rc, out, err = module.run_command([cmd_path, "install", "-l"], **kwargs)
    if rc:
        return (False, dict(msg=err, stdout=out))
    else:
        # slice: remove header and last newline
        versions = [line.strip() for line in out.split("\n")[1:-1]]
        return (True, dict(
            changed=False, failed=False, stdout=out, stderr=err,
            versions=versions))


cmd_install_list = wrap_get_func(get_install_list)


def get_versions(module, cmd_path, bare, skip_aliases, **kwargs):
    """ rbenv versions [--bare] [--skip-aliases]
    """
    cmd = [cmd_path, "versions"]
    if bare:
        cmd.append("--bare")
    if skip_aliases:
        cmd.append("--skip-aliases")
    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return (False, dict(msg=err, stdout=out))
    else:
        # slice: remove last newline
        versions = [line.strip() for line in out.split("\n")[:-1]]
        return (True, dict(
            changed=False, failed=False, stdout=out, stderr=err,
            versions=versions))


cmd_versions = wrap_get_func(get_versions)


def cmd_uninstall(module, cmd_path, version, **kwargs):
    """ rbenv uninstall --force <version>
    """
    result, data = get_versions(module, cmd_path, True, False, **kwargs)
    if not result:
        return module.fail_json(**data)
    if version not in data["versions"]:
        return module.exit_json(
            changed=False, failed=False, stdout="", stderr="")
    cmd = [cmd_path, "uninstall", "--force", version]
    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        module.fail_json(msg=err, stdout=out)
    else:
        module.exit_json(changed=True, failed=False, stdout=out, stderr=err)


def get_global(module, cmd_path, **kwargs):
    """ rbenv global
    """
    rc, out, err = module.run_command([cmd_path, "global"], **kwargs)
    if rc:
        return (False, dict(msg=err, stdout=out))
    else:
        # slice: remove last newline
        versions = [line.strip() for line in out.split("\n")[:-1]]
        version = versions[0] if versions else None
        return (True, dict(
            changed=False, failed=False, stdout=out, stderr=err,
            version=version))


cmd_get_global = wrap_get_func(get_global)


def cmd_set_global(module, cmd_path, version, **kwargs):
    """ rbenv global <version>
    """
    result, data = get_global(module, cmd_path, **kwargs)
    if not result:
        return module.fail_json(**data)
    if set(data["version"]) == version:
        return module.exit_json(
            changed=False, failed=False, stdout="", stderr="",
            version=version)
    rc, out, err = module.run_command(
        [cmd_path, "global", version], **kwargs)
    if rc:
        module.fail_json(msg=err, stdout=out)
    else:
        module.exit_json(
            changed=True, failed=False, stdout=out, stderr=err,
            version=version)


def cmd_install(module, cmd_path, version, params, **kwargs):
    """ rbenv install [--skip-existing] [--force] <version>
    """
    cmd = [cmd_path, "install"]
    if params["skip_existing"] is not False:
        force = False
        cmd.append("--skip-existing")
    elif params["force"] is True:
        force = True
        cmd.append("--force")

    cmd.append(version)

    rc, out, err = module.run_command(cmd, **kwargs)
    if rc:
        return module.fail_json(msg=err, stdout=out)
    else:
        changed = force or out
        return module.exit_json(
            changed=changed, failed=False, stdout=out, stderr=err)


MSGS = {
    "required_rbenv_root": (
        "Either the environment variable 'RBENV_ROOT' "
        "or 'rbenv_root' option is required")
}


def get_rbenv_root(params):
    if params["rbenv_root"]:
        if params["expanduser"]:
            return os.path.expanduser(params["rbenv_root"])
        else:
            return params["rbenv_root"]
    else:
        if "RBENV_ROOT" not in os.environ:
            return None
        if params["expanduser"]:
            return os.path.expanduser(os.environ["RBENV_ROOT"])
        else:
            return os.environ["RBENV_ROOT"]


def main():
    module = AnsibleModule(argument_spec={
        "bare": {"required": False, "type": "bool", "default": True},
        "force": {"required": False, "type": "bool", "default": None},
        "expanduser": {"required": False, "type": "bool", "default": True},
        "list": {"required": False, "type": "bool", "default": False},
        "rbenv_root": {"required": False, "default": None},
        "skip_aliases": {"required": False, "type": "bool", "default": True},
        "skip_existing": {"required": False, "type": "bool", "default": None},
        "subcommand": {
            "required": False, "default": "install",
            "choices": [
                "install", "uninstall", "versions", "global"]
        },
        "version": {"required": False, "type": "str", "default": None},
        "versions": {"required": False, "type": "list", "default": None},
    })
    params = module.params
    environ_update = {}
    rbenv_root = get_rbenv_root(params)
    if rbenv_root is None:
        return module.fail_json(
            msg=MSGS["required_rbenv_root"])
    environ_update["RBENV_ROOT"] = rbenv_root
    run_options = {"environ_update": environ_update}
    cmd_path = os.path.join(rbenv_root, "bin", "rbenv")

    if params["subcommand"] == "install":
        if params["list"]:
            return cmd_install_list(module, cmd_path, **run_options)
        version = params["version"]
        if not version:
            return module.fail_json(
                msg="install subcommand requires the 'version' parameter")
        return cmd_install(
            module, cmd_path, version, params, **run_options)
    elif params["subcommand"] == "uninstall":
        version = params["version"]
        if not version:
            return module.fail_json(
                msg="uninstall subcommand requires the 'version' parameter")
        return cmd_uninstall(
            module, cmd_path, version, **run_options)
    elif params["subcommand"] == "versions":
        return cmd_versions(
            module, cmd_path, params["bare"],
            params["skip_aliases"], **run_options)
    elif params["subcommand"] == "global":
        if params["version"]:
            return cmd_set_global(
                module, cmd_path, params["version"],
                **run_options)
        else:
            return cmd_get_global(
                module, cmd_path, **run_options)


if __name__ == '__main__':
    main()
