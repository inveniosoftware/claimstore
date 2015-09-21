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

"""Test click commands for claims module."""

from claimstore.modules.claims import cli
from claimstore.modules.claims.fixtures.decorator import populate_all


def test_database_create(cli_runner, db):
    """Test `claimstore database create` command."""
    # keep `db` parameter to ensure database rollback.
    result = cli_runner(cli.database_cli, ['create'])
    assert result.exit_code == 0
    assert result.output == 'Database initialisation completed.\n'


def test_database_populate(cli_runner, db):
    """Test `claimstore database populate` command."""
    # keep `db` parameter to ensure database rollback.
    result = cli_runner(cli.database_cli, ['populate'])
    assert result.exit_code == 0
    assert result.output.endswith('Database populate completed.\n')


@populate_all
def test_eqid_drop(cli_runner, db):
    """Test `claimstore eqid drop` command."""
    # keep `db` parameter to ensure database rollback.
    result = cli_runner(cli.eqid_cli, ['drop'], input='y')
    assert result.exit_code == 0
    assert result.output.endswith('Index cleared.\n')


@populate_all
def test_eqid_reindex(cli_runner, db):
    """Test `claimstore eqid reindex` command."""
    # keep `db` parameter to ensure database rollback.
    result = cli_runner(cli.eqid_cli, ['reindex'], input='y')
    assert result.exit_code == 0
    assert result.output.endswith('Index rebuilt.\n')
