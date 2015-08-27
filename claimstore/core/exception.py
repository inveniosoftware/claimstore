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

"""Definition of specific exceptions."""


class RestApiException(Exception):

    """Generic Rest API exception."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None, details=None):
        """Initialise the exception."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.details = details

    def to_dict(self):
        """Return exception as a dictionary."""
        rv = {
            'status': 'error',
            'message': self.message
        }
        if self.details:
            rv['details'] = self.details
        return rv


class InvalidJSONData(RestApiException):

    """Invalid JSON Data.

    Used to identify that JSON data that do not follow the appropiate schema.
    """

    pass


class InvalidRequest(RestApiException):

    """The REST request could not be fulfilled."""

    pass
