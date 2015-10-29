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

"""Claimant fixtures."""

import glob
import json
import os

import pytest
from flask import current_app
from jsonschema import ValidationError

from claimstore.app import db
from claimstore.core.json import validate_json
from claimstore.modules.claims.models import Claimant


def create_claimant(claimant_json):
    """Insert a claimant in the database."""
    if not Claimant.query.filter_by(name=claimant_json['name']).first():
        claimant = Claimant(**claimant_json)
        db.session.add(claimant)
    db.session.commit()


def load_all_claimants(config_path=None):
    """Fixture that loads all test claimants."""
    if config_path:
        claimants_filepath = os.path.join(
            config_path,
            'claimants'
        )
    else:
        claimants_filepath = os.path.join(
            current_app.config['BASE_DIR'],
            'tests',
            'myclaimstore',
            'config',
            'claimants'
        )
    for claimant_fp in glob.glob("{}/*.json".format(claimants_filepath)):
        with open(claimant_fp) as f:
            json_data = json.load(f)
            try:
                validate_json(json_data, 'claims.claimant')
            except ValidationError:
                print(
                    '`{}` could not be loaded. It does not follow the proper '
                    'JSON schema specification.'.format(claimant_fp)
                )
                continue
            create_claimant(json_data)


@pytest.fixture
def dummy_claimant():
    """Fixture that creates a dummy claimant."""
    return {
        "name": "dummy_claimant",
        "url": "http://dummy.net",
        "persistent_identifiers": [
            {
                "type": "CDS_RECORD_ID",
                "description": "CDS record",
                "url": "http://cds.cern.ch/record/<CDS_RECORD_ID>",
                "example_value": "123",
                "example_url": "http://cds.cern.ch/record/123"
            },
            {
                "type": "CDS_REPORT_NUMBER",
                "description": "CDS report number",
                "url": "http://cds.cern.ch/report/<CDS_REPORT_NUMBER>",
                "example_value": "CMS-PAS-HIG-14-008",
                "example_url": "http://cds.cern.ch/report/CMS-PAS-HIG-14-008"
            }
        ]
    }


@pytest.fixture
def create_dummy_claimant(webtest_app, dummy_claimant):
    """Add dummy claimant to the database."""
    webtest_app.post_json(
        '/subscribe',
        dummy_claimant
    )


@pytest.fixture
def all_claimants(db):
    """Fixture that loads all claimants."""
    load_all_claimants()
