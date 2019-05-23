Mutagen Helper
==============

[![Latest Version](http://img.shields.io/pypi/v/mutagen-helper.svg)](https://pypi.python.org/pypi/mutagen-helper)
![MIT License](http://img.shields.io/badge/license-MIT-blue.svg)
[![Build Status](http://img.shields.io/travis/gfi-centre-ouest/mutagen-helper.svg)](https://travis-ci.org/gfi-centre-ouest/mutagen-helper)
[![Coveralls](http://img.shields.io/coveralls/gfi-centre-ouest/mutagen-helper.svg)](https://coveralls.io/github/gfi-centre-ouest/mutagen-helper?branch=develop)

Mutagen Helper allow you to define [Mutagen](https://mutagen.io/) synchronisation sessions inside `.mutagen.yml` 
files on directories you want to synchronise.

Install
-------

- Download binaries right from [github release pages](https://github.com/gfi-centre-ouest/mutagen-helper/releases)

or

- run `pip install mutagen-helper` on Python 3.6+

Quickstart
----------

- Install mutagen as usual, and make it available in the user `PATH` or define `MUTAGEN_HELPER_MUTAGEN_BIN` environment 
variable to the path of the mutagen binary as an alternative (ie: `C:\tools\mutagen\mutagen.exe`).

- Create `.mutagen.yml` file inside some local directory you want to synchronize and set `beta` property to the 
destination of the synchronisation.

```yaml
project_name: 'helper-project' # Optional, it will fallback to directory name if not defined
beta: 'vagrant@192.168.1.100:/home/vagrant/projects' # Beta side of the synchronisation
options: # Options can be provided
  sync-mode: two-way-resolved
  default-file-mode-beta: 664
  default-directory-mode-beta: 775
  ignore-vcs: True
  ignore:
    - node_modules/
    - vendor/
```

*important note: mutagen-helper automatically appends the `project_name` to the beta definition. It means that this
directory will be synchronised to /home/vagrant/projects/helper-project*.

- Run `mutagen-helper up` from the project directory.

- Run `mutagen-helper list` to see which sessions are running on which projects. Output match `mutagen list` command
output, but as JSON and with `Project name` and `Name` additional properties.

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
        |- .mutagen.yml
        |- ...
    |- project2
        |- .mutagen.yml
        |- ...
    |- project3
        |- .mutagen.yml
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

Those command will create all mutagen sessions defined in `.mutagen.yml` of each subdirectories of `C:\workspace`.

Advanced configuration
----------------------

You may use environment variable expansion, with `${VARIABLE}` syntax like in bash.

Your may also define multiple sessions under a `sessions` key. Properties defined at root of the configuration file 
will be inherited by each session.

You may also give names to sessions for them to be identified with precision, but keep in mind that changing name
on running sessions could cause problem as they are used to find out the real mutagen session id.

```
beta: '${DOCKER_DEVBOX_URL}:/home/vagrant/projects'
sessions:
  - options:
      name: 'partial-watch-alpha'
      sync-mode: two-way-resolved
      default-file-mode-beta: 664
      default-directory-mode-beta: 775
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
      max-staging-file-size: 1MB
      watch-mode: no-watch
```

Some properties have default values.

  - `alpha`
    - `MUTAGEN_HELPER_ALPHA` environment variable, *or*
    - Directory when the `.mutagen.yml` resides
  - `beta`: 
    - `MUTAGEN_HELPER_BETA` environment variable, *or*
    - mandatory in the `.mutagen.yml`
  - `append_project_name_to_beta`: 
    - `MUTAGEN_HELPER_APPEND_PROJECT_NAME_TO_BETA`, *or*
    -  `True`