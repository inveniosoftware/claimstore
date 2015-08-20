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

from flask import render_template, Blueprint
from claimstore.core.json import get_json_schema


claims_views = Blueprint(
    'claims_views',
    __name__,
)


@claims_views.route('/', methods=['GET'])
def index():
    return render_template('cover.html', active_menu='home')


@claims_views.route('/subscription', methods=['GET'])
def subscription():
    return render_template(
        "subscription.html",
        json_schema=get_json_schema('claims.claimant')
    )


@claims_views.route('/api', methods=['GET'])
def api():
    return render_template("api.html", active_menu='api')


@claims_views.route('/contact', methods=['GET'])
def contact():
    return render_template("contact.html", active_menu='contact')
