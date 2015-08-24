================
 RFC ClaimStore
================

Tibor Simko 2015-05-26 (updated 2015-08-10)

1. About
========

This document describes ClaimStore, a new proposed mini service that
permits to exchange information about information claims within a set
of collaborating heterogeneous information services.

A primary use case example is the exchange of information about
persistent identifiers (such as DOI) in the domain of astrophysics and
particle physics among `ADS <http://adswww.harvard.edu/>`_, `arXiv
<http://arxiv.org/>`_, and `INSPIRE <http://inspirehep.net/>`_
services.  This would permit to better track and disambiguate papers,
offer cross-linking between services, or offer cross-search between
services.

The driving idea behind ClaimStore is to offer a neutral micro-service
that would be (1) storing claims that various collaborating services
perform and (2) answering questions about claims.

2. Description
==============

   *Consider a collaborative system of independent digital library
   heterogeneous services (S1, S2, ...) that want to exchange
   information about the data objects (O1, O2, ...) of various types
   (T1, T2, ...) that they manage.*

For example, the collaborative network of ADS, arXiv, and INSPIRE that
exchanges information about papers and people using arXiv IDs, ADS
bibcodes, ORCID, DOI persistent identifier types.

2.1 Defining collaborative network
----------------------------------

The collaborative network of services is defined means of describing
each service and each persistent object types that they usually
manage.  Each participating service in the network, such as::

  .
                               +-------+
           +-------+           | arXiv |            +---------+
           |  ADS  |           +-------+            | INSPIRE |
           +-------+                                +---------+


                           +--------------+               +-----+
                           |  ClaimStore  |               | ... |
                           +--------------+               +-----+

        +-----------+
        | CERN Data |                               +--------+
        +-----------+        +---------+            | Zenodo |
                             | HEPDATA |            +--------+
                             +---------+


will describe the assets it manages, for example, INSPIRE manages
record IDs and person IDs::

  {
    "service": "INSPIRE",
    "url": "http://inspirehep.net",
    "persistent_identifiers": [
       {
         "type": "INSPIRE_RECORD_ID",
         "description": "INSPIRE record",
         "url": "http://inspirehep.net/record/<INSPIRE_RECORD_ID>",
         "example_value": "123",
         "example_url": "http://inspirehep.net/record/123",
       },
       {
         "type": "INSPIRE_AUTHOR_ID",
         "description": "INSPIRE author",
         "url": "http://inspirehep.net/author/<INSPIRE_AUTHOR_ID>",
         "example_value": "J.R.Ellis.1",
         "example_url": "http://inspirehep.net/author/J.R.Ellis.1",
       },
    ],
  }

Optionally, the service can also expose some information about how the
claims are asserted, for example::

  {
    "service": "INSPIRE",
    "url": "http://inspirehep.net",
    "persistent_identifiers": [
       {
         "type": "INSPIRE_RECORD_ID",
         "description": "INSPIRE record",
         "url": "http://inspirehep.net/record/<INSPIRE_RECORD_ID>",
         "example_value": "123",
         "example_url": "http://inspirehep.net/record/123",
       },
       {
         "type": "INSPIRE_AUTHOR_ID",
         "description": "INSPIRE author",
         "url": "http://inspirehep.net/author/<INSPIRE_AUTHOR_ID>",
         "example_value": "J.R.Ellis.1",
         "example_url": "http://inspirehep.net/author/J.R.Ellis.1",
       },
    ],
    "certainty_levels": [
      {
        "1.0": "human approved"
      },
      {
        "0.5": "trusted algorithm"
      },
      {
        "0.1": "less trusted algorithm"
      },
      {
        "0.0": "guess"
      }
    ]
  }

Defining all services in this way will define our (1) operational
service nework (ADS, arXiv, INSPIRE, HEPDATA, etc), (2) data objects
(papers, people, software, data, etc) and (3) persistent identifier
types (arXIv ID, ADS bibcode, ORCID, DOI, etc) that the network uses.

2.2 Making claims
-----------------

Each service can make claims about objects, for example:

   *Service S1 says that object O1 of type T1 is the same as the
   object O2 of type T2 with a certainty of C.*

