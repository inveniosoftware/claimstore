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

"""Restful resources for the claims module."""

from functools import wraps

import isodate  # noqa
from flask import Blueprint, request
from sqlalchemy import or_

from claimstore.core.datetime import loc_date_utc
from claimstore.core.exception import InvalidJSONData, InvalidRequest, \
    RestApiException
from claimstore.core.json import validate_json
from claimstore.ext.sqlalchemy import db
from claimstore.modules.claims.models import Claim, Claimant, IdentifierType, \
    Predicate

from flask_restful import Api, Resource, abort, inputs, reqparse  # isort:skip

blueprint = Blueprint(
    'claims_restful',
    __name__,
)

claims_api = Api(blueprint)


def error_handler(f):
    """Decorator to handle restful exceptions.

    If this decorator is not used, Flask-RestFul will always raise a 500 code,
    independently of your Flask app error handler registration.
    """
    @wraps(f)
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except RestApiException as e:
            abort(
                e.status_code,
                message=e.message,
                status=e.status_code,
                extra=e.extra
            )
    return inner


restful_decorators = [error_handler]


class ClaimStoreResource(Resource):

    """Base class for REST resources."""

    method_decorators = restful_decorators
    json_schema = None

    def validate_json(self, json_data):
        """Validate that json_data follows the appropiate JSON schema.

        :param json_data: JSON data to be validated.
        :raises: InvalidJSONData
        """
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
        """Subscribe a new claimant.

        Receives JSON data with all the information of a new claimant and it
        stores it in the database.
        """
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
                        claimant_id=new_claimant.id
                    )
                    db.session.add(new_persistent_id)
            db.session.commit()
            return {'status': 'success', 'uuid': new_claimant.uuid}
        else:
            raise InvalidRequest('This claimant is already registered')


