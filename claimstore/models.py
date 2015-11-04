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

"""ClaimStore data model."""

from uuid import uuid4

from flask import current_app
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import JSONB, UUID

from claimstore.app import db
from claimstore.core.datetime import now_utc
from claimstore.core.db.types import UTCDateTime


class Claim(db.Model):

    """Model representing a Claim.

    Each claim is associated to a specific Claimant and references some already
    existing Identifier Types and predicate.
    """

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    """Unique id of the claim."""

    uuid = db.Column(
        UUID,
        nullable=False,
        unique=True,
        default=lambda: str(uuid4())
    )
    """Universally Unique Identifier that represents a single claim."""

    received = db.Column(
        UTCDateTime,
        default=now_utc,
        nullable=False
    )
    """Datetime in which the claim has been received and stored."""

    created = db.Column(
        UTCDateTime,
        nullable=False
    )
    """Datetime in which the claim has been created by the claimant."""

    claimant_id = db.Column(
        db.Integer,
        db.ForeignKey('claimant.id'),
        nullable=False
    )
    """Id of the associated Claimant."""

    subject_type_id = db.Column(
        db.Integer,
        db.ForeignKey('identifier_type.id'),
        nullable=False
    )
    """Id of the associated IdentifierType used as a subject."""

    subject_value = db.Column(
        db.String,
        nullable=False
    )
    """Value of the subject."""

    subject_eqid = db.Column(
        db.Integer,
        db.ForeignKey('equivalent_identifier.id', ondelete='SET NULL')
    )
    """Unique identifier for this subject (type, value)."""

    predicate_id = db.Column(
        db.Integer,
        db.ForeignKey('predicate.id'),
        nullable=False
    )
    """Id of the associated Predicate."""

    certainty = db.Column(
        db.Float,
        nullable=False
    )
    """Certainty of the claim. It must be a float between 0 and 1.0."""

    human = db.Column(db.Integer)
    """Whether the claims has been done by a human (1) or not (0)."""

    actor = db.Column(db.String)
    """`Human` that has performed the claim."""

    role = db.Column(db.String)
    """Role of the `human` who has performed the claim."""

    object_type_id = db.Column(
        db.Integer,
        db.ForeignKey('identifier_type.id'),
        nullable=False
    )
    """Id of the associated IdentifierType used as an object."""

    object_value = db.Column(
        db.String,
        nullable=False
    )
    """Value of the object."""

    object_eqid = db.Column(
        db.Integer,
        db.ForeignKey('equivalent_identifier.id', ondelete='SET NULL')
    )
    """Unique identifier for this object (type, value)."""

    claim_details = db.Column(JSONB)
    """JSONB representation of the full claim as received."""

    @classmethod
    def equivalents(cls, type_name, value):
        """Get claims with the all the equivalent subjects or objects."""
        all_eqids = EquivalentIdentifier.equivalent_ids(type_name, value)
        if all_eqids:
            return cls.query.filter(
                or_(
                    cls.subject_eqid.in_(all_eqids),
                    cls.object_eqid.in_(all_eqids)
                )
            ).all()
        return []

    def __repr__(self):
        """Printable version of the Claim object."""
        return '<Claim {}>'.format(self.uuid)


class Claimant(db.Model):

    """Represents a Claimant.

    Claimants are the main providers of claims. Each claimant may be associated
    to many different claims.
    """

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    """Unique id of the claimant."""

    uuid = db.Column(
        UUID(),
        nullable=False,
        unique=True,
        default=lambda: str(uuid4()),
    )
    """Universally unique id of the claimant."""

    joined = db.Column(
        UTCDateTime,
        default=now_utc,
    )
    """Datetime when the claimant subscribed to ClaimStore."""

    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
        index=True
    )
    """Claimant name. It must be unique and preferably short."""

    url = db.Column(db.String)
    """URL of the claimant."""

    claim = db.relationship(
        'Claim',
        backref='claimant',
        cascade="all, delete-orphan",
        lazy='dynamic'
    )
    """Claim associated with this claimant."""

    def __repr__(self):
        """Printable version of the Claimant object."""
        return '<Claimant {}>'.format(self.uuid)


class IdentifierType(db.Model):

    """Represents an identifier type.

    An Identifier Type is a persistent identifier type that can be used in
    claims by claimants.
    """

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    """Unique id of the Identifier."""

    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
        index=True
    )
    """Unique name of the identifier type. Preferably one word in caps."""

    description = db.Column(
        db.String,
        nullable=False
    )
    """Description of the identifier type."""

    url = db.Column(
        db.String,
        nullable=False
    )
    """URL in which the identifier is used."""

    example_value = db.Column(
        db.String,
        nullable=False
    )
    """Example of a possible value for an identifier."""

    example_url = db.Column(
        db.String,
        nullable=False
    )
    """Example of a full URL in which the identifier is being used."""

    claimant_id = db.Column(
        db.Integer,
        db.ForeignKey('claimant.id')
    )
    """Id of the associated claimant that registered this identifier."""

    subject = db.relationship(
        'Claim',
        backref='subject_type',
        primaryjoin="Claim.subject_type_id == IdentifierType.id",
        lazy='dynamic'
    )
    """Backref in claim to reach this identifier_type."""

    object = db.relationship(
        'Claim',
        backref='object_type',
        primaryjoin="Claim.object_type_id == IdentifierType.id",
        lazy='dynamic'
    )
    """Backref in claim to reach this identifier_type."""

    eqid = db.relationship(
        'EquivalentIdentifier',
        backref='type',
        primaryjoin="EquivalentIdentifier.type_id == IdentifierType.id",
        lazy='dynamic'
    )
    """Backref in equivalent_identifier to reach this identifier_type."""

    def __repr__(self):
        """Printable version of the IdentifierType object."""
        return '<IdentifierType {}>'.format(self.name)


