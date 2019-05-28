#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main module
"""
import json
import logging
import sys

import click

from mutagen_helper.__version__ import __version__
from mutagen_helper.manager import Manager


class SpecialHelpOrder(click.Group):
    def __init__(self, *args, **kwargs):
        self.help_priorities = {}
        super(SpecialHelpOrder, self).__init__(*args, **kwargs)

    def get_help(self, ctx):
        self.list_commands = self.list_commands_for_help
        return super(SpecialHelpOrder, self).get_help(ctx)

    def list_commands_for_help(self, ctx):
        """reorder the list of commands when listing the help"""
        commands = super(SpecialHelpOrder, self).list_commands(ctx)
        return (c[1] for c in sorted(
            (self.help_priorities.get(command, 1), command)
            for command in commands))

    def command(self, *args, **kwargs):
        """Behaves the same as `click.Group.command()` except capture
        a priority for listing command names in help.
        """
        help_priority = kwargs.pop('help_priority', 1)
        help_priorities = self.help_priorities

        def decorator(f):
            cmd = super(SpecialHelpOrder, self).command(*args, **kwargs)(f)
            help_priorities[cmd.name] = help_priority
            return cmd

        return decorator


@click.group(context_settings=dict(help_option_names=['-h', '--help']), cls=SpecialHelpOrder)
@click.version_option(prog_name='mutagen-helper', version=__version__)
@click.option('-v', '--verbose', default=False, is_flag=True, help="Add more output")
@click.option('-s', '--silent', default=False, is_flag=True, help="No output at all")
def main(verbose, silent):
    """
    Main command group
    :return:
    """
    if not silent:
        root = logging.getLogger()
        if verbose:
            root.setLevel(logging.DEBUG)
        else:
            root.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)


@main.command(help='Creates and starts a new synchronization sessions', help_priority=1)
@click.argument('project', required=False)
@click.argument('session', required=False)
@click.option('-p', '--path', required=False)
def up(path=None, project=None, session=None):
    manager = Manager()
    manager.up(path, project, session)


@main.command(help='Permanently terminates synchronization sessions', help_priority=2)
@click.argument('project', required=False)
@click.argument('session', required=False)
@click.option('-p', '--path', required=False)
def down(path=None, project=None, session=None):
    manager = Manager()
    manager.down(path, project, session)


@main.command(help='Pauses synchronization sessions', help_priority=3)
@click.argument('project', required=False)
@click.argument('session', required=False)
@click.option('-p', '--path', required=False)
def pause(path=None, project=None, session=None):
    manager = Manager()
    manager.pause(path, project, session)


@main.command(help='Resumes paused or disconnected synchronization sessions', help_priority=4)
@click.argument('project', required=False)
@click.argument('session', required=False)
@click.option('-p', '--path', required=False)
def resume(path=None, project=None, session=None):
    manager = Manager()
    manager.resume(path, project, session)


@main.command(help='Flush synchronization sessions', help_priority=4)
@click.argument('project', required=False)
@click.argument('session', required=False)
@click.option('-p', '--path', required=False)
def flush(path=None, project=None, session=None):
    manager = Manager()
    manager.flush(path, project, session)


@main.command(help='Lists existing synchronization sessions and their statuses', help_priority=5)
@click.argument('project', required=False)
@click.argument('session', required=False)
@click.option('-p', '--path', required=False)
@click.option('-l', '--long', required=False, is_flag=True)
def list(project=None, session=None, path=None, long=False):
    manager = Manager()
    ret = manager.list(path, project, session, long)
    print(json.dumps(ret, indent=2))


if __name__ == '__main__':
    main()
