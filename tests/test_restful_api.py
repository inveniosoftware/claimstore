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

"""claimstore.modules.claims.restful test suite.

isort:skip_file
"""

from webtest import TestApp

from claimstore.modules.claims.fixtures.claim import dummy_claim, \
    load_all_claims
from claimstore.modules.claims.fixtures.claimant import dummy_claimant, \
    load_all_claimants
from claimstore.modules.claims.fixtures.pid import load_all_pids
from claimstore.modules.claims.fixtures.predicate import load_all_predicates

from .base import ClaimStoreTestCase


class PutRestfulAPITestCase(ClaimStoreTestCase):

    """Testing PUT requests from claimstore.modules.claims.restful."""

    def setUp(self):
        """Set up."""
        super(PutRestfulAPITestCase, self).setUp()

        with self.app.app_context():
            self.test_app = TestApp(
                self.app,
                extra_environ=dict(REMOTE_ADDR='127.0.0.1')
            )
            load_all_predicates()

    def test_put_claimant(self):
        """Testing `subscribe` api."""
        resp = self.test_app.post_json(
            '/subscribe',
            dummy_claimant()
        )
        self.assertEqual(resp.status_code, 200)

        # Re-adding the same claimant should fail.
        resp = self.test_app.post_json(
            '/subscribe',
            dummy_claimant(),
            expect_errors=True
        )
        self.assertEqual(resp.status_code, 400)

    def test_put_claim(self):
        """Testing POST to `claims` api."""
        # Firstly we need a claimant, so the claim submission should fail.
        resp = self.test_app.post_json(
            '/claims',
            dummy_claim(),
            expect_errors=True
        )
        self.assertEqual(resp.status_code, 400)

        # Test when there is a claimant.
        self.test_app.post_json(
            '/subscribe',
            dummy_claimant()
        )
        resp = self.test_app.post_json(
            '/claims',
            dummy_claim()
        )
        self.assertEqual(resp.status_code, 200)


class GetRestfulAPITestCase(ClaimStoreTestCase):

    """Testing GET request form claimstore.modules.claims.restful."""

    def setUp(self):
        """Set up."""
        super(GetRestfulAPITestCase, self).setUp()

        with self.app.app_context():
            self.test_app = TestApp(
                self.app,
                extra_environ=dict(REMOTE_ADDR='127.0.0.1')
            )
            self._populate_all()

    def _populate_all(self):
        """Populate database for searching tests."""
        load_all_predicates()
        load_all_pids()
        load_all_claimants()
        load_all_claims(self.test_app)

    def test_get_claims(self):
        """Testing GET claims api."""
        resp = self.test_app.get('/claims')
        self.assertEqual(resp.status_code, 200)

    def test_get_claims_by_claimant(self):
        """Testing GET claims filtering by claimant."""
        # There are 1 CDS claim and 2 INSPIRE claims
        resp = self.test_app.get('/claims')
        self.assertEqual(len(resp.json), 3)
        resp = self.test_app.get('/claims?claimant=CDS')
        self.assertEqual(len(resp.json), 1)
        resp = self.test_app.get('/claims?claimant=INSPIRE')
        self.assertEqual(len(resp.json), 2)

    def test_get_claims_by_predicate(self):
        """Testing GET claims filtering by predicate."""
        # There are 2 claims is_same_as and 1 is_variant_of
        resp = self.test_app.get('/claims')
        self.assertEqual(len(resp.json), 3)
        resp = self.test_app.get('/claims?predicate=is_same_as')
        self.assertEqual(len(resp.json), 2)
        resp = self.test_app.get('/claims?predicate=is_variant_of')
        self.assertEqual(len(resp.json), 1)

    def test_get_claims_by_certainty(self):
        """Testing GET claims filtering by certainty."""
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
        # There are 2 human reported claims and 1 by an algorithm.
        resp = self.test_app.get('/claims?human=0')
        self.assertEqual(len(resp.json), 1)
        resp = self.test_app.get('/claims?human=1')
        self.assertEqual(len(resp.json), 2)

    def test_get_claims_by_actor(self):
        """Testing GET claims filtering by actor."""
        # There are 2 actors: John Doe (2 times) and CDS_submission (1).
        resp = self.test_app.get('/claims?actor=John%')
        self.assertEqual(len(resp.json), 2)
        resp = self.test_app.get('/claims?actor=CDS%sub%')
        self.assertEqual(len(resp.json), 1)

    def test_get_claims_by_type_value(self):
        """Testing GET claims filtering by type."""
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
        resp = self.test_app.get('/identifiers')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 7)

    def test_get_predicates(self):
        """Testing GET predicates api."""
        resp = self.test_app.get('/predicates')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json), 5)
