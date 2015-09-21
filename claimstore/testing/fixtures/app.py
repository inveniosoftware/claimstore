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

"""App fixtures."""

import pytest
from click.testing import CliRunner
from flask_cli.cli import ScriptInfo
from webtest import TestApp

from claimstore.app import create_app


@pytest.yield_fixture(scope='session', autouse=True)
def app():
    """Create the flask app."""
    app_ = create_app()
    with app_.app_context():
        yield app_


@pytest.fixture(scope='session')
def webtest_app(app):
    """Create webtest TestApp."""
    return TestApp(
        app,
        extra_environ=dict(REMOTE_ADDR='127.0.0.1')
    )


@pytest.fixture(scope='session')
def cli_runner(app):
    """Create a cli runner."""
    def cli_invoke(command, args, input=None):
        # Testing click applications which needs the Flask app context requires
        # you to manually create a ScriptInfo object
        obj = ScriptInfo(create_app=lambda x: app)
        return CliRunner().invoke(command, args, input=input, obj=obj)
    return cli_invoke
