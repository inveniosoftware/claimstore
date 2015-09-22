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

"""Restful resources for the claims module.

isort:skip_file
"""

from collections import defaultdict
from functools import wraps

import isodate  # noqa
from flask import Blueprint, current_app, request
from flask_restful import Api, Resource, abort, inputs, reqparse
from jsonschema import ValidationError
from sqlalchemy import and_, or_

from claimstore.core.datetime import loc_date_utc
from claimstore.core.exception import InvalidJSONData, InvalidRequest, \
    RestApiException
from claimstore.core.json import validate_json
from claimstore.ext.sqlalchemy import db
from claimstore.modules.claims.models import Claim, Claimant, \
    EquivalentIdentifier, IdentifierType, Predicate

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


def check_ip(f):
    """Decorator to control the access to the API.

    If the client's IP matches the list of IPs defined in the environment
    variable `CLAIMSTORE_ALLOWED_IPS`, then the access will be granted.
    Otherwise, an access denied code 403 will be raised.
    """
    @wraps(f)
    def inner(*args, **kwargs):
        if request.remote_addr in current_app.config['CLAIMSTORE_ALLOWED_IPS']:
            return f(*args, **kwargs)
        else:
            abort(
                403,
                message="Access denied",
                status=403
            )
    return inner


restful_decorators = [error_handler, check_ip]


class ClaimStoreResource(Resource):

    """Base class for REST resources."""

    method_decorators = restful_decorators
    json_schema = None

    def validate_json(self, json_data):
        """Validate that json_data follows the appropiate JSON schema.

        :param json_data: JSON data to be validated.
        :raises: :exc:`InvalidJSONData` if the instance is invalid.
        """
        try:
            validate_json(json_data, self.json_schema)
        except ValidationError as e:
            raise InvalidJSONData('JSON data is not valid', extra=str(e))


class ClaimantResource(ClaimStoreResource):

    """Resource related to claimant subscription in the ClaimStore.

    This POST service expects JSON data following the JSON schema defined for
    claimants.
    """

    json_schema = 'claims.claimant'

    def post(self):
        """Register a new claimant in the ClaimStore.

        .. http:post:: /subscribe

            This resource is expecting JSON data with all the necessary
            information of a new claimant.

            **Request**:

            .. sourcecode:: http

                POST /subscribe HTTP/1.1
                Content-Type: application/json
                Host: localhost:5000

                {
                    "name": "INSPIRE",
                    "url": "http://inspirehep.net"
                }

            :reqheader Content-Type: application/json
            :json body: JSON with the information of the claimant. The JSON
                        data should be valid according to the `JSON Schema for
                        claimants <https://goo.gl/9ts8ov>`_.

            **Responses**:

            .. sourcecode:: http

                HTTP/1.0 200 OK
                Content-Length: 80
                Content-Type: application/json

                {
                    "status": "success",
                    "uuid": "ab19c98b-xxxx-xxxx-xxxx-1d6af3bf58b4"
                }

            .. sourcecode:: http

                HTTP/1.0 400 BAD REQUEST
                Content-Length: 95
                Content-Type: application/json

                {
                    "extra": null,
                    "message": "This claimant is already registered",
                    "status": 400
                }

            :resheader Content-Type: application/json
            :statuscode 200: no error - the claimant was subscribed
            :statuscode 400: invalid request - problably a malformed JSON
            :statuscode 403: access denied

            .. see docs/users.rst for usage documenation.
        """
        json_data = request.get_json()
        self.validate_json(json_data)
        if not Claimant.query.filter_by(name=json_data['name']).first():
            new_claimant = Claimant(
                name=json_data['name'],
                url=json_data['url']
            )
            db.session.add(new_claimant)
            db.session.flush()

            if 'persistent_identifiers' in json_data:
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


