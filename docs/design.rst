Design
------

This part of the documentation presents general architecture, design
and implementation guidelines.

Architecture
------------

ClaimStore is an independent mini-application built upon our usual
Flask ecosystem:

- `Flask-AppFactory
  <https://github.com/inveniosoftware/flask-appfactory>`_ for general
  application loading
- `Flask-RESTful
  <https://github.com/flask-restful/flask-restful/>`_ for REST API
- `Flask-Notifications
  <https://github.com/inveniosoftware/flask-notifications>`_ for
  optional alerts
- `OAuth <http://oauth.net/>`_ for authorisation needs
- `SQLAlchemy <http://sqlalchemy.readthedocs.org/>`_ for DB abstraction
- `JSON Schema <http://json-schema.org/>`_ for JSON object description
- `PostgreSQL <http://www.postgresql.org/>`_ for DB persistence and
  JSON search

Database
--------

The information about network of services, data objects and persistent
identifier types, and claims about them is described via JSON snippets.

The JSON data is stored in several tables for ``claimants``,
``object_types`` etc.  The individual claims are stored in a
``claims`` table that uses both regular RDBMS and JSONB columns,
permitting some fast inter-table JOINs as well as free-format
additional claim parameters, for example::

  claims
  =======================
  uuid            integer
  created         date
  claimant        ref ->
  subject_type    ref ->
  subject_value   text
  claim           ref ->
  certainty       number
  claim_details   jsonb
  status          ref ->  e.g. to mark revoked claims
  object_type     ref ->
  object_value    text

The JSON format of claims is also checked against a formal JSON schema
to verify its validity upon claim submission.  There are several JSON
Schemata describing the system: one JSON schema describes a service,
another JSON schema describes a persistent ID type, another JSON
schema describes a claim, etc.

For searching the claim database, PostgreSQL/JSONB column type can be
used which offers efficient querying out of the box.  In case of
extended usage needs, JSON claims can be propagated to an
`Elasticsearch cluster
<https://www.elastic.co/products/elasticsearch>`_. that can increase
query speed and query language further.

Claim types
-----------

The primary motivation behind ClaimStore was the exchange of
information about persistent identifiers, hence the typical claim
types are:

- `is_same_as`: used when there is a 100% equivalence, e.g. a local copy of an
  arXiv record, with either the same or enriched metadata, e.g. ORCID
  corresponds to this INSPIRE ID
- `is_variant_of`: lesser claim, e.g. arXiv preprint and DOI of a
  published paper, e.g. when INSPIRE merges two sources into one

However, the system is generic enough to accept any kind of claims, so
the ClaimStore can also be used to store information about other
types of relations, such as:

- `is_author_of`: this person is the author of this document
- `is_contributor_to`: this person is supervisor/translator/spokesperson
  of this document
- `is_erratum_of`: e.g. if INSPIRE record R1 is variant of DOI1, and DOI2
  is erratum of DOI1, but INSPIRE merges all these in the same record,
  then there would be three claims: R1 is variant of DOI1, DOI2 is erratum of
  DOI1, R1 is variant of DOI2

Examples of other possible relations that could be included in the future
are:

- ``is_cited_by``
- ``is_superseded_by``
- ``is_software_for_paper``
- ``is_dataset_for_paper``
- ``is_dataset_for_software``

For example, imagine the following table of claims::

  subject               predicate      object
  --------------------  -----------    -------------------
  arXiv:hep-th/0101001  is_variant_of  DOI:10.1234/foo.bar
  arXiv:hep-th/0101001  is_same_as     arXiv:1506.07188

One could then ask queries like *who does know about DOI
10.1234/foo.bar?* and the system could return only direct claims::

  GET /claims/?type=DOI&value=10.1234/foo.bar

listing only the first relation, or else we could also ask to include
all indirect claims::

  GET /claims/?type=DOI&value=10.1234/foo.bar&include=indirect&certainty=0.5+

which would return both relations.
