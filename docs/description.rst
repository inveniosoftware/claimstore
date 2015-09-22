-----------
Description
-----------

This part of the documentation presents technical description of the
ClaimStore system.

   *Consider a collaborative system of independent digital library
   heterogeneous services (S1, S2, ...) that want to exchange
   information about the data objects (O1, O2, ...) of various types
   (T1, T2, ...) that they manage.*

For example, the collaborative network of ADS, arXiv, and INSPIRE that
exchanges information about papers and people using arXiv IDs, ADS
bibcodes, ORCID, DOI persistent identifier types.

Defining collaborative network
------------------------------

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

Making claims
-------------

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
      "predicate": "is_same_as",
      "certainty": 1,
      "object": {
          "type": "ADS_BIBCODE",
          "value": "2005astro.ph..1001H"
      },
      "created": "2015-05-26T11:00:00Z"
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
      "predicate": "is_same_as",
      "certainty": 0.9,
      "object": {
          "type": "ADS_BIBCODE",
          "value": "2005astro.ph..1001H"
      },
      "arguments": {
          "human": 0,
          "actor": "ADS_record_generator"
      },
      "created": "2015-05-26T11:00:00Z"
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
      "predicate": "is_same_as",
      "certainty": 1,
      "object": {
          "type": "CDS_RECORD_ID",
          "value": "2001192"
      },
      "arguments": {
          "human": 0,
          "actor": "CDS_submission"
      },
      "created": "2015-05-26T11:00:00Z"
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
      "predicate": "is_same_as",
      "certainty": 0.8,
      "object": {
          "type": "DOI",
          "value": "10.1103/PhysRevE.62.7422"
      },
      "arguments": {
          "human": 1,
          "actor": "John Doe",
          "role": "cataloguer"
      },
      "created": "2015-05-26T11:00:00Z"
    }

Using claims
------------

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
      "predicate": "is_same_as",
      "certainty": 0.8,
      "object": {
          "type": "DOI",
          "value": "10.1103/PhysRevE.62.7422"
      },
      "arguments": {
          "human": 1,
          "actor": "John Doe",
          "role": "cataloguer"
      },
      "created": "2015-05-26T11:00:00Z",
      "recieved": "2015-05-26T11:00:00Z"
    },
    {
      "claimant": "ARXIV",
      "subject": {
          "type": "ARXIV_ID",
          "value": "cond-mat/9906097"
       },
      "predicate": "is_same_as",
      "certainty": 1.0,
      "object": {
          "type": "DOI",
          "value": "10.1103/PhysRevE.62.7422"
      },
      "arguments": {
          "human": 1,
          "actor": "John Doe",
          "role": "author"
      },
      "created": "2015-05-26T11:00:00Z",
      "recieved": "2015-05-26T11:00:00Z"
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

Managing claims
---------------

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

Notifications
-------------

The usual usage of ClaimStore by the services is (1) pushing own claim
information to the ClaimStore in order to register new claims and (2)
pulling information about others' claims from the ClaimStore as the
service needs them.

Alternatively, another mode of service operation could include (3)
registering to be automatically notified via push notifications in
case somebody claims something about a certain object types.  This
could come as a later extension.

Authorisations
--------------

After a service registers in the collaborative network, it is given a
secret key that the service could use to push the claim information.

Each participating service is allowed to read claims made by others.

This would be sufficient for a simple start of the service.  A
possible extension could include (1) opening parts of the claim
database for other non-participating clients, or (2) introducing
trusted partners making claims on others' behalf, etc.
