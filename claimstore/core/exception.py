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

"""Definition of specific exceptions."""


class RestApiException(Exception):

    """Generic Rest API exception."""

    status_code = 400

    def __init__(self, message, status_code=None, details=None):
        """Initialise the exception.

        :param message: Exception message.
        :type message: str.
        :param status_code: HTTP status code. By default it is 400.
        :type status_code: int.
        :param details: Extra details of the exception.
        :type details: str.
        """
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

    This exception is raised when  there is some JSON data that does not follow
    its associated JSON schema.
    """

    pass


class InvalidRequest(RestApiException):

    """REST request could not be fulfilled."""

    pass
