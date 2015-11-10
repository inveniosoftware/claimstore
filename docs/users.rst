-----------------
Restful Resources
-----------------


Subscribe to ClaimStore
=======================

.. autosimple:: claimstore.restful.ClaimantResource.post

**Usage**:

* From `python <https://www.python.org/>`_:

    .. sourcecode:: python

        import json
        import requests

        url = "http://localhost:5000/subscribe/
        headers = {"Content-Type": "application/json"}
        with open(
            '$PROJECT_HOME/tests/config/claimants/cds.json'
        ) as f:
            data=json.dumps(f.read())
        r = requests.post(url, data=data, headers=headers)

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: console

        $ http POST http://localhost:5000/subscribe < tests/myclaimstore/config/claimants/cds.json

* From `curl <http://curl.haxx.se/>`_:

    .. sourcecode:: console

        $ curl http://localhost:5000/subscribe \
               -H "Content-Type: application/json" \
               -d @tests/myclaimstore/config/claimants/inspire.json -X POST -v



Submit a claim
==============

.. autosimple:: claimstore.restful.ClaimResource.post

**Usage**:

* From `python <https://www.python.org/>`_:

    .. sourcecode:: python

        import json
        import requests

        url = "http://localhost:5000/claims/
        headers = {"Content-Type": "application/json"}
        with open(
            '$PROJECT_HOME/tests/config/claims/cds.1.json'
        ) as f:
            data=json.dumps(f.read())
        r = requests.post(url, data=data, headers=headers)

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: console

        $ http POST http://localhost:5000/claims < tests/myclaimstore/data/claims/cds.1.json

* From `curl <http://curl.haxx.se/>`_:

    .. sourcecode:: console

        $ curl http://localhost:5000/claims \
               -H "Content-Type: application/json" \
               -d @tests/myclaimstore/data/claims/inspire.1.json -X POST -v


List claims
===========

.. autosimple:: claimstore.restful.ClaimResource.get

**Usage**:

* From `python <https://www.python.org/>`_:

    .. sourcecode:: python

        import requests
        response = requests.get("http://localhost:5000/claims")
        print response.json()

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: console

        $ http GET http://localhost:5000/claims

* From `curl <http://curl.haxx.se/>`_:

    .. sourcecode:: console

        $ curl http://localhost:5000/claims


List identifiers
================

.. autosimple:: claimstore.restful.IdentifierResource.get

**Usage**:

* From `python <https://www.python.org/>`_:

    .. sourcecode:: python

        import requests
        response = requests.get("http://localhost:5000/identifiers")
        print response.json()

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: console

        $ http GET http://localhost:5000/identifiers

* From `curl <http://curl.haxx.se/>`_:

    .. sourcecode:: console

        $ curl http://localhost:5000/identifiers


List predicates
===============

.. autosimple:: claimstore.restful.PredicateResource.get

**Usage**:

* From `python <https://www.python.org/>`_:

    .. sourcecode:: python

        import requests
        response = requests.get("http://localhost:5000/predicates")
        print response.json()

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: console

        $ http GET http://localhost:5000/predicates

* From `curl <http://curl.haxx.se/>`_:

    .. sourcecode:: console

        $ curl http://localhost:5000/predicates


List equivalent identifiers
===========================

.. autosimple:: claimstore.restful.EquivalentIdResource.get

**Usage**:

* From `python <https://www.python.org/>`_:

    .. sourcecode:: python

        import requests
        response = requests.get("http://localhost:5000/eqids")
        print response.json()

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: console

        $ http GET http://localhost:5000/eqids

* From `curl <http://curl.haxx.se/>`_:

    .. sourcecode:: console

        $ curl http://localhost:5000/eqids
