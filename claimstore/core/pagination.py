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

"""Restful pagination."""

from flask import current_app, request, url_for
from flask_restful import reqparse


class RestfulSQLAlchemyPaginationMixIn(object):

    """Implement Restful pagination for SQLAlchemy model and Flask-Restful.

    It creates an instance of RequestParser that should be used by the
    Restful Resource implementation. By default, it adds two query fields to
    the Restful Resource:

    :param page: page from which to fetch the data
    :param per_page: amout of data per page
    """

    def __init__(self):
        """Initialize pagination property."""
        self.args_parser = reqparse.RequestParser()
        self._query = None
        self._page = None
        self._per_page = None
        self._pagination = None

        # Add extra arguments to Restful Resource
        self.args_parser.add_argument(
            'page', dest='page', type=int,
            default=current_app.config['CFG_PAGINATION_ARG_PAGE'],
            location='args', trim=True,
            help='Page from where to fetch data'
        )
        self.args_parser.add_argument(
            'per_page', dest='per_page', type=int,
            default=current_app.config['CFG_PAGINATION_ARG_PER_PAGE'],
            location='args', trim=True,
            help='Amount of data per page'
        )

    def paginate(self, query, page, per_page):
        """Paginate query.

        :param query: query object from SQLAlchemy.
        :param page: page from which to fetch data.
        :param per_page: amount of data per page.
        """
        self._query = query
        self._page = page
        self._per_page = per_page
        self._pagination = self._query.paginate(self._page,
                                                self._per_page,
                                                False)
        return self._pagination.items

    def set_link_header(self, response, **kwargs):
        """Set Link details in the response header.

        :param response: Flask Response object.
        """
        links = self._links(**kwargs)
        keys = ("first", "prev", "next", "last")
        links_string = ",".join([links[key] for key in keys if key in links])
        response.headers['Link'] = links_string
        response.headers['Content-Type'] = 'application/json'

    def _links(self, endpoint=None, args=None):
        """Generate links for the headers.

        :param endpoint: the URL endpoint
        :param args: the arguments of request
        """
        if not endpoint:
            endpoint = request.endpoint
        if not args:
            args = request.args

        links = {}
        link_template = '<{}>; rel="{}"'

        # arguments to stick to the URL
        url_args = dict(args)
        # url_args['page'] will be updated for every link
        url_args['page'] = 1
        url_args['per_page'] = self._per_page

        # generate link for rel first
        links['first'] = link_template.format(
            url_for(endpoint, **url_args), "first"
        )

        # generate link for prev if it exists
        if self._pagination.has_prev:
            url_args['page'] = self._page - 1
            links['prev'] = link_template.format(
                url_for(endpoint, **url_args), "prev"
            )

        # generate link for next if it exists
        if self._pagination.has_next:
            url_args['page'] = self._page + 1
            links['next'] = link_template.format(
                url_for(endpoint, **url_args), "next"
            )

        # generate link for last
        url_args['page'] = self._pagination.pages
        links['last'] = link_template.format(
            url_for(endpoint, **url_args), "last"
        )
        return links
