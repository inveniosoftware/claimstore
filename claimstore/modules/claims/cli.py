# -*- coding: utf-8 -*-
#
# This file is part of ClaimStore.
# Copyright (C) 2015 CERN.
#
# ClaimStore is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# ClaimStore is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ClaimStore; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307,
# USA.

"""CLI commands."""

from pathlib import Path

import click
from flask_cli import with_appcontext

from claimstore.app import db
from claimstore.modules.claims.fixtures.claim import load_all_claims
from claimstore.modules.claims.fixtures.claimant import load_all_claimants
from claimstore.modules.claims.fixtures.pid import load_all_pids
from claimstore.modules.claims.fixtures.predicate import load_all_predicates
from claimstore.modules.claims.models import EquivalentIdentifier


@click.group('database')
@with_appcontext
def database_cli():
    """Database related commands."""
    pass


@database_cli.command()
@click.option('--config', help='Path to a folder with the db configuration')
@with_appcontext
def create(config):
    """Create database and populate it with basic data.

    The database will be populated with the predicates, persistent identifiers
    and claimants that are defined in `tests/myclaimstore/config`. An
    alternative directory can be specified thanks to the argument `--config`.
    """
    if config:
        path = Path(config)
        if not path.exists():
            raise click.BadParameter(
                'The specified config path does not exist.'
            )
        elif not path.is_dir():
            raise click.BadParameter(
                'The specified config path is not a directory.'
            )
        else:
            dirs = set(str(x.name) for x in path.iterdir() if x.is_dir())
            if not set(['predicates', 'pids', 'claimants']).issubset(dirs):
                raise click.BadParameter(
                    'The specified directory must contain three folders: '
                    'predicates, pids and claimants.'
                )
    db.create_all()
    load_all_predicates(config)
    load_all_pids(config)
    load_all_claimants(config)
    click.echo('Database initialisation completed.')


@database_cli.command()
@click.option('--data', help='Path to a folder with data (claims)')
@with_appcontext
def populate(data):
    """Populate database with claims.

    The database will be populated with the claims that are defined in
    `tests/myclaimstore/data`. An alternative directory can be specified
    thanks to the argument `--data`.
    """
    if data:
        path = Path(data)
        if not path.exists():
            raise click.BadParameter(
                'The specified data path does not exist.'
            )
        elif not path.is_dir():
            raise click.BadParameter(
                'The specified data path is not a directory.'
            )
        else:
            dirs = [str(x.name) for x in path.iterdir() if x.is_dir()]
            if 'claims' not in dirs:
                raise click.BadParameter(
                    'The specified directory must contain one folder named:'
                    'claims.'
                )
    try:
        load_all_claims(config_path=data)
        click.echo('Database populate completed.')
    except Exception:
        click.echo(
            'Claims could not be loaded. Try `claimstore database create` '
            'first.'
        )


@database_cli.command()
@with_appcontext
def drop():
    """Drop the whole database."""
    if click.confirm('Are you sure you want to drop the whole database?'):
        db.drop_all()
        click.echo('Database dropped')
    else:
        click.echo('Command aborted')


@click.group('eqid')
@with_appcontext
def eqid_cli():
    """Command providing actions to alter the Equivalent Identifier index."""
    pass


@eqid_cli.command('drop')
@with_appcontext
def drop_eqid():
    """Delete all the entries in the eqid index."""
    if click.confirm('Are you sure to drop the whole index?'):
        EquivalentIdentifier.clear()
        click.echo('Index cleared.')
    else:
        click.echo('Command aborted')


@eqid_cli.command()
@with_appcontext
def reindex():
    """Process all claims to rebuild the eqid index."""
    if click.confirm('Are you sure to reindex eqid?'):
        EquivalentIdentifier.rebuild()
        click.echo('Index rebuilt.')
    else:
        click.echo('Command aborted')
