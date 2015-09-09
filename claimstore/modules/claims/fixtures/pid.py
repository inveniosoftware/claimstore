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

"""Persistent identifiers fixtures."""

import glob
import json
import os

import pytest
from flask import current_app

from claimstore.ext.sqlalchemy import db
from claimstore.modules.claims.models import IdentifierType


@pytest.fixture
def create_pid(pid_json):
    """Insert an identifier in the database."""
    pid_json['name'] = pid_json.pop('type')
    if not IdentifierType.query.filter_by(name=pid_json['name']).first():
        identifier = IdentifierType(**pid_json)
        db.session.add(identifier)
    db.session.commit()


@pytest.fixture
def load_all_pids(config_path=None):
    """Populate all persistent identifiers."""
    if config_path:
        pids_filepath = os.path.join(
            config_path,
            'pids'
        )
    else:
        pids_filepath = os.path.join(
            current_app.config['BASE_DIR'],
            'tests',
            'myclaimstore',
            'config',
            'pids'
        )
    for pid_fp in glob.glob("{}/*.json".format(pids_filepath)):
        with open(pid_fp) as f:
            create_pid(json.loads(f.read()))
