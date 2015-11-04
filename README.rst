============
 ClaimStore
============

.. image:: https://travis-ci.org/inveniosoftware/claimstore.svg?branch=master
   :target: https://travis-ci.org/inveniosoftware/claimstore

.. image:: https://coveralls.io/repos/inveniosoftware/claimstore/badge.svg?branch=master
   :target: https://coveralls.io/r/inveniosoftware/claimstore

.. image:: https://img.shields.io/badge/licence-GPL_3-green.svg?style=flat
   :target: https://raw.githubusercontent.com/inveniosoftware/claimstore/master/LICENSE

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/inveniosoftware/claimstore?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge

About
-----

ClaimStore is a mini-service permitting to exchange information about
claims done within a system of collaborating heterogeneous digital
repositories or information services.

Installation
------------

Using Docker
++++++++++++

.. code-block:: console

   $ docker-compose build
   $ docker-compose run --rm web /code/run-tests.sh
   $ docker-compose up

Using command line
++++++++++++++++++

.. code-block:: console

   $ mkvirtualenv claimstore --python=$(which python3.4)
   $ apt-get install npm  # install nodejs
   $ npm install -g bower
   $ pip install -e.[tests,docs].
   $ bower install
   $ claimstore collect
   $ export SQLALCHEMY_DATABASE_URI=postgres://postgres:postgres@db:5432/postgres  # replace with your database URI
   $ claimstore database create
   $ claimstore database populate  # optional
   $ python setup.py test
   $ claimstore run

Documentation
-------------

- `claimstore.readthedocs.org <http://claimstore.readthedocs.org/>`_