class Predicate(db.Model):

    """Represents a predicate.

    The predicate defines the type of claim. An example of predicate could be:
    is_same_as.
    """

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    """Unique id of the predicate."""

    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
        index=True
    )
    """Unique name of a predicate."""

    description = db.Column(
        db.String
    )
    """Description of the predicate."""

    claim = db.relationship(
        'Claim',
        backref='predicate',
        cascade="all, delete-orphan",
        lazy='dynamic'
    )
    """Backref in claim to reach this predicate."""

    def __repr__(self):
        """Printable version of the Predicate object."""
        return '<Predicate {}'.format(self.name)


class EquivalentIdentifier(db.Model):

    """Model that defines equivalent identifiers.

    A given tuple (IdentifierType1, value1), e.g. (DOI, 1234) will have
    associated a unique id (`eqid`) that will be shared by the other tuple,
    e.g. (IdentifierType2, value2) in the relationship, in case the two IDs are
    equivalent (e.g. related via is_same_as predicate). If new equality claims
    are done in which existing identifiers are used, they will take the `eqid`
    from them.

    For instance, if we have some claims like:

    =========== ============ ===========  ========== ===========
    SubjectType SubjectValue  Predicate   ObjectType ObjectValue
    =========== ============ ===========  ========== ===========
    Type1       Value1       is_same_as   Type2      Value2
    Type3       Value3       is_same_as   Type4      Value4
    Type1       Value1       is_same_as   Type4      Value4
    Type5       Value5       is_same_as   Type6      Value6
    =========== ============ ===========  ========== ===========


    Then, in the EquivalentIdentifier table there will be something like:

    ====== ====== ====
    type   value  uuid
    ====== ====== ====
    Type1  Value1 01
    Type2  Value2 01
    Type3  Value3 01
    Type4  Value4 01
    Type5  Value4 02
    Type6  Value4 02
    ====== ====== ====

    This table will enable and facilitate several use cases:

    #. We could very easily get a list of the different identifiers for the
       same data resource.
    #. It will simplify the recursive query by type/value in any
       subject/object claim.
    """

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    """Unique id of the data resource."""

    eqid = db.Column(
        UUID,
        nullable=False,
        index=True
    )
    """Universally Unique Identifier that represents a single data resource."""

    type_id = db.Column(
        db.Integer,
        db.ForeignKey('identifier_type.id'),
        nullable=False,
        index=True
    )
    """The id of a given IdentifierType."""

    value = db.Column(
        db.String,
        nullable=False,
        index=True
    )
    """A given value for the IdentifierType."""

    @classmethod
    def equivalents(cls, type_name, value):
        """Return all the equivalent identifiers.

        This method fetches the eqid for a given (type_name, value) and uses it
        to find all the equivalent identifiers.
        """
        type_ = IdentifierType.query.filter_by(name=type_name).first()
        if type_:
            eqi = cls.query.with_entities(
                cls.eqid).filter_by(
                    type_id=type_.id,
                    value=value
            ).first()
            if eqi:
                return cls.query.filter(
                    cls.eqid == eqi.eqid
                )
        return []

    @classmethod
    def equivalent_ids(cls, type_name, value):
        """Return the identifiers of all the equivalent entities.

        This method fetches the eqid for a given (type_name, value) and uses it
        to find all the equivalent identifiers.
        It returns a list with `EquivalentIdentifier.id`.
        """
        eqs = cls.equivalents(type_name, value)
        if eqs:
            return eqs.with_entities(cls.id)
        return []

    @classmethod
    def set_equivalent_id(cls, subject_id, subject_value, object_id,
                          object_value):
        """Store and return the equivalent identifiers as required."""
        subject_eqid = cls.query.filter_by(
            type_id=subject_id,
            value=subject_value
        ).first()
        object_eqid = cls.query.filter_by(
            type_id=object_id,
            value=object_value
        ).first()
        if not (subject_eqid or object_eqid):
            eqid_uuid = str(uuid4())
            subject_eqid = cls(
                eqid=eqid_uuid,
                type_id=subject_id,
                value=subject_value
            )
            db.session.add(subject_eqid)
            object_eqid = cls(
                eqid=eqid_uuid,
                type_id=object_id,
                value=object_value
            )
            db.session.add(object_eqid)
        elif subject_eqid and object_eqid and \
                subject_eqid.eqid != object_eqid.eqid:
            cls.query.filter_by(eqid=object_eqid.eqid).update({
                cls.eqid: subject_eqid.eqid
            })
        elif subject_eqid and not object_eqid:
            object_eqid = cls(
                eqid=subject_eqid.eqid,
                type_id=object_id,
                value=object_value
            )
            db.session.add(object_eqid)
        elif object_eqid and not subject_eqid:
            subject_eqid = cls(
                eqid=object_eqid.eqid,
                type_id=subject_id,
                value=subject_value
            )
            db.session.add(subject_eqid)
        db.session.flush()
        return subject_eqid, object_eqid

    @classmethod
    def clear(cls):
        """Delete all the entries of the table equivalent_identifiers."""
        cls.query.delete()
        db.session.commit()

    @classmethod
    def rebuild(cls):
        """Rebuild index based on claims."""
        for claim in Claim.query.all():
            if claim.predicate.name in \
               current_app.config['CFG_EQUIVALENT_PREDICATES']:
                cls.set_equivalent_id(
                    claim.subject_type_id,
                    claim.subject_value,
                    claim.object_type_id,
                    claim.object_value
                )
        db.session.commit()
