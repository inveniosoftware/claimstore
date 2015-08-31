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

"""ClaimStore data model."""

from uuid import uuid4

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

    claim_details = db.Column(JSONB)
    """JSONB representation of the full claim as received."""

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

    claim = db.relationship(
        'Claim',
        backref='predicate',
        cascade="all, delete-orphan",
        lazy='dynamic'
    )
    """Claim associated with this predicate."""

    def __repr__(self):
        """Printable version of the Predicate object."""
        return '<Predicate {}'.format(self.name)