class ClaimResource(ClaimStoreResource):

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
        self.get_claims_parser.add_argument(
            'recurse', dest='recurse',
            type=inputs.boolean, default=False, location='args',
            help='True if fetching all equivalent identifiers',
            trim=True
        )

    def post(self):
        """Record a new claim.

        .. http:post:: /claims

            This resource is expecting JSON data with all the necessary
            information of a new claim.

            **Request**:

            .. sourcecode:: http

                POST /claims HTTP/1.1
                Accept: application/json
                Content-Length: 336
                Content-Type: application/json

                {
                    "arguments": {
                        "actor": "CDS_submission",
                        "human": 0
                    },
                    "certainty": 1.0,
                    "claimant": "CDS",
                    "created": "2015-03-25T11:00:00Z",
                    "object": {
                        "type": "CDS_REPORT_NUMBER",
                        "value": "CMS-PAS-HIG-14-008"
                    },
                    "predicate": "is_same_as",
                    "subject": {
                        "type": "CDS_RECORD_ID",
                        "value": "2003192"
                    }
                }

            :reqheader Content-Type: application/json
            :json body: JSON with the information of the claimt. The JSON
                        data should be valid according to the `JSON Schema for
                        claims <https://goo.gl/C1f6vw>`_.

            **Responses**:

            .. sourcecode:: http

                HTTP/1.0 200 OK
                Content-Length: 80
                Content-Type: application/json

                {
                    "status": "success",
                    "uuid": "fad4ec9f-0e95-4a22-b65c-d01f15aba6be"
                }

            .. sourcecode:: http

                HTTP/1.0 400 BAD REQUEST
                Content-Length: 9616
                Content-Type: application/json
                Date: Tue, 22 Sep 2015 09:02:25 GMT
                Server: Werkzeug/0.10.4 Python/3.4.3

                {
                    "extra": "'claimant' is a required property. Failed
                              validating 'required' in schema...",
                    "message": "JSON data is not valid",
                    "status": 400
                }

            :resheader Content-Type: application/json
            :statuscode 200: no error - the claim was recorded
            :statuscode 400: invalid request - problably a malformed JSON
            :statuscode 403: access denied

            .. see docs/users.rst for usage documenation.
        """
        json_data = request.get_json()

        self.validate_json(json_data)

        try:
            created_dt = isodate.parse_datetime(json_data['created'])
        except isodate.ISO8601Error as e:
            raise InvalidJSONData(
                'Claim `created` datetime does not follow ISO 8601 Z',
                extra=str(e)
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
            name=json_data['predicate']
        ).first()
        if not predicate:
            raise InvalidRequest('Predicate not registered')

        subject_eqid, object_eqid = None, None
        if json_data['predicate'] in \
                current_app.config['CFG_EQUIVALENT_PREDICATES']:
            subject_eqid, object_eqid = EquivalentIdentifier.set_equivalent_id(
                subject_type.id,
                json_data['subject']['value'],
                object_type.id,
                json_data['object']['value']
            )

        arguments = json_data.get('arguments', {})
        new_claim = Claim(
            created=created_dt,
            claimant=claimant,
            subject_type_id=subject_type.id,
            subject_value=json_data['subject']['value'],
            subject_eqid=subject_eqid.id if subject_eqid else None,
            predicate_id=predicate.id,
            object_type_id=object_type.id,
            object_value=json_data['object']['value'],
            object_eqid=object_eqid.id if object_eqid else None,
            certainty=json_data['certainty'],
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

        .. http:get:: /claims

            Returns a JSON list with all the claims matching the query
            parameters.

            **Request**:

                .. sourcecode:: http

                    GET /claims?type=INSPIRE_RECORD_ID&value=cond-mat/9906097&
                    recurse=1 HTTP/1.1
                    Accept: */*
                    Host: localhost:5000

            :reqheader Content-Type: application/json
            :query datetime since: it must have the format 'YYYY-MM-DD'. It
                                   fetches claims that were created from this
                                   given datetime.
            :query datetime until:  it must have the format 'YYYY-MM-DD'. It
                                    fetches claims that were created up to this
                                    given datetime.
            :query string claimant: claimant's unique name. It fetches claims
                                    submitted by the specified claimant.
            :query string predicate: predicate's unique name. It finds claims
                                     using this predicate (e.g. is_same_as).
            :query float certainty: float number between 0 and 1.0. It will
                                    search for claims with at least the
                                    specified certainty.
            :query int human: enter 1 if searching for human-created claims, 0
                              for algorithms and nothing in order to retrieve
                              all.
            :query string actor: it filters claims by their actor's name (one
                                 can use `%`).
            :query string role: it filters claims by their actor's role (one
                                can use `%`).
            :query string type: it finds claims using a certain identifier type
                                (either subject or object). For instance: DOI.
            :query string value: it fetches all the claims with that identifier
                                 value.
            :query boolean recurse: used in combination with `type` and `value`
                                    will find all the equivalent identifiers to
                                    the specified one.
            :query string subject: it fetches claims using the given identifier
                                   type as a subject type.
            :query string object: it fetches claims using the given identifier
                                  type as an object type.

            **Response**:

                .. sourcecode:: http

                    HTTP/1.0 200 OK
                    Content-Length: 1166
                    Content-Type: application/json

                    [
                        {
                            "arguments": {
                                "actor": "CDS_submission",
                                "human": 0
                            },
                            "certainty": 1.0,
                            "claimant": "CDS",
                            "created": "2015-03-25T11:00:00Z",
                            "object": {
                                "type": "CDS_REPORT_NUMBER",
                                "value": "CMS-PAS-HIG-14-008"
                            },
                            "predicate": "is_same_as",
                            "recieved": "2015-09-22T08:18:30.606912+00:00",
                            "subject": {
                                "type": "CDS_RECORD_ID",
                                "value": "2003192"
                            },
                            "uuid": "44103ee2-0d87-47f9-b0e4-77673d297cdb"
                        },
                        {
                            "arguments": {
                                "actor": "John Doe",
                                "human": 1,
                                "role": "cataloguer"
                            },
                            "certainty": 0.5,
                            "claimant": "INSPIRE",
                            "created": "2015-05-25T11:00:00Z",
                            "object": {
                                "type": "CDS_RECORD_ID",
                                "value": "2003192"
                            },
                            "predicate": "is_variant_of",
                            "recieved": "2015-09-22T08:18:30.638933+00:00",
                            "subject": {
                                "type": "INSPIRE_RECORD_ID",
                                "value": "cond-mat/9906097"
                            },
                            "uuid": "27689445-02b9-4d5d-8f9b-da21970e2352"
                        }
                    ]

            :resheader Content-Type: application/json
            :statuscode 200: no error
            :statuscode 400: invalid request
            :statuscode 403: access denied

            .. see docs/users.rst for usage documenation.
        """
        args = self.get_claims_parser.parse_args()
        if all(x is None for x in args.values()):  # Avoid false positives (0)
            claims = Claim.query.all()
        else:
            claims = Claim.query

            if args.type and args.value:
                if args.recurse:
                    claims = Claim.equivalents(args.type, args.value)
                    if not claims:
                        return []
                else:
                    type_ = IdentifierType.query.filter_by(
                        name=args.type
                    ).first()
                    if type_:
                        claims = claims. \
                            filter(
                                or_(
                                    and_(
                                        Claim.subject_type_id == type_.id,
                                        Claim.subject_value.like(args.value)
                                    ),
                                    and_(
                                        Claim.object_type_id == type_.id,
                                        Claim.object_value.like(args.value)
                                    )
                                )
                            )
                    else:
                        return []
            elif args.type:  # Only by type
                    claims = claims. \
                        join(
                            IdentifierType,
                            or_(
                                Claim.subject_type_id == IdentifierType.id,
                                Claim.object_type_id == IdentifierType.id
                            )
                        ).filter(IdentifierType.name == args.type)

            elif args.value:  # Only by value
                claims = claims. \
                    filter(
                        or_(
                            Claim.subject_value.like(args.value),
                            Claim.object_value.like(args.value))
                    )

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

        output = []
        for c in claims:
            item = c.claim_details
            item['recieved'] = c.received.isoformat()
            item['uuid'] = c.uuid
            output.append(item)
        return output


class IdentifierResource(ClaimStoreResource):

    """Resource that handles Identifier requests."""

    def get(self):
        """GET service that returns the stored identifiers.

        .. http:get:: /identifiers

            Returns a JSON list with all the available identifiers.

            **Request**:

                .. sourcecode:: http

                    GET /identifiers HTTP/1.1
                    Accept: */*
                    Host: localhost:5000

            :reqheader Content-Type: application/json

            **Response**:

                .. sourcecode:: http

                    HTTP/1.0 200 OK
                    Content-Length: 147
                    Content-Type: application/json

                    [
                        "ARXIV_ID",
                        "CDS_AUTHOR_ID",
                        "CDS_RECORD_ID",
                        "CDS_REPORT_NUMBER",
                        "DOI",
                        "INSPIRE_AUTHOR_ID",
                        "INSPIRE_RECORD_ID"
                    ]

            :resheader Content-Type: application/json
            :statuscode 200: no error
            :statuscode 400: invalid request
            :statuscode 403: access denied

            .. see docs/users.rst for usage documenation.
        """
        id_types = IdentifierType.query.all()
        return [id_type.name for id_type in id_types]


class PredicateResource(ClaimStoreResource):

    """Resource that handles Predicate requests."""

    def get(self):
        """GET service that returns all the available predicates.

        .. http:get:: /predicates

            Returns a JSON list with all the predicates.

            **Request**:

                .. sourcecode:: http

                    GET /predicates HTTP/1.1
                    Accept: */*
                    Host: localhost:5000

            :reqheader Content-Type: application/json

            **Response**:

                .. sourcecode:: http

                    HTTP/1.0 200 OK
                    Content-Length: 108
                    Content-Type: application/json

                    [
                        "is_author_of",
                        "is_contributor_to",
                        "is_erratum_of",
                        "is_same_as",
                        "is_variant_of"
                    ]

            :resheader Content-Type: application/json
            :statuscode 200: no error
            :statuscode 400: invalid request
            :statuscode 403: access denied

            .. see docs/users.rst for usage documenation
        """
        predicates = Predicate.query.all()
        return [pred.name for pred in predicates]


class EquivalentIdResource(ClaimStoreResource):

    """Resource that handles Equivalent Identifier requests."""

    def get(self, eqid=None):
        """GET service that returns all the stored Equivalent Identifiers.

        .. http:get:: /eqids/(uuid:eqid)

            Returns all the type/value entries in the index grouped by their
            equivalent identifiers.

            **Requests**:

                .. sourcecode:: http

                    GET /eqids HTTP/1.1
                    Accept: */*
                    Host: localhost:5000

                .. sourcecode:: http

                    GET /eqids/0e64606e-68ce-482e-ad59-1e9981394f84 HTTP/1.1
                    Accept: */*
                    Host: localhost:5000

            :reqheader Content-Type: application/json
            :param eqid: query by a specific uuid which is shared by some
                         equivalent identifiers

            **Response**:

                .. sourcecode:: http

                    HTTP/1.0 200 OK
                    Content-Length: 592
                    Content-Type: application/json

                    {
                        "36dfb125-5c35-4d3a-870c-76eb4bad498e": [
                            {
                                "type": "ARXIV_ID",
                                "value": "cond-mat/9906097"
                            },
                            {
                                "type": "DOI",
                                "value": "C10.1103/PhysRevE.62.7422"
                            }
                        ],
                        "77c4a5eb-3ed8-4c80-ba0d-644d6bc397a3": [
                            {
                                "type": "CDS_RECORD_ID",
                                "value": "2003192"
                            },
                            {
                                "type": "CDS_REPORT_NUMBER",
                                "value": "CMS-PAS-HIG-14-008"
                            },
                            {
                                "type": "INSPIRE_RECORD_ID",
                                "value": "cond-mat/9906097"
                            }
                        ]
                    }

            :resheader Content-Type: application/json
            :statuscode 200: no error
            :statuscode 400: invalid request - problably a malformed UUID
            :statuscode 403: access denied

            .. see docs/users.rst for usage documenation.
        """
        if eqid:
            eqids = EquivalentIdentifier.query.filter_by(eqid=str(eqid))
        else:
            eqids = EquivalentIdentifier.query.all()
        output_dict = defaultdict(list)
        for eqi in eqids:
            output_dict[eqi.eqid].append({
                'type': eqi.type.name,
                'value': eqi.value
            })
        return output_dict


claims_api.add_resource(ClaimantResource,
                        '/subscribe',
                        endpoint='subscribe')
claims_api.add_resource(ClaimResource,
                        '/claims',
                        endpoint='claims')
claims_api.add_resource(IdentifierResource,
                        '/identifiers',
                        endpoint='identifiers')
claims_api.add_resource(PredicateResource,
                        '/predicates',
                        endpoint='predicates')
claims_api.add_resource(EquivalentIdResource,
                        '/eqids',
                        '/eqids/<uuid:eqid>',
                        endpoint='eqids')
