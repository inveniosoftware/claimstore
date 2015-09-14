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

"""Predicate fixtures."""

import glob
import json
import os

import pytest
from flask import current_app
from jsonschema import ValidationError

from claimstore.core.json import validate_json
from claimstore.ext.sqlalchemy import db
from claimstore.modules.claims.models import Predicate


def create_predicate(pred_json):
    """Insert a predicate in the database."""
    if not Predicate.query.filter_by(name=pred_json['name']).first():
        predicate = Predicate(**pred_json)
        db.session.add(predicate)
    db.session.commit()


def load_all_predicates(config_path=None):
    """Populate all predicates."""
    if config_path:
        predicates_filepath = os.path.join(
            config_path,
            'predicates'
        )
    else:
        predicates_filepath = os.path.join(
            current_app.config['BASE_DIR'],
            'tests',
            'myclaimstore',
            'config',
            'predicates'
        )
    for pred_fp in glob.glob("{}/*.json".format(predicates_filepath)):
        with open(pred_fp) as f:
            json_data = json.load(f)
            try:
                validate_json(json_data, 'claims.predicate')
            except ValidationError:
                print('`{}` could not be loaded. It does not follow the proper'
                      ' JSON schema specification.'.format(pred_fp))
                continue
            create_predicate(json_data)


@pytest.fixture
def all_predicates(db):
    """Fixture that loads all predicates."""
    load_all_predicates()
