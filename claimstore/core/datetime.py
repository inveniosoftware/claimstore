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

"""DateTime related tools."""

from datetime import datetime

import pytz


def now_utc():
    """Return UTC datetime with tzinfo."""
    return pytz.utc.localize(datetime.utcnow())


def loc_date_utc(date):
    """Localise a naive date in UTC.

    :param date: naive date
    :returns: date with UTC tzinfo
    """
    return pytz.utc.localize(date)
