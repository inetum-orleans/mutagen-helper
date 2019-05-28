History
=======

1.0.0rc1 (2019-05-28)
---------------------

- Add support for many projects in the same configuration file
- Add auto configuration support to create sessions from subdirectories with no configuration file
- Add `MUTAGEN_HELPER_PATH` environment variable

1.0.0b4 (2019-05-27)
--------------------

- Add missing [expandvars](https://github.com/sayanarijit/expandvars) dependency
- Remove [tinydb](https://github.com/msiemens/tinydb) dependency


1.0.0b3 (2019-05-27)
--------------------

- Add default value support for environment expansion replacements, with 
[expandvars](https://github.com/sayanarijit/expandvars)
- Upgrade list command to support short and long listing (`--long` option)


1.0.0b2 (2019-05-27)
--------------------

- Add `project` and `session` arguments to commands
- Fix stuck sessions on `up` command because of invalid stdin/stdout support
- Fix missing project name in output
- Remove dead code

1.0.0b1 (2019-05-27)
--------------------

- Use labels feature introduced in mutagen 
[v0.9.0-beta2](https://github.com/havoc-io/mutagen/releases/tag/v0.9.0-beta2). There's no local database anymore 
(`~/.mutagen-helper` directory can be removed) ([#4](https://github.com/gfi-centre-ouest/mutagen-helper/issues/4))
- Add support for YAML configuration files without dot (`mutagen.yml` and `mutagen.yaml`) ([#3](https://github.com/gfi-centre-ouest/mutagen-helper/issues/3))


1.0.0a2 (2019-05-25)
--------------------

- Enhance error handling of mutagen commands ([#5](https://github.com/gfi-centre-ouest/mutagen-helper/issues/5))
- Add support of user input for underlying mutagen commands ([#6](https://github.com/gfi-centre-ouest/mutagen-helper/issues/6))

1.0.0a1 (2019-05-23)
--------------------

- First release
