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

"""Restful resources for the claims module."""

import isodate  # noqa
from flask import Blueprint, request
from flask_restful import Api, Resource

from claimstore.app import db
from claimstore.core.exception import InvalidJSONData, InvalidRequest
from claimstore.core.json import validate_json
from claimstore.modules.claims.models import Claim, Claimant, IdentifierType, \
    Predicate

blueprint = Blueprint(
    'claims_restful',
    __name__,
)
claims_api = Api(blueprint)


class ClaimStoreResource(Resource):

    """Base class for REST resources."""

    json_schema = None

    def validate_json(self, json_data):
        """Validate that json_data follows the appropiate JSON schema."""
        try:
            validate_json(json_data, self.json_schema)
        except Exception as e:
            raise InvalidJSONData('JSON data is not valid', details=str(e))


class Subscription(ClaimStoreResource):

    """Register a new claimant in the database.

    This POST service expects JSON data following the JSON schema defined for
    claimants.
    """

    json_schema = 'claims.claimant'

    def post(self):
        """Process post request."""
        json_data = request.get_json()
        self.validate_json(json_data)
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
            return {'status': 'success', 'uuid': new_claimant.uuid}
        else:
            raise InvalidRequest('This claimant is already registered')


class Claims(ClaimStoreResource):

    """Resource that handles all claims-related requests."""

    json_schema = 'claims.claim'

    def post(self):
        """Record a new claim.

        This POST service expects JSON data following the JSON schema defined
        for claims.
        """
        json_data = request.get_json()

        self.validate_json(json_data)

        try:
            created_dt = isodate.parse_datetime(json_data['claim']['datetime'])
        except isodate.ISO8601Error as e:
            raise InvalidJSONData(
                'Claim datetime does not follow ISO 8601 Z',
                details=str(e)
            )

        claimant = Claimant.query.filter_by(name=json_data['claimant']).first()
        if not claimant:
            raise InvalidRequest('Claimant not registered')

        subject_type = IdentifierType.query.filter_by(
            name=json_data['subject']['type']
        ).first()
        if not subject_type:
            raise InvalidRequest('Subject Type not registered')

        object_type = IdentifierType.query.filter_by(
            name=json_data['object']['type']
        ).first()
        if not object_type:
            raise InvalidRequest('Object Type not registered')

        if subject_type.uid == object_type.uid:
            raise InvalidRequest('Subject and Object cannot have the same \
                identifier type')

        predicate = Predicate.query.filter_by(
            name=json_data['claim']['predicate']
        ).first()
        if not predicate:
            raise InvalidRequest('Predicate not registered')

        arguments = json_data['claim'].get('arguments', {})
        new_claim = Claim(
            created=created_dt,
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
        return {'status': 'success', 'uuid': new_claim.uuid}

    def get(self):
        """GET service that returns the stored claims."""
        return [{
            'received': c.received.isoformat(),
            'created': c.created.isoformat(),
            'claim_details': c.claim_details
        } for c in Claim.query.all()]


claims_api.add_resource(Subscription, '/subscribe', endpoint='subscribe')
claims_api.add_resource(Claims, '/claims', endpoint='claims')
