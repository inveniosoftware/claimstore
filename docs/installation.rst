------------
Installation
------------

Using Docker
++++++++++++

.. code-block:: console

   $ docker-compose build
   $ docker-compose run --rm web bower install
   $ docker-compose run --rm web claimstore database create
   $ docker-compose run --rm web claimstore database populate  # optional
   $ docker-compose run --rm web /code/run-tests.sh
   $ docker-compose up

Using command line
++++++++++++++++++

.. code-block:: console

   $ mkvirtualenv claimstore --python=$(which python3.4)
   $ sudo apt-get install npm  # install nodejs
   $ sudo npm install -g bower
   $ pip install -e .[tests,docs]
   $ bower install
   $ export SQLALCHEMY_DATABASE_URI=postgres://postgres:postgres@db:5432/postgres
   $ claimstore database create
   $ claimstore database populate  # optional
   $ python setup.py test
   $ claimstore run
