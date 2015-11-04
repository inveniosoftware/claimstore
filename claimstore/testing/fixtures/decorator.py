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

"""Fixture decorators."""

import pytest


def populate_all(f):
    """Simple decorator to populate db."""
    return pytest.mark.usefixtures(
        'all_predicates',
        'all_pids',
        'all_claimants',
        'all_claims'
    )(f)


def populate_all_and_dummy_claimant(f):
    """Simple decorator to populate db, including a dummy claimant."""
    return pytest.mark.usefixtures(
        'all_predicates',
        'all_pids',
        'all_claimants',
        'all_claims',
        'create_dummy_claimant'
    )(f)
