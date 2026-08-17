import click

from flask.cli import with_appcontext

from .habref_v7 import import_v07, apply_v07

import logging

logger = logging.getLogger("habref_commands")


@click.group(help="Manager HabRef referentials.")
def habref():
    pass


habref.add_command(import_v07)
habref.add_command(apply_v07)
