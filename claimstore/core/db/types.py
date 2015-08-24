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

"""Custom database types."""

import pytz
from sqlalchemy import types


class UTCDateTime(types.TypeDecorator):

    """Custom UTC DateTime type."""

    impl = types.DateTime

    def process_bind_param(self, value, engine):
        """Process binding."""
        if value is not None:
            return value.astimezone(pytz.utc).replace(tzinfo=None)

    def process_result_value(self, value, engine):
        """Process result."""
        if value is not None:
            return value.replace(tzinfo=pytz.utc)
