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

"""claimstore.modules.claims.restful test suite."""

import pytest

from claimstore.modules.claims.fixtures.decorator import populate_all

pytest_plugins = (
    'claimstore.modules.claims.fixtures.claim',
    'claimstore.modules.claims.fixtures.claimant',
    'claimstore.modules.claims.fixtures.pid',
    'claimstore.modules.claims.fixtures.predicate'
)


@pytest.mark.usefixtures('all_predicates')
def test_put_claimant(webtest_app, dummy_claimant):
    """Testing `subscribe` api."""
    resp = webtest_app.post_json(
        '/subscribe',
        dummy_claimant
    )
    assert resp.status_code == 200

    # Re-adding the same claimant should fail.
    resp = webtest_app.post_json(
        '/subscribe',
        dummy_claimant,
        expect_errors=True
    )
    assert resp.status_code == 400


@pytest.mark.usefixtures('all_predicates')
def test_put_claim(webtest_app, dummy_claimant, dummy_claim):
    """Testing POST to `claims` api."""
    # Firstly we need a claimant, so the claim submission should fail.
    resp = webtest_app.post_json(
        '/claims',
        dummy_claim,
        expect_errors=True
    )
    assert resp.status_code == 400

    # Test when there is a claimant.
    webtest_app.post_json(
        '/subscribe',
        dummy_claimant
    )
    resp = webtest_app.post_json(
        '/claims',
        dummy_claim
    )
    assert resp.status_code == 200


@populate_all
def test_get_claims(webtest_app):
    """Testing GET claims api."""
    resp = webtest_app.get('/claims')
    assert resp.status_code == 200


@populate_all
def test_get_claims_by_claimant(webtest_app):
    """Testing GET claims filtering by claimant."""
    # There are 1 CDS claim and 2 INSPIRE claims
    resp = webtest_app.get('/claims')
    assert len(resp.json) == 3
    resp = webtest_app.get('/claims?claimant=CDS')
    assert len(resp.json) == 1
    resp = webtest_app.get('/claims?claimant=INSPIRE')
    assert len(resp.json) == 2


@populate_all
def test_get_claims_by_predicate(webtest_app):
    """Testing GET claims filtering by predicate."""
    # There are 2 claims is_same_as and 1 is_variant_of
    resp = webtest_app.get('/claims')
    assert len(resp.json) == 3
    resp = webtest_app.get('/claims?predicate=is_same_as')
    assert len(resp.json) == 2
    resp = webtest_app.get('/claims?predicate=is_variant_of')
    assert len(resp.json) == 1


@populate_all
def test_get_claims_by_certainty(webtest_app):
    """Testing GET claims filtering by certainty."""
    # There are 3 claims with: 0.5, 0.8 and 1 as certainty.
    resp = webtest_app.get('/claims?certainty=0.1')
    assert len(resp.json) == 3
    resp = webtest_app.get('/claims?certainty=0.5')
    assert len(resp.json) == 3
    resp = webtest_app.get('/claims?certainty=0.8')
    assert len(resp.json) == 2
    resp = webtest_app.get('/claims?certainty=1')
    assert len(resp.json) == 1


@populate_all
def test_get_claims_by_c(webtest_app):
    """Testing GET claims filtering by certainty."""
    # There are 3 claims with: 0.5, 0.8 and 1 as certainty.
    resp = webtest_app.get('/claims?certainty=0.1')
    assert len(resp.json) == 3
    resp = webtest_app.get('/claims?certainty=0.5')
    assert len(resp.json) == 3
    resp = webtest_app.get('/claims?certainty=0.8')
    assert len(resp.json) == 2
    resp = webtest_app.get('/claims?certainty=1')
    assert len(resp.json) == 1


@populate_all
def test_get_claims_by_human(webtest_app):
    """Testing GET claims filtering by human."""
    # There are 2 human reported claims and 1 by an algorithm.
    resp = webtest_app.get('/claims?human=0')
    assert len(resp.json) == 1
    resp = webtest_app.get('/claims?human=1')
    assert len(resp.json) == 2


@populate_all
def test_get_claims_by_actor(webtest_app):
    """Testing GET claims filtering by actor."""
    # There are 2 actors: John Doe (2 times) and CDS_submission (1).
    resp = webtest_app.get('/claims?actor=John%')
    assert len(resp.json) == 2
    resp = webtest_app.get('/claims?actor=CDS%sub%')
    assert len(resp.json) == 1


@populate_all
def test_get_claims_by_type_value(webtest_app):
    """Testing GET claims filtering by type."""
    # There are 2 CDS_RECORD_ID, one as subject and one as an object.
    resp = webtest_app.get('/claims?type=CDS_RECORD_ID')
    assert len(resp.json) == 2
    # The type with value `2003192` can be found 2 times.
    resp = webtest_app.get('/claims?value=2003192')
    assert len(resp.json) == 2
    # Filter by type and value
    resp = webtest_app.get('/claims?type=CDS_RECORD_ID&value=2003192')
    assert len(resp.json) == 2


@populate_all
def test_get_claims_by_type_value_recursive(webtest_app):
    """Testing GET claims filtering by type."""
    resp = webtest_app.get(
        '/claims?type=INSPIRE_RECORD_ID&value=cond-mat/9906097'
    )
    assert len(resp.json) == 1
    resp = webtest_app.get(
        '/claims?type=INSPIRE_RECORD_ID&value=cond-mat/9906097&recurse=1'
    )
    assert len(resp.json) == 2


@populate_all
def test_get_claims_by_subject_object(webtest_app):
    """Testing GET claims filtering by subject/object."""
    resp = webtest_app.get('/claims?subject=CDS_RECORD_ID')
    assert len(resp.json) == 1
    resp = webtest_app.get('/claims?object=CDS_REPORT_NUMBER')
    assert len(resp.json) == 1
    resp = webtest_app.get(
        '/claims?subject=CDS_RECORD_ID&object=CDS_REPORT_NUMBER'
    )
    assert len(resp.json) == 1


@populate_all
def test_get_identifiers(webtest_app):
    """Testing GET identifiers api."""
    resp = webtest_app.get('/identifiers')
    assert resp.status_code == 200
    assert len(resp.json) >= 7


@populate_all
def test_get_predicates(webtest_app):
    """Testing GET predicates api."""
    resp = webtest_app.get('/predicates')
    assert resp.status_code == 200
    assert len(resp.json) == 5


@populate_all
def test_get_eqids(webtest_app):
    """Testing GET eqids api."""
    resp = webtest_app.get('/eqids')
    assert resp.status_code == 200
    assert len(resp.json) >= 2
    eqid = list(resp.json)[0]
    resp = webtest_app.get('/eqids/{}'.format(eqid))
    assert resp.status_code == 200
    assert len(resp.json) == 1
