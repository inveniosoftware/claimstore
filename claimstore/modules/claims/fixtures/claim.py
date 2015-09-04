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

"""Claim fixtures."""

import json
import os

import pytest

CLAIM_CDS1_FN = 'claim.cds.1.json'
CLAIM_INSPIRE1_FN = 'claim.inspire.1.json'
CLAIM_INSPIRE2_FN = 'claim.inspire.2.json'


@pytest.fixture
def load_claim(app, json_filename=CLAIM_CDS1_FN):
    """Fixture that returns the JSON data representing a claim."""
    with open(os.path.join(
        app.config['BASE_DIR'],
        'claimstore',
        'modules',
        'claims',
        'static',
        'json',
        'examples',
        json_filename
    )) as f:
        return json.loads(f.read())


@pytest.fixture
def create_claim(test_app, json_filename=CLAIM_CDS1_FN):
    """Fixture that creates a claim."""
    test_app.post_json(
        '/claims',
        load_claim(test_app.app, json_filename)
    )
