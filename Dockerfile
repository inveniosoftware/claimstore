# -*- coding: utf-8 -*-
#
# This file is part of ClaimStore.
# Copyright (C) 2015 CERN.
#
# ClaimStore is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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

# Install some prerequisites ahead of `requirements.txt` in order to
# profit from the docker build cache:
RUN pip install flask \
                flask-sqlalchemy \
                jsonschema \
                pep257 \
                psycopg2 \
                pytest \
                pytest-cov \
                pytest-pep8 \
                sphinx

# Install all prerequisites:
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Add sources to `code` and work there:
WORKDIR /code
ADD . /code

# Run container as user `claimstore` with UID `1000`, which should match
# current host user in most situations:
RUN adduser --uid 1000 --disabled-password --gecos '' claimstore && \
    chown -R claimstore:claimstore /code

# Start ClaimStore application:
USER claimstore
CMD  ["python", "run.py"]
