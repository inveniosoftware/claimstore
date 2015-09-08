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

"""ClaimStore configuration."""

import os

EXTENSIONS = [
    "flask_appfactory.ext.jinja2",
    "claimstore.ext.sqlalchemy",
    "claimstore.ext.collect"
]

PACKAGES = [
    "claimstore.modules.claims",
]

BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')

# Define the database as environment variable
if 'SQLALCHEMY_DATABASE_URI' in os.environ:
    SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']

# Define the IPs that can use the RESTful API. The list of IPs should be
# separated by whitespaces.
if 'CLAIMSTORE_ALLOWED_IPS' in os.environ and \
        os.environ['CLAIMSTORE_ALLOWED_IPS'].strip():
    CLAIMSTORE_ALLOWED_IPS = os.environ['CLAIMSTORE_ALLOWED_IPS']
else:
    CLAIMSTORE_ALLOWED_IPS = '127.0.0.1'
