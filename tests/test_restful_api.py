# -*- coding: utf-8 -*-
#
# This file is part of ClaimStore.
# Copyright (C) 2015 CERN.
#
# ClaimStore is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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

"""claimstore.modules.claims.restful test suite."""

import json
import os

import pytest  # isort:skip
from webtest import TestApp  # isort:skip

from .base import ClaimStoreTestCase  # isort:skip


@pytest.fixture(scope='module')
def claimant_example(app):
    """Fixture that returns a JSON example of a claimant."""
    with open(os.path.join(
        app.config['BASE_DIR'],
        'claimstore',
        'static',
        'json',
        'examples',
        'claimant.cds.json'
    )) as f:
        return json.loads(f.read())


@pytest.fixture(scope='module')
def claim_example(app):
    """Fixture that returns a JSON example of a claim."""
    with open(os.path.join(
        app.config['BASE_DIR'],
        'claimstore',
        'static',
        'json',
        'examples',
        'claim.cds.1.json'
    )) as f:
        return json.loads(f.read())


class RestfulAPITestCase(ClaimStoreTestCase):

    """Testing claimstore.modules.claims.restful."""

    def setUp(self):
        """Set up."""
        super(RestfulAPITestCase, self).setUp()

        with self.app.app_context():
            self.test_app = TestApp(self.app)

    def test_submit_claimant(self):
        """Testing `subscribe` api."""
        resp = self.test_app.post_json(
            '/subscribe',
            claimant_example(self.app)
        )
        self.assertEqual(resp.status_code, 200)

    def test_submit_claim(self):
        """Testing POST to `claims` api."""
        # Firstly we need a claimant, so the claim submission should fail.
        resp = self.test_app.post_json(
            '/claims',
            claim_example(self.app),
            expect_errors=True
        )
        self.assertEqual(resp.status_code, 400)

        # Test when there is a claimant.
        resp = self.test_app.post_json(
            '/subscribe',
            claimant_example(self.app)
        )
        resp = self.test_app.post_json(
            '/claims',
            claim_example(self.app)
        )
        self.assertEqual(resp.status_code, 200)

    def test_get_claims(self):
        """Testing GET claims api."""
        resp = self.test_app.get('/claims')
        self.assertEqual(resp.status_code, 200)
