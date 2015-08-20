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

from flask import Blueprint, request, jsonify
from claimstore.modules.claims.models import Claim, Claimant, IdentifierType, \
    Predicate
from claimstore.app import db
from claimstore.core.json import validate_json
from claimstore.core.decorators import only_json
from claimstore.core.exception import InvalidUsage


claims_restful = Blueprint(
    'claims_restful',
    __name__,
)


@claims_restful.route('/subscribe', methods=['POST'])
@only_json
def subscribe():
    json_data = request.get_json()

    try:
        validate_json(json_data, 'claims.claimant')
    except Exception as e:
        raise InvalidUsage('JSON data is not valid', details=str(e))

    if not Claimant.query.filter_by(name=json_data['name']).first():
        new_claimant = Claimant(
            name=json_data['name'],
            url=json_data['url']
        )
        db.session.add(new_claimant)

        for persistent_id in json_data['persistent_identifiers']:
            all_caps_pers_id = persistent_id['type'].upper()
            existing_persistent_id = IdentifierType.query.filter_by(
                name=all_caps_pers_id
            ).first()
            if not existing_persistent_id:
                new_persistent_id = IdentifierType(
                    name=all_caps_pers_id,
                    description=persistent_id['description'],
                    url=persistent_id['url'],
                    example_value=persistent_id['example_value'],
                    example_url=persistent_id['example_url'],
                    claimant_id=new_claimant.uid
                )
                db.session.add(new_persistent_id)
        db.session.commit()
        return jsonify({'status': 'success', 'uuid': new_claimant.uuid})
    else:
        return jsonify({'status': 'error',
                        'message': 'This claimant is already registered'}), 400


@claims_restful.route('/claims', methods=['POST'])
@only_json
def submit_claim():
    json_data = request.get_json()

    try:
        validate_json(json_data, 'claims.claim')
    except Exception as e:
        raise InvalidUsage('JSON data is not valid', details=str(e))

    claimant = Claimant.query.filter_by(name=json_data['claimant']).first()
    if not claimant:
        return jsonify({'status': 'error',
                        'message': 'Claimant not registered'}), 400

    subject_type = IdentifierType.query.filter_by(
        name=json_data['subject']['type']
    ).first()
    if not subject_type:
        return jsonify({'status': 'error',
                        'message': 'Subject Type not registered'}), 400

    object_type = IdentifierType.query.filter_by(
        name=json_data['object']['type']
    ).first()
    if not object_type:
        return jsonify({'status': 'error',
                        'message': 'Object Type not registered'}), 400

    if subject_type.uid == object_type.uid:
        return jsonify(
            {'status': 'error',
             'message': 'Subject and Object cannot have the same identifier \
             type'}
        ), 400

    predicate = Predicate.query.filter_by(
        name=json_data['claim']['predicate']
    ).first()
    if not predicate:
        return jsonify({'status': 'error',
                        'message': 'IdentifierType not registered'}), 400

    arguments = json_data['claim'].get('arguments', {})
    new_claim = Claim(
        claimant_id=claimant.uid,
        subject_type_id=subject_type.uid,
        subject_value=json_data['subject']['value'],
        predicate_id=predicate.uid,
        object_type_id=object_type.uid,
        object_value=json_data['object']['value'],
        certainty=json_data['claim']['certainty'],
        human=arguments.get('human', None),
        actor=arguments.get('actor', None),
        role=arguments.get('role', None),
        claim_details=json_data,
    )
    db.session.add(new_claim)
    db.session.commit()
    return jsonify({'status': 'success', 'uuid': new_claim.uuid})


@claims_restful.route('/claims', methods=['GET'])
def get_claim():
    return jsonify(
        json_list=[
            {'created': c.created,
             'claim_details': c.claim_details} for c in Claim.query.all()
        ]
    )