For example, ADS can claim that ``arXiv:astro-ph/0501001`` is having
bibcode ``2005astro.ph..1001H``::

    {
      "claimant": "ADS",
      "subject": {
          "type": "ARXIV_ID",
          "value": "astro-ph/0501001"
       },
      "claim": {
          "predicate": "is_same_as",
          "datetime": "2015-05-26T11:00:00Z",
          "certainty": 1,
      },
      "object": {
           "type": "ADS_BIBCODE",
           "value": "2005astro.ph..1001H"
      }
    }

Each individual claim can optionally include a free set of additional
parameters detailing the claim, for example:

   *... as was asserted on day D1 using algorithm A1 with parameters
   P1, P2, P3 and subsequently verified by humans H1 and H2 using
   external databases E1 and E2.*

For example, we can say that the ADS bibcode was added automatically
by a trusted program::

    {
      "claimant": "ADS",
      "subject": {
          "type": "ARXIV_ID",
          "value": "astro-ph/0501001"
       },
      "claim": {
          "predicate": "is_same_as",
          "datetime": "2015-05-26T11:00:00Z",
          "certainty": 0.9,
          "arguments": {
             "human": 0,
             "actor": "ADS_record_generator"
          }

      },
      "object": {
           "type": "ADS_BIBCODE",
           "value": "2005astro.ph..1001H"
      }
    }

A service would usually claim something about the objects it manages.
In the following example, CDS claims that "CMS-PAS-HIG-14-008" has a
persistent CDS record ID 2001192::

    {
      "claimant": "CDS",
      "subject": {
          "type": "CDS_REPORT_NUMBER",
          "value": "CMS-PAS-HIG-14-008"
       },
      "claim": {
          "predicate": "is_same_as",
          "datetime": "2015-05-26T11:00:00Z",
          "certainty": 1,
          "arguments": {
              "human": 0,
              "actor": "CDS_submission"
           }
      },
      "object": {
           "type": "CDS_RECORD_ID",
           "value": "2001192"
      }
    }

A service can claim statements about holdings of other services in the
the collaborative network.  For example, INSPIRE can claim that the
arXiv paper "cond-mat/9906097" is having DOI of
"10.1103/PhysRevE.62.7422" with high certainty, as it was confirmed by
an apprentice cataloguer::

    {
      "claimant": "INSPIRE",
      "subject": {
          "type": "ARXIV_ID",
          "value": "cond-mat/9906097"
       },
      "claim": {
          "predicate": "is_same_as",
          "datetime": "2015-05-26T11:00:00Z",
          "certainty": 0.8,
          "arguments": {
              "human": 1,
              "actor": "John Doe",
              "role": "cataloguer"
           }
      },
      "object": {
           "type": "DOI",
           "value": "10.1103/PhysRevE.62.7422"
      }
    }

2.3 Using claims
----------------

Each participating service can ask questions about claims related to
individual objects, such as:

   *Who knows anything about DOI "10.1103/PhysRevE.62.7422"?*

which would be asked via::

  GET /claims/?type=DOI&value=10.1103/PhysRevE.62.7422

Upon seeing this query, the ClaimStore would return a list of claims
about this DOI (whether found as a subject or an object of the claim),
in chronological order, for example::

  [
    {
      "claimant": "INSPIRE",
      "subject": {
          "type": "ARXIV_ID",
          "value": "cond-mat/9906097"
       },
      "claim": {
          "predicate": "is_same_as",
          "datetime": "2015-05-26T11:00:00Z",
          "certainty": 0.8,
          "arguments": {
              "human": 1,
              "actor": "John Doe",
              "role": "cataloguer"
           }
      },
      "object": {
           "type": "DOI",
           "value": "10.1103/PhysRevE.62.7422"
      }
    },
    {
      "claimant": "ARXIV",
      "subject": {
          "type": "ARXIV_ID",
          "value": "cond-mat/9906097"
       },
      "claim": {
          "predicate": "is_same_as",
          "datetime": "2015-05-26T11:00:00Z",
          "certainty": 1.0,
          "arguments": {
              "human": 1,
              "actor": "John Doe",
              "role": "author"
           }
      },
      "object": {
           "type": "DOI",
           "value": "10.1103/PhysRevE.62.7422"
      }
    },
  ]

ClaimStore will faithfully return the list of any claims it knows
about this DOI without manipulating them.

Each service can ask summary questions as well, such as:

   *What did CERN Open Data ever said about software packages with
   high confidence?*

