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

from claimstore.ext.sqlalchemy import db
from claimstore.modules.claims.fixtures.claim import load_all_claims
from claimstore.modules.claims.fixtures.claimant import load_all_claimants
from claimstore.modules.claims.fixtures.pid import load_all_pids
from claimstore.modules.claims.fixtures.predicate import load_all_predicates


@click.command()
@click.option('--config', help='Path to a folder with the db configuration')
@with_appcontext
def initdb(config):
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


@click.command()
@click.option('--data', help='Path to a folder with data (claims)')
@with_appcontext
def populatedb(data):
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
            'Claims could not be loaded. Try `claimstore initdb` first.'
        )


commands = [initdb, populatedb]
