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


JSON_EXAMPLES_PATH = os.path.join(
    'claimstore',
    'static',
    'json',
    'examples'
)


@pytest.fixture(scope='module')
def claimant_example_cds(app):
    """Fixture that returns a JSON example of a claimant."""
    with open(os.path.join(
        app.config['BASE_DIR'],
        JSON_EXAMPLES_PATH,
        'claimant.cds.json'
    )) as f:
        return json.loads(f.read())


@pytest.fixture(scope='module')
def claimant_example_inspire(app):
    """Fixture that returns a JSON example of a claimant."""
    with open(os.path.join(
        app.config['BASE_DIR'],
        JSON_EXAMPLES_PATH,
        'claimant.inspire.json'
    )) as f:
        return json.loads(f.read())


@pytest.fixture(scope='module')
def claim_example_cds(app):
    """Fixture that returns a JSON example of a claim."""
    with open(os.path.join(
        app.config['BASE_DIR'],
        JSON_EXAMPLES_PATH,
        'claim.cds.1.json'
    )) as f:
        return json.loads(f.read())


@pytest.fixture(scope='module')
def claim_example_isnpire_1(app):
    """Fixture that returns a JSON example of a claim."""
    with open(os.path.join(
        app.config['BASE_DIR'],
        JSON_EXAMPLES_PATH,
        'claim.inspire.1.json'
    )) as f:
        return json.loads(f.read())


@pytest.fixture(scope='module')
def claim_example_isnpire_2(app):
    """Fixture that returns a JSON example of a claim."""
    with open(os.path.join(
        app.config['BASE_DIR'],
        JSON_EXAMPLES_PATH,
        'claim.inspire.2.json'
    )) as f:
        return json.loads(f.read())


