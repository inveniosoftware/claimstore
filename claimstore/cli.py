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

"""CLI factory."""

from __future__ import absolute_import

import click
from flask_cli import FlaskGroup
from flask_collect import Collect

from claimstore.app import create_app
from claimstore.modules.claims.cli import database_cli, eqid_cli


def clifactory():
    """Create a click CLI application based on configuration.

    :param create_app: Flask application factory function.
    """
    # Create application object without loading the full application.
    app = create_app()

    def create_cli_app(info):
        return app

    @click.group(cls=FlaskGroup, create_app=create_cli_app)
    def cli(**params):
        pass

    # Register CLI modules from packages.
    cli.add_command(database_cli)
    cli.add_command(eqid_cli)

    # Collect
    app.config.setdefault('COLLECT_STATIC_ROOT', app.static_folder)
    app.config.setdefault('COLLECT_STORAGE', 'flask_collect.storage.link')
    collect = Collect(app)

    @cli.command('collect')
    def collect_cli():
        """Collect static files."""
        collect.collect(verbose=True)

    return cli


cli = clifactory()
