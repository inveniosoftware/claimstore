============
 ClaimStore
============

.. currentmodule:: claimstore

About
=====

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

Table of contents
=================

.. toctree::
   :maxdepth: 1
   :numbered:

   installation
   description
   design
   releases
   Users <users>
   developers
   API <api/modules>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
