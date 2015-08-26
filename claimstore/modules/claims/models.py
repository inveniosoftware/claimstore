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

    """Represents a Claim."""

    uid = db.Column(
        db.Integer,
        primary_key=True
    )
    uuid = db.Column(
        UUID,
        nullable=False,
        unique=True,
        default=lambda: str(uuid4())
    )
    received = db.Column(
        UTCDateTime,
        default=now_utc,
        nullable=False
    )
    created = db.Column(
        UTCDateTime,
        nullable=False
    )
    claimant_id = db.Column(
        db.Integer,
        db.ForeignKey('claimant.uid'),
        nullable=False
    )
    subject_type_id = db.Column(
        db.Integer,
        db.ForeignKey('identifier_type.uid'),
        nullable=False
    )
    subject_value = db.Column(
        db.String,
        nullable=False
    )
    predicate_id = db.Column(
        db.Integer,
        db.ForeignKey('predicate.uid'),
        nullable=False
    )
    certainty = db.Column(
        db.Integer,
        nullable=False
    )
    human = db.Column(db.Boolean)
    actor = db.Column(db.String)
    role = db.Column(db.String)
    object_type_id = db.Column(
        db.Integer,
        db.ForeignKey('identifier_type.uid'),
        nullable=False
    )
    object_value = db.Column(
        db.String,
        nullable=False
    )
    claim_details = db.Column(JSONB)

    def __repr__(self):
        """Printable version of the Claim object."""
        return '<Claim {}>'.format(self.uuid)


class Claimant(db.Model):

    """Represents a Claimant."""

    uid = db.Column(
        db.Integer,
        primary_key=True,
    )
    uuid = db.Column(
        UUID(),
        nullable=False,
        unique=True,
        default=lambda: str(uuid4()),
    )
    joined = db.Column(
        UTCDateTime,
        default=now_utc,
    )
    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
        index=True
    )
    url = db.Column(db.String)

    def __repr__(self):
        """Printable version of the Claimant object."""
        return '<Claimant {}>'.format(self.uuid)


class IdentifierType(db.Model):

    """Represents an identifier type."""

    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
        index=True
    )
    description = db.Column(
        db.String,
        nullable=False
    )
    url = db.Column(
        db.String,
        nullable=False
    )
    example_value = db.Column(
        db.String,
        nullable=False
    )
    example_url = db.Column(
        db.String,
        nullable=False
    )
    claimant_id = db.Column(
        db.Integer,
        db.ForeignKey('claimant.uid')
    )

    def __repr__(self):
        """Printable version of the IdentifierType object."""
        return '<IdentifierType {}>'.format(self.name)


class Predicate(db.Model):

    """Represents a predicate.

    The predicate defines the type of claim. An example of predicate could be:
    is_same_as.
    """

    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
        index=True
    )

    def __repr__(self):
        """Printable version of the Predicate object."""
        return '<Predicate {}'.format(self.name)
