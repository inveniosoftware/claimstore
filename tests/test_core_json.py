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

"""claimstore.core.json test suite."""

from claimstore.core.json import get_json_schema

from .base import ClaimStoreTestCase


class FlaskTestCase(ClaimStoreTestCase):

    """Testing claimstore.core.json."""

    def test_get_json_schema(self):
        """Testing `get_json_schema()`."""
        with self.app.app_context():
            assert '"title": "Service Name",' in \
                get_json_schema('claims.claimant')
            assert 'URL showing the identifier placeholder' in \
                get_json_schema('claims.claimant')
            assert '"required": ["type", "description", "url", ' + \
                '"example_value", "example_url"],' in \
                get_json_schema('claims.claimant')