class ClaimsResource(ClaimStoreResource):

    """Resource that handles all claims-related requests."""

    json_schema = 'claims.claim'

    def __init__(self):
        """Initialise Claims Resource."""
        super(ClaimStoreResource, self).__init__()
        self.get_claims_parser = reqparse.RequestParser()
        self.get_claims_parser.add_argument(
            'claimant', dest='claimant',
            type=str, location='args',
            help='Unique short name of a registered claimant',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'predicate', dest='predicate',
            type=str, location='args',
            help='Unique name of a registered predicate',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'subject', dest='subject',
            type=str, location='args',
            help='Unique name of a registered identifier',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'object', dest='object',
            type=str, location='args',
            help='Unique name of a registered identifier',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'certainty', dest='certainty',
            type=float, location='args',
            help='Minimum certainty for a claim (float between 0 and 1.0)',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'human', dest='human',
            type=int, location='args',
            help='`1` if human claims. `0` if algorithm. No value shows all',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'actor', dest='actor',
            type=str, location='args',
            help='Name of the actor of the claim',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'role', dest='role',
            type=str, location='args',
            help='Role of the actor',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'since', dest='since',
            type=inputs.date, location='args',
            help='Date with the format YYYY-MM-DD',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'until', dest='until',
            type=inputs.date, location='args',
            help='Date with the format YYYY-MM-DD',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'type', dest='type',
            type=str, location='args',
            help='Identifier Type (e.g. DOI)',
            trim=True
        )
        self.get_claims_parser.add_argument(
            'value', dest='value',
            type=str, location='args',
            help='Value of an Identifier Type',
            trim=True
        )

    def post(self):
        """Record a new claim.

        This POST service expects JSON data following the JSON schema defined
        for claims.
        """
        json_data = request.get_json()

        self.validate_json(json_data)

        try:
            created_dt = isodate.parse_datetime(json_data['claim']['created'])
        except isodate.ISO8601Error as e:
            raise InvalidJSONData(
                'Claim `created` datetime does not follow ISO 8601 Z',
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

        if subject_type.id == object_type.id:
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
            claimant=claimant,
            subject_type_id=subject_type.id,
            subject_value=json_data['subject']['value'],
            predicate_id=predicate.id,
            object_type_id=object_type.id,
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
        """GET service that returns the stored claims.


        Many arguments can be used in order to filter the output. Only AND
        queries are preformed at the moment.

        List of arguments:

        * since: datetime (YYYY-MM-DD) - it fetches claims that were created
          from this given datetime.
        * until: datetime (YYYY-MM-DD) - it fetches claims that were created
          up to this given datetime.
        * claimant: claimant's unique name - it fetches claims submitted by the
          specified claimant.
        * predicate: predicate's unique name - it finds claims using this
          predicate (e.g. is_same_as).
        * certainty: float number between 0 and 1.0. It will search for claims
          with at least the specified certainty.
        * human: enter 1 if searching for human-created claims, 0 for
          algorithms and nothing in order to retrieve all.
        * actor: it filters claims by their actor's name (one can use %).
        * role: it filters claims by their actor's role (one can use %).
        * type: it finds claims using a certain identifier type (either subject
          or object). For instance: DOI.
        * value: it fetches all the claims with that identifier value.
        * subject: it fetches claims using a given identifier type as a subject
          type.
        * object: it fetches claims using a given identifier type as an object
          type.
        """
        args = self.get_claims_parser.parse_args()
        if all(x is None for x in args.values()):  # Avoid false positives (0)
            claims = Claim.query.all()
        else:
            claims = Claim.query

            if args.since:
                claims = claims.filter(
                    Claim.created >= loc_date_utc(args.since)
                )

            if args.until:
                claims = claims.filter(
                    Claim.created < loc_date_utc(args.until)
                )

            if args.claimant:
                claims = claims. \
                    join(Claim.claimant). \
                    filter(Claimant.name == args.claimant)

            if args.predicate:
                claims = claims. \
                    join(Claim.predicate). \
                    filter(Predicate.name == args.predicate)

            if args.certainty is not None:
                claims = claims.filter(Claim.certainty >= args.certainty)

            if args.human is not None:
                claims = claims.filter(Claim.human == args.human)

            if args.actor:
                claims = claims.filter(Claim.actor.like(args.actor))

            if args.role:
                claims = claims.filter(Claim.role.like(args.role))

            if args.subject or args.object:
                # Using subject/object makes type/value incompatible.
                subject_type = db.aliased(IdentifierType, name='SubjectType')
                object_type = db.aliased(IdentifierType, name='ObjectType')
                if args.subject:
                    claims = claims. \
                        join(subject_type,
                             Claim.subject_type_id == subject_type.id). \
                        filter(subject_type.name == args.subject)

                if args.object:
                    claims = claims. \
                        join(object_type,
                             Claim.object_type_id == object_type.id). \
                        filter(object_type.name == args.object)
            else:
                # Type searches both in subject and object
                if args.type:
                    claims = claims. \
                        join(
                            IdentifierType,
                            or_(
                                Claim.subject_type_id == IdentifierType.id,
                                Claim.object_type_id == IdentifierType.id
                            )
                        ).filter(IdentifierType.name == args.type)

                if args.value:
                    claims = claims. \
                        filter(
                            or_(
                                Claim.subject_value.like(args.value),
                                Claim.object_value.like(args.value))
                        )

        return [{
            'received': c.received.isoformat(),
            'claim_details': c.claim_details
        } for c in claims]


class IdentifierResource(ClaimStoreResource):

    """Resource that handles Identifier requests."""

    def get(self):
        """GET service that returns the stored identifiers."""
        id_types = IdentifierType.query.all()
        return [id_type.name for id_type in id_types]


class PredicateResource(ClaimStoreResource):

    """Resource that handles Predicate requests."""

    def get(self):
        """GET service that returns the stored predicates."""
        predicates = Predicate.query.all()
        return [pred.name for pred in predicates]


claims_api.add_resource(Subscription,
                        '/subscribe',
                        endpoint='subscribe')
claims_api.add_resource(ClaimsResource,
                        '/claims',
                        endpoint='claims')
claims_api.add_resource(IdentifierResource,
                        '/identifiers',
                        endpoint='identifiers')
claims_api.add_resource(PredicateResource,
                        '/predicates',
                        endpoint='predicates')
