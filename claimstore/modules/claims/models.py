from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID, JSONB
from claimstore.app import db


class Claim(db.Model):
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
    created = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp()
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
        return '<Claim {}>'.format(self.uuid)


class Claimant(db.Model):
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
        db.DateTime,
        default=db.func.current_timestamp(),
    )
    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
        index=True
    )
    url = db.Column(db.String)

    def __repr__(self):
        return '<Claimant {}>'.format(self.uuid)


class IdentifierType(db.Model):
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
        return '<IdentifierType {}>'.format(self.name)


class Predicate(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String,
        nullable=False,
        unique=True,
        index=True
    )

    def __repr__(self):
        return '<Predicate {}'.format(self.name)
