-----------------
Restful Resources
-----------------


Subscribe to ClaimStore
=======================

.. autosimple:: claimstore.modules.claims.restful.ClaimantResource.post

**Usage**:

* From python:

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

    .. sourcecode:: bash

        $http POST http://localhost:5000/subscribe < tests/myclaimstore/config/claimants/cds.json

* From cURL:

    .. sourcecode:: bash

        $curl http://localhost:5000/subscribe -H "Content-Type: application/json" -d @tests/myclaimstore/config/claimants/inspire.json -X POST -v



Submit a claim
==============

.. autosimple:: claimstore.modules.claims.restful.ClaimResource.post

**Usage**:

* From python:

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

    .. sourcecode:: bash

        $http POST http://localhost:5000/claims < tests/myclaimstore/data/claims/cds.1.json

* From cURL:

    .. sourcecode:: bash

        $curl http://localhost:5000/claims -H "Content-Type: application/json" -d @tests/myclaimstore/data/claims/inspire.1.json -X POST -v


List claims
===========

.. autosimple:: claimstore.modules.claims.restful.ClaimResource.get

**Usage**:

* From python:

    .. sourcecode:: python

        import requests
        response = requests.get("http://localhost:5000/claims")
        print response.json()

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: bash

        $http GET http://localhost:5000/claims

* From cURL:

    .. sourcecode:: bash

        $curl http://localhost:5000/claims


List identifiers
================

.. autosimple:: claimstore.modules.claims.restful.IdentifierResource.get

**Usage**:

* From python:

    .. sourcecode:: python

        import requests
        response = requests.get("http://localhost:5000/identifiers")
        print response.json()

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: bash

        $http GET http://localhost:5000/identifiers

* From cURL:

    .. sourcecode:: bash

        $curl http://localhost:5000/identifiers


List predicates
===============

.. autosimple:: claimstore.modules.claims.restful.PredicateResource.get

**Usage**:

* From python:

    .. sourcecode:: python

        import requests
        response = requests.get("http://localhost:5000/predicates")
        print response.json()

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: bash

        $http GET http://localhost:5000/predicates

* From cURL:

    .. sourcecode:: bash

        $curl http://localhost:5000/predicates


List equivalent identifiers
===========================

.. autosimple:: claimstore.modules.claims.restful.EquivalentIdResource.get

**Usage**:

* From python:

    .. sourcecode:: python

        import requests
        response = requests.get("http://localhost:5000/eqids")
        print response.json()

* From `httpie <https://github.com/jkbrzt/httpie>`_:

    .. sourcecode:: bash

        $http GET http://localhost:5000/eqids

* From cURL:

    .. sourcecode:: bash

        $curl http://localhost:5000/eqids


