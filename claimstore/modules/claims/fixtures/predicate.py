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

import pytest

from claimstore.ext.sqlalchemy import db
from claimstore.modules.claims.models import Predicate


@pytest.fixture
def create_predicate(pred_name='is_same_as'):
    """Insert a predicate in the database."""
    if not Predicate.query.filter_by(name=pred_name).first():
        predicate = Predicate(name=pred_name)
        db.session.add(predicate)
    db.session.commit()


@pytest.fixture
def create_all_predicates():
    """Populate all predicates."""
    predicates = [
        'is_same_as',
        'is_different_than',
        'is_erratum_of',
        'is_superseded_by',
        'is_cited_by',
        'is_software_for',
        'is_dataset_for'
    ]
    for pred in predicates:
        create_predicate(pred)