class RestfulAPITestCase(ClaimStoreTestCase):

    """Testing claimstore.modules.claims.restful."""

    def setUp(self):
        """Set up."""
        super(RestfulAPITestCase, self).setUp()

        with self.app.app_context():
            self.test_app = TestApp(self.app)

    def _populate_for_search(self):
        """Populate database for searching tests."""
        # Adding 2 claimants
        self.test_app.post_json(
            '/subscribe',
            claimant_example_cds(self.app)
        )
        self.test_app.post_json(
            '/subscribe',
            claimant_example_inspire(self.app)
        )
        # Adding 3 claims (1 CDS, 2 INSPIRE)
        self.test_app.post_json(
            '/claims',
            claim_example_cds(self.app)
        )
        self.test_app.post_json(
            '/claims',
            claim_example_isnpire_1(self.app)
        )
        self.test_app.post_json(
            '/claims',
            claim_example_isnpire_2(self.app)
        )

    def test_submit_claimant(self):
        """Testing `subscribe` api."""
        resp = self.test_app.post_json(
            '/subscribe',
            claimant_example_cds(self.app)
        )
        self.assertEqual(resp.status_code, 200)

        # Re-adding the same claimant should fail.
        resp = self.test_app.post_json(
            '/subscribe',
            claimant_example_cds(self.app),
            expect_errors=True
        )
        self.assertEqual(resp.status_code, 400)

    def test_submit_claim(self):
        """Testing POST to `claims` api."""
        # Firstly we need a claimant, so the claim submission should fail.
        resp = self.test_app.post_json(
            '/claims',
            claim_example_cds(self.app),
            expect_errors=True
        )
        self.assertEqual(resp.status_code, 400)

        # Test when there is a claimant.
        resp = self.test_app.post_json(
            '/subscribe',
            claimant_example_cds(self.app)
        )
        resp = self.test_app.post_json(
            '/claims',
            claim_example_cds(self.app)
        )
        self.assertEqual(resp.status_code, 200)

    def test_get_claims(self):
        """Testing GET claims api."""
        resp = self.test_app.get('/claims')
        self.assertEqual(resp.status_code, 200)

    def test_get_claims_by_claimant(self):
        """Testing GET claims filtering by claimant."""
        self._populate_for_search()
        # There are 1 CDS claim and 2 INSPIRE claims
        resp = self.test_app.get('/claims')
        self.assertEqual(len(resp.json), 3)
        resp = self.test_app.get('/claims?claimant=CDS')
        self.assertEqual(len(resp.json), 1)
        resp = self.test_app.get('/claims?claimant=INSPIRE')
        self.assertEqual(len(resp.json), 2)

    def test_get_claims_by_predicate(self):
        """Testing GET claims filtering by predicate."""
        self._populate_for_search()
        # There are 2 claims is_same_as and 1 is_cited_by
        resp = self.test_app.get('/claims')
        self.assertEqual(len(resp.json), 3)
        resp = self.test_app.get('/claims?predicate=is_same_as')
        self.assertEqual(len(resp.json), 2)
        resp = self.test_app.get('/claims?predicate=is_cited_by')
        self.assertEqual(len(resp.json), 1)

    def test_get_claims_by_certainty(self):
        """Testing GET claims filtering by certainty."""
        self._populate_for_search()
        # There are 3 claims with: 0.5, 0.8 and 1 as certainty.
        resp = self.test_app.get('/claims?certainty=0.1')
        self.assertEqual(len(resp.json), 3)
        resp = self.test_app.get('/claims?certainty=0.5')
        self.assertEqual(len(resp.json), 3)
        resp = self.test_app.get('/claims?certainty=0.8')
        self.assertEqual(len(resp.json), 2)
        resp = self.test_app.get('/claims?certainty=1')
        self.assertEqual(len(resp.json), 1)

    def test_get_claims_by_c(self):
        """Testing GET claims filtering by certainty."""
        self._populate_for_search()
        # There are 3 claims with: 0.5, 0.8 and 1 as certainty.
        resp = self.test_app.get('/claims?certainty=0.1')
        self.assertEqual(len(resp.json), 3)
        resp = self.test_app.get('/claims?certainty=0.5')
        self.assertEqual(len(resp.json), 3)
        resp = self.test_app.get('/claims?certainty=0.8')
        self.assertEqual(len(resp.json), 2)
        resp = self.test_app.get('/claims?certainty=1')
        self.assertEqual(len(resp.json), 1)

    def test_get_claims_by_human(self):
        """Testing GET claims filtering by human."""
        self._populate_for_search()
        # There are 2 human reported claims and 1 by an algorithm.
        resp = self.test_app.get('/claims?human=0')
        self.assertEqual(len(resp.json), 1)
        resp = self.test_app.get('/claims?human=1')
        self.assertEqual(len(resp.json), 2)

    def test_get_claims_by_actor(self):
        """Testing GET claims filtering by actor."""
        self._populate_for_search()
        # There are 2 actors: John Doe (2 times) and CDS_submission (1).
        resp = self.test_app.get('/claims?actor=John%')
        self.assertEqual(len(resp.json), 2)
        resp = self.test_app.get('/claims?actor=CDS%sub%')
        self.assertEqual(len(resp.json), 1)

    def test_get_claims_by_type_value(self):
        """Testing GET claims filtering by type."""
        self._populate_for_search()
        # There are 2 CDS_RECORD_ID, one as subject and one as an object.
        resp = self.test_app.get('/claims?type=CDS_RECORD_ID')
        self.assertEqual(len(resp.json), 2)
        # The type with value `2001192` can be found 1 times.
        resp = self.test_app.get('/claims?value=2001192')
        self.assertEqual(len(resp.json), 1)
        # Filter by type and value
        resp = self.test_app.get('/claims?type=CDS_RECORD_ID&value=2001192')
        self.assertEqual(len(resp.json), 1)

    def test_get_claims_by_subject_object(self):
        """Testing GET claims filtering by subject/object."""
        self._populate_for_search()
        resp = self.test_app.get('/claims?subject=CDS_RECORD_ID')
        self.assertEqual(len(resp.json), 1)
        resp = self.test_app.get('/claims?object=CDS_REPORT_NUMBER')
        self.assertEqual(len(resp.json), 1)
        resp = self.test_app.get(
            '/claims?subject=CDS_RECORD_ID&object=CDS_REPORT_NUMBER'
        )
        self.assertEqual(len(resp.json), 1)

    def test_get_identifiers(self):
        """Testing GET identifiers api."""
        self._populate_for_search()
        resp = self.test_app.get('/identifiers')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 7)
