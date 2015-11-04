------------
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
