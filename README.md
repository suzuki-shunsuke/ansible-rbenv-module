# ansible-rbenv-module

[![Build Status](https://travis-ci.org/suzuki-shunsuke/ansible-rbenv-module.svg?branch=master)](https://travis-ci.org/suzuki-shunsuke/ansible-rbenv-module)

ansible module to run rbenv command.

https://galaxy.ansible.com/suzuki-shunsuke/rbenv-module/

## Notice

* This module doesn't support the [check mode](http://docs.ansible.com/ansible/dev_guide/developing_modules_general.html#supporting-check-mode)

## Supported platform

* GenericLinux
* MacOSX

We test this module in

* Ubuntu 16.04 (Vagrant, Virtualbox)
* CentOS 7.3 (Vagrant, Virtualbox)
* MaxOS Sierra 10.12.5

## Requirements

* [rbenv](https://github.com/rbenv/rbenv)
* [ruby build dependencies](https://github.com/rbenv/ruby-build/wiki#suggested-build-environment)
* [ruby-build](https://github.com/rbenv/ruby-build)

If you want to install rbenv and ruby-build and ruby build dependencies with ansible role, we recommend the [suzuki-shunsuke.rbenv](https://galaxy.ansible.com/suzuki-shunsuke/rbenv/).

## Supported rbenv subcommands and options

```
$ rbenv install [--skip-existing] [--force] <version>
$ rbenv uninstall --force <version>
$ rbenv install --list
$ rbenv versions [--bare] [--skip-aliases]
$ rbenv global
$ rbenv global <version>
```

## Install

```
$ ansible-galaxy install suzuki-shunsuke.rbenv-module
```

```yaml
# playbook.yml

- hosts: default
  roles:
  # After you call this role, you can use this module.
  - suzuki-shunsuke.rbenv-module
```

## Options

In addition to this document, please see [rbenv command reference](https://github.com/rbenv/rbenv#command-reference) and the output of `rbenv help <command>` command also.

### Common Options

name | type | required | default | choices / example | description
--- | --- | --- | --- | --- | ---
subcommand | str | no | install | [install, uninstall, versions, global] |
rbenv_root | str | no | | ~/.rbenv | If the environment variable "RBENV_ROOT" is not set, this option is required
expanduser | bool | no | yes | | By default the environment variable RBENV_ROOT and "rbenv_root" option are filtered by [os.path.expanduser](https://docs.python.org/2.7/library/os.path.html#os.path.expanduser)

### Options of the "install" subcommand

parameter | type | required | default | choices / example | description
--- | --- | --- | --- | --- | ---
version | str | no | | 2.4.0 |
list | bool | no | no | | -l option
skip_existing | bool | no | yes | | -s option
force | bool | no | no | | -f option

Either "version" or "list" option is required.
If the "list" option is set, the return value of that task has "versions" field.

### Options of the "uninstall" subcommand

parameter | type | required | default | choices / example | description
--- | --- | --- | --- | --- | ---
version | str | yes | | 2.4.0 |

### Options of the "global" subcommand

parameter | type | required | default | choices | description
--- | --- | --- | --- | --- | ---
version | str | no | | |

The return value of the "global" subcommand has "versions" field.

### Options of the "versions" subcommand

parameter | type | required | default | choices | description
--- | --- | --- | --- | --- | ---
bare | bool | no | yes | |
skip_aliases | bool | no | yes | | --skip-aliases option

The return value of the "versions" subcommand has "versions" field.

## Example

```yaml
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
```

## Tips

### Install ruby packages with gem

Now this module doesn't support `gem` subcommand,
but you can do it with [the official gem module](http://docs.ansible.com/ansible/gem_module.html).

```yaml
# install ruby and create virtualenv before using gem module
- name: rbenv install --skip-existing 2.4.0
  rbenv:
    rbenv_root: "{{rbenv_root}}"
    version: 2.4.0

# use gem module with executable option
- name: install rake on ruby 2.4.0
  gem:
    name: rake
    executable: "{{rbenv_root}}/versions/2.4.0/bin/gem"
```

## Change Log

See [CHANGELOG.md](CHANGELOG.md).

## Licence

[MIT](LICENSE)

## Develop

### Requirements

* Vagrant
* Ansible
* Node.js
* yarn

### Setup

```
$ yarn install
$ cd tests
$ ansible-galaxy install -r roles.yml
```

### Test

```
$ cd tests
$ vagrant up --provision
```