which would be asked via::

  GET /claims/?claimant=CERNOPENDATA&type=SOFTWARE&confidence=50+

More complex querying on the JSON structure of claims can be done, for
example::

   *Which claims were done by John Doe from INSPIRE between 2012-01-23
   and 2012-08-07?*

which would be asked via::

   GET /claims/?claimant=INSPIRE&since=2012-01-03&until=2012-08-07&claim.arguments.actor=John%20Doe

e.g. because we learned that the procedure was buggy at the time and
would like to clean it.

Any such possible evolution depends on the further uses of the system
beyond simple persistent ID exchange.

2.4 Managing claims
-------------------

ClaimStore is a neutral application dedicated to efficiently storing
individual claims and answering questions about them.  ClaimStore
*does not* attempt to impose any workflow or resolve any possible
conflicts, such as when service S1 claims that object O1 is the same
as object O2 with certainty C1, while service S2 claims that object O1
is the same as object O3 with certainty C2.  The resolution of
conflicts and is left upon each participating service that can
implement a solution fitting its own workflows and quality standards.

For example, when INSPIRE receives an arXiv paper of the "astro-ph"
category, it can ask ClaimStore about all the claims related to it::

  GET /claims/?type=ARXIV_ID&value=arXiv:1505.06718&claimant=ADS

as it may decide to trust ADS's claims more than author claims or
publisher claims in this subject domain.

If a service wants to revoke an old claim, it can make a new claim
with higher certainty.

The bottom line is that ClaimStore does not attempt to do any
judgement about claims, nor does it do any management of claims beyond
simply storing what the services claimed and answering questions about
stored assets.

2.5 Notifications
-----------------

The usual usage of ClaimStore by the services is (1) pushing own claim
information to the ClaimStore in order to register new claims and (2)
pulling information about others' claims from the ClaimStore as the
service needs them.

Alternatively, another mode of service operation could include (3)
registering to be automatically notified via push notifications in
case somebody claims something about a certain object types.  This
could come as a later extension.

2.6 Authorisations
------------------

After a service registers in the collaborative network, it is given a
secret key that the service could use to push the claim information.

Each participating service is allowed to read claims made by others.

This would be sufficient for a simple start of the service.  A
possible extension could include (1) opening parts of the claim
database for other non-participating clients, or (2) introducing
trusted partners making claims on others' behalf, etc.

3. Design
=========

3.1 Architecture
----------------

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

3.2 Database
------------

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

3.3 Claim types
---------------

The primary motivation behind ClaimStore was the exchange of
information about persistent identifiers, hence the typical claim
types are:

- ``is_same_as``
- ``is_different_than``

However, the system is generic enough to accept any kind of claims, so
the ClaimStore could be easily used to store information about other
types of relations, such as "is_cited_by" to indicate citation
relations:

- ``is_cited_by``

Examples of other possible relations include errata and superseded
papers:

- ``is_erratum_of``
- ``is_superseded_by``

or relations between papers, data and software:

- ``is_software_for_paper``
- ``is_dataset_for_paper``
- ``is_dataset_for_software``

For example, imagine the following table of claims::

  subject               predicate    object
  --------------------  -----------  -------------------
  arXiv:hep-th/0101001  is_same_as   DOI:10.1234/foo.bar
  arXiv:hep-th/0101001  is_cited_by  arXiv:1506.07188

One could then ask queries like *who does know about DOI
10.1234/foo.bar?* and the system could return only direct claims::

  GET /claims/?type=DOI&value=10.1234/foo.bar

listing only the first relation, or else we could also ask to include
all indirect claims::

  GET /claims/?type=DOI&value=10.1234/foo.bar&include=indirect&certainty=0.5+

which would return both relations.

4. Implementation
-----------------

CERN-IT offers to implement and run the central ClaimStore service and
to provide example Python client libraries.  Each participating
digital library service would then plug the client to post their
claims and use the client to retrieve the claims of others and use
them as they see fit in their workflows.

5. Operation
------------

CERN-IT offers to run and monitor ClaimStore's operation using the
CERN OpenStack infrastructure.

Post Scriptum
-------------

Caveat lector: this RFC is meant to exemplify general ideas behind the
ClaimStore in order to clarify its design and future use cases.  The
concrete implementation with respect to JSON structure etc may change.
