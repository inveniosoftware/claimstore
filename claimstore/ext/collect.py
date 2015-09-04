
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

"""Flask-Collect extension."""

import click
from flask import current_app
from flask_cli import with_appcontext
from flask_collect import Collect


@click.command()
@click.option('-v', '--verbose', default=False, is_flag=True)
@with_appcontext
def collect(verbose=False):
    """Collect static files."""
    current_app.extensions['collect'].collect(verbose=verbose)


def setup_app(app):
    """Initialize Menu."""
    def filter_(items):
        """Filter application blueprints."""
        order = [blueprint.name for blueprint in
                 app.extensions['registry']['blueprints']]

        def _key(item):
            if item.name in order:
                return order.index(item.name)
            return -1

        return sorted(items, key=_key)

    app.config.setdefault('COLLECT_FILTER', filter_)
    app.config.setdefault('COLLECT_STATIC_ROOT', app.static_folder)
    app.config.setdefault('COLLECT_STORAGE', 'flask_collect.storage.link')

    ext = Collect(app)

    # unsetting the static_folder so it's not picked up by collect.
    class FakeApp(object):
        name = "fakeapp"
        has_static_folder = False
        static_folder = None

    ext.app = FakeApp()

    app.cli.add_command(collect)
