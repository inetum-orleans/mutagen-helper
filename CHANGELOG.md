Changelog
=======

<!--next-version-placeholder-->

## v2.0.0 (2021-04-19)
### Feature
* Add support for mutagen v0.12 ([#16](https://github.com/inetum-orleans/mutagen-helper/issues/16)) ([`7b4917d`](https://github.com/inetum-orleans/mutagen-helper/commit/7b4917d5bfaba2d8243730f4d3f2d899d6540188))

### Fix
* **wrapper:** Do not buffer subprocess ([`caf49df`](https://github.com/inetum-orleans/mutagen-helper/commit/caf49dfaa9ec0304c1fda56c634dd73ccd5d3384))
* **readme:** Add readme to project configuration ([`e48212c`](https://github.com/inetum-orleans/mutagen-helper/commit/e48212cd72138bbc3c673072b77de2f9212de2c6))

### Breaking
* support for mutagen v0.9 and below has been dropped. ([`7b4917d`](https://github.com/inetum-orleans/mutagen-helper/commit/7b4917d5bfaba2d8243730f4d3f2d899d6540188))

## v1.2.0 (2021-03-30)
### Feature
* Better packaging, semantic release, github actions ([`48e8408`](https://github.com/inetum-orleans/mutagen-helper/commit/48e840847f942382d5887a85878b87fbc4d264e4))

1.1.0 (2019-07-29)
------------------

- Add support for mutagen `0.10.0`.
- Rename configuration file from `mutagen.yml` to `mutagen-helper.yml`.

1.0.0 (2019-06-14)
------------------

- Fix session being creating on root directory when `auto_configure` is enabled and no project is found (show an error
  message to the user)

1.0.0rc3 (2019-05-28)
---------------------

- Add project and session optional arguments to `up` command

1.0.0rc2 (2019-05-28)
---------------------

- Use auto configure `include` and `exclude` when loading project configuration file
- auto configure `include` now has priority over `exclude`

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
- Add support for YAML configuration files without dot (`mutagen.yml`
  and `mutagen.yaml`) ([#3](https://github.com/gfi-centre-ouest/mutagen-helper/issues/3))

1.0.0a2 (2019-05-25)
--------------------

- Enhance error handling of mutagen commands ([#5](https://github.com/gfi-centre-ouest/mutagen-helper/issues/5))
- Add support of user input for underlying mutagen
  commands ([#6](https://github.com/gfi-centre-ouest/mutagen-helper/issues/6))

1.0.0a1 (2019-05-23)
--------------------

- First release
