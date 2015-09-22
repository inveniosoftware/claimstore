# -*- coding: utf-8 -*-
#
# This file is part of ClaimStore.
# Copyright (C) 2015 CERN.
#
# ClaimStore is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# ClaimStore is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ClaimStore; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307,
# USA.

# Use Python-3.4:
FROM python:3.4

# Install some prerequisites ahead of `setup.py` in order to profit
# from the docker build cache:
RUN pip install Flask \
                Flask-AppFactory \
                Flask-Collect \
                Flask-RESTful \
                Flask-SQLAlchemy \
                isodate \
                jsonschema \
                psycopg2 \
                pytest \
                pytest-cache \
                pytest-cov \
                pytest-isort \
                pytest-pep8 \
                pytest-pep257 \
                pytz \
                sphinx \
                webtest

# Add sources to `code` and work there:
WORKDIR /code
ADD . /code

# Install ClaimStore:
RUN pip install -e .[tests]
RUN pip install -e .[docs]
RUN claimstore collect

# Run container as user `claimstore` with UID `1000`, which should match
# current host user in most situations:
RUN adduser --uid 1000 --disabled-password --gecos '' claimstore && \
    chown -R claimstore:claimstore /code

# Start ClaimStore application:
USER claimstore
CMD  ["python", "run.py"]
