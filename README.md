Mutagen Helper
==============

[![Latest Version](http://img.shields.io/pypi/v/mutagen-helper.svg)](https://pypi.python.org/pypi/mutagen-helper)
![MIT License](http://img.shields.io/badge/license-MIT-blue.svg)
[![Build Status](http://img.shields.io/travis/gfi-centre-ouest/mutagen-helper.svg)](https://travis-ci.org/gfi-centre-ouest/mutagen-helper)
[![Coveralls](http://img.shields.io/coveralls/gfi-centre-ouest/mutagen-helper.svg)](https://coveralls.io/github/gfi-centre-ouest/mutagen-helper?branch=develop)

Mutagen Helper allow you to define [Mutagen](https://mutagen.io/) synchronisation sessions inside a configuration file 
on directories you want to synchronise. Created sessions are marked with a session name and a project name that makes
them easier to manage.

About mutagen 0.10+
===================

Mutagen was written on earlier version of Mutagen. Mutagen `0.10+` brings a new 
[Orchestration feature](https://mutagen.io/documentation/orchestration/) that makes most mutagen-helper features
redundant, so you should first give a try to this new feature.

I'm still working with [Mutagen's author Jacob Howard](https://github.com/havoc-io) to embed as much as mutagen-helper 
use cases as possible into mutagen's core ([mutagen-io/mutagen#109](https://github.com/mutagen-io/mutagen/issues/109)).

Install
-------

- Download binaries right from [github release pages](https://github.com/gfi-centre-ouest/mutagen-helper/releases)

or

- run `pip install mutagen-helper` on Python 3.6+

Quickstart
----------

- Install mutagen as usual (version `0.9+`), and make it available in the user `PATH` or define `MUTAGEN_HELPER_MUTAGEN_BIN` environment 
variable to the path of the mutagen binary as an alternative (ie: `C:\tools\mutagen\mutagen-helper.exe`).

- Create `.mutagen-helper.yml` file inside some local directory you want to synchronize and set `beta` property to the 
destination of the synchronisation.

```yaml
project_name: 'helper-project' # Optional, it will fallback to directory name if not defined
beta: 'root@192.168.1.100:/home/vagrant/projects' # Beta side of the synchronisation
options: # Options can be provided
  sync-mode: two-way-resolved
  default-file-mode-beta: 664
  default-directory-mode-beta: 775
  default-owner-beta: vagrant
  default-group-beta: vagrant
  ignore-vcs: True
  ignore:
    - node_modules/
    - vendor/
```

Mutagen Helper appends the `project_name` to the beta URL. It means that this
directory will be synchronised to `/home/vagrant/projects/helper-project`.

- Run `mutagen-helper up` from the project directory.

- Run `mutagen-helper list` to see which sessions are running. Output of this command match `mutagen list` output, 
but as JSON and with additional synchronisation helper properties like `Project name`, `Session name` and 
`Configuration file`.

- Run `mutagen-helper --help` to check other available commands.

Usage
-----

```text
Usage: __main__.py [OPTIONS] COMMAND [ARGS]...

  Main command group :return:

Options:
  --version      Show the version and exit.
  -v, --verbose  Add more output
  -s, --silent   No output at all
  -h, --help     Show this message and exit.

Commands:
  up      Creates and starts a new synchronization sessions
  down    Permanently terminates synchronization sessions
  pause   Pauses synchronization sessions
  flush   Flush synchronization sessions
  resume  Resumes paused or disconnected synchronization sessions
  list    Lists existing synchronization sessions and their statuses
```

Multiple projects support
-------------------------

You may `up` multiple projects at the same time if all your projects lies in the same directory.

```text
C:\workspace
    |- project1
        |- .mutagen-helper.yml
        |- ...
    |- project2
        |- .mutagen-helper.yml
        |- ...
    |- project3
        |- .mutagen-helper.yml
        |- ...
```

```bash
mutagen-helper up --path C:\workspace
```

or

```bash
cd C:\workspace
mutagen-helper up
```

or 

```bash
export MUTAGEN_HELPER_PATH=C:\workspace
mutagen-helper up
```

Those command will create all mutagen sessions defined in `.mutagen-helper.yml` of each subdirectories of `C:\workspace`.

Advanced configuration
----------------------

You may use environment variable expansion, with `${VARIABLE}` syntax like in bash. Your can set a default value if 
variable is not defined with `${VARIABLE:-default}`.

Your may also define multiple sessions under a `sessions` key. Properties defined at root of the configuration file 
will be inherited by each session.

You may also give names to sessions for them to be identified with precision, but keep in mind that changing name
on running sessions could cause problem as they are used to find out the real mutagen session id.

```yaml
beta: '${DOCKER_DEVBOX_MUTAGEN_BETA:-root@192.168.1.100:/home/vagrant/projects}'
sessions:
  - options:
      name: 'partial-watch-alpha'
      sync-mode: two-way-resolved
      default-file-mode-beta: 664
      default-directory-mode-beta: 775
      default-owner-beta: vagrant
      default-group-beta: vagrant
      ignore-vcs: True
      ignore:
        - node_modules/
        - vendor/
      max-staging-file-size: 1MB
      watch-mode-beta: no-watch
  - options:
      name: 'full-no-watch'
      sync-mode: two-way-resolved
      default-file-mode-beta: 664
      default-directory-mode-beta: 775
      default-owner-beta: vagrant
      default-group-beta: vagrant
      max-staging-file-size: 1MB
      watch-mode: no-watch
```

It's possible to define a single configuration file for multiple projects with `projects` key. It supports the same 
inheritance mechanism as with `sessions`.

```yaml
beta: '${DOCKER_DEVBOX_MUTAGEN_BETA:-root@192.168.1.100:/home/vagrant/projects}'
options:
  sync-mode: two-way-resolved
  default-file-mode-beta: 664
  default-directory-mode-beta: 775
  default-owner-beta: vagrant
  default-group-beta: vagrant
projects:
  - path: C:\workspace\project1
  - path: C:\workspace\project2
  - path: C:\workspace\project3
    beta: beta: 'vagrant@192.168.1.100:/home/vagrant/projects'
    options:
      sync-mode: two-way-resolved
      default-file-mode-beta: 600
      default-directory-mode-beta: 700
```


Automatic configuration
-----------------------

You can automate the configuration of a directory containing many project. Create a `.mutagen-helper.yml` file inside
the parent of those directories, and set `auto_configure`.

```yaml
auto_configure: True
``` 

```text
C:\workspace
    |- .mutagen-helper.yml  # Auto configure YAML file
    |- project-dev1  # Projects without any mutagen-helper configuration file
        |- ...
    |- project-dev2
        |- ...
    |- project-dev2-stage
        |- ...
    |- project-prod1
        |- ...
```

This will create synchronisation projects for each subdirectory (`project-dev1`, `project-dev2`, `project-dev2-stage` and 
`project-prod1`).

You can set `include` and `exclude` to disable auto configure feature for some subdirectories only, and other property
you can normally use on `projects` and `sessions`

```yaml
beta: '${DOCKER_DEVBOX_MUTAGEN_BETA:-root@192.168.1.100:/home/vagrant/projects}'
auto_configure: 
  include: 
    - '*-dev*'
  exclude:
    - '*-stage'
options:
  sync-mode: two-way-resolved
  default-file-mode-beta: 644
  default-directory-mode-beta: 755
  default-owner-beta: vagrant
  default-group-beta: vagrant
``` 

this will create a synchronisation project for `project-dev1` and `project-dev2` (`include` has priority other `exclude`).

By default, if a configuration file is present in a project directory, it is still used to create the 
synchronisation project. You can ignore those configuration files with `ignore_project_configuration` to let auto 
configure create the synchronisation project on his own.

```yaml
beta: '${DOCKER_DEVBOX_MUTAGEN_BETA:-root@192.168.1.100:/home/vagrant/projects}'
auto_configure: 
  ignore_project_configuration: True  # It can also be a list of glob for project names to ignore
options:
  sync-mode: two-way-resolved
  default-file-mode-beta: 644
  default-directory-mode-beta: 755
  default-owner-beta: vagrant
  default-group-beta: vagrant
```

Environment variables and default values
----------------------------------------

Some properties have default values, based on environment variables if defined.

  - `alpha`
    - `MUTAGEN_HELPER_ALPHA` environment variable, *or*
    - Directory when the `.mutagen-helper.yml` resides
  - `beta`: 
    - `MUTAGEN_HELPER_BETA` environment variable, *or*
    - mandatory in the `.mutagen-helper.yml`
  - `append_project_name_to_beta`: 
    - `MUTAGEN_HELPER_APPEND_PROJECT_NAME_TO_BETA`, *or*
    -  `True`

`MUTAGEN_HELPER_PATH` environment variable can be set to a path to make mutagen-helper load 
configuration from this path by default instead of current working directory. (`--path` option can still be used)