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

"""Tests for equivalent identifiers logic."""

from copy import deepcopy

import pytest
from sqlalchemy.orm.exc import NoResultFound

from claimstore.modules.claims.models import EquivalentIdentifier, \
    IdentifierType

pytest_plugins = (
    'claimstore.modules.claims.fixtures.claim',
    'claimstore.modules.claims.fixtures.claimant',
    'claimstore.modules.claims.fixtures.pid',
    'claimstore.modules.claims.fixtures.predicate'
)


def populate_all(f):
    """Simple decorator to populate db."""
    return pytest.mark.usefixtures(
        'all_predicates',
        'all_pids',
        'all_claimants',
        'all_claims',
        'create_dummy_claimant'
    )(f)


@populate_all
def test_new_equivalence(webtest_app, dummy_claim, dummy_subject,
                         dummy_object):
    """New subject and object.

    Test when the subject and object are not in the equivalent_identifier
    table yet.
    """
    dummy_subject['value'] = 'xxx'
    dummy_object['value'] = 'yyy'

    pre_all_eqs = EquivalentIdentifier.query.all()

    ds_id = IdentifierType.query.filter_by(
        name=dummy_subject['type']
    ).one().id
    do_id = IdentifierType.query.filter_by(
        name=dummy_object['type']
    ).one().id

    # The subject and object types/values do not exist yet:
    with pytest.raises(NoResultFound) as excinfo:
        EquivalentIdentifier.query.filter_by(
            type_id=ds_id,
            value=dummy_subject['value']
        ).one()
        assert 'No row was found for one' in str(excinfo)
        EquivalentIdentifier.query.filter_by(
            type_id=do_id,
            value=dummy_object['value']
        ).one()
        assert 'No row was found for one' in str(excinfo)

    webtest_app.post_json(
        '/claims',
        dummy_claim
    )

    post_all_eqs = EquivalentIdentifier.query.all()
    assert len(pre_all_eqs) + 2 == len(post_all_eqs)

    post_dummy_subject = EquivalentIdentifier.query.filter_by(
        type_id=ds_id,
        value=dummy_subject['value']
    ).one()

    eqs = EquivalentIdentifier.query.filter_by(
        eqid=post_dummy_subject.eqid
    ).all()
    assert len(eqs) == 2


@populate_all
def test_new_subject(webtest_app, dummy_claim, dummy_subject, dummy_object):
    """Test equivalence with a new subject.

    In this case, there is a new claim that will add one extra entry (the
    subject) in the equivalent_identifier table. But the object already exists
    so its eqid will be reused.
    """
    pre_all_eqs = EquivalentIdentifier.query.all()

    # Get 'object' before posting new claim
    do_id = IdentifierType.query.filter_by(
        name=dummy_object['type']
    ).one().id
    pre_dummy_object = EquivalentIdentifier.query.filter_by(
        type_id=do_id,
        value=dummy_object['value']
    ).one()

    # Posting new claim
    webtest_app.post_json(
        '/claims',
        dummy_claim
    )

    post_all_eqs = EquivalentIdentifier.query.all()

    # Get 'subject' after posting new claim
    ds_id = IdentifierType.query.filter_by(
        name=dummy_subject['type']
    ).one().id
    post_dummy_subject = EquivalentIdentifier.query.filter_by(
        type_id=ds_id,
        value=dummy_subject['value']
    ).one()

    assert len(pre_all_eqs) + 1 == len(post_all_eqs)
    assert pre_dummy_object.eqid == post_dummy_subject.eqid


@populate_all
def test_new_object(webtest_app, dummy_claim, dummy_subject, dummy_object):
    """Test equivalence with a new object.

    In this case, there is a new claim that will add one extra entry (the
    object) in the equivalent_identifier table. But the subject already exists
    so its eqid will be reused.
    """
    temp = deepcopy(dummy_object)
    dummy_object.update(dummy_subject)
    dummy_subject.update(temp)
    pre_all_eqs = EquivalentIdentifier.query.all()

    # Get 'subject' before posting new claim
    ds_id = IdentifierType.query.filter_by(
        name=dummy_subject['type']
    ).one().id
    pre_dummy_subject = EquivalentIdentifier.query.filter_by(
        type_id=ds_id,
        value=dummy_subject['value']
    ).one()

    # Posting new claim
    webtest_app.post_json(
        '/claims',
        dummy_claim
    )

    post_all_eqs = EquivalentIdentifier.query.all()

    # Get 'object' after posting new claim
    do_id = IdentifierType.query.filter_by(
        name=dummy_object['type']
    ).one().id
    post_dummy_object = EquivalentIdentifier.query.filter_by(
        type_id=do_id,
        value=dummy_object['value']
    ).one()

    assert len(pre_all_eqs) + 1 == len(post_all_eqs)
    assert pre_dummy_subject.eqid == post_dummy_object.eqid


@populate_all
def test_existing_subject_object(webtest_app, dummy_claim, dummy_subject,
                                 dummy_object):
    """Test equivalence with an already existing subject and object.

    In this case, the subject and object already exist but the have different
    eqid. All the eqids of one set should be udpated.
    """
    sub_value = 'xxx'
    ob_value = 'yyy'
    sub_id = IdentifierType.query.filter_by(
        name=dummy_subject['type']
    ).one().id

    # Claim with a totally new equivalence
    dummy_subject['value'] = sub_value
    dummy_object['value'] = ob_value
    webtest_app.post_json(
        '/claims',
        dummy_claim
    )
    sub_eq = EquivalentIdentifier.query.filter_by(
        type_id=sub_id,
        value=sub_value
    ).one()
    assert EquivalentIdentifier.query.filter_by(eqid=sub_eq.eqid).count() == 2

    # Build claim with previous subject and random existing object
    random_eq = EquivalentIdentifier.query.filter(
        EquivalentIdentifier.type_id != sub_id
    ).first()
    random_eqid = random_eq.eqid
    dummy_object.update({
        'type': random_eq.type.name,
        'value': random_eq.value
    })
    pre_random_equivalents_count = EquivalentIdentifier.query.filter_by(
        eqid=random_eq.eqid
    ).count()
    assert pre_random_equivalents_count > 0
    assert random_eq.eqid != sub_eq.eqid

    webtest_app.post_json(
        '/claims',
        dummy_claim
    )
    # After the previous claim submission, all the eqids equivalent to the
    # object must have changed:
    new_random_equivalents_count = EquivalentIdentifier.query.filter_by(
        eqid=random_eqid
    ).count()
    sub_equivalents_count = EquivalentIdentifier.query.filter_by(
        eqid=sub_eq.eqid
    ).count()

    assert new_random_equivalents_count == 0
    assert sub_equivalents_count == pre_random_equivalents_count + 2
