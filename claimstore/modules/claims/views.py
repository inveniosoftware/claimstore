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

"""ClaimStore views."""

from flask import Blueprint, render_template

from claimstore.core.json import get_json_schema
from claimstore.modules.claims.restful import blueprint as restful_bp

views_bp = Blueprint(
    'claims_views',
    __name__,
    template_folder='templates',
    static_folder='static'
)

blueprints = [views_bp, restful_bp]


@views_bp.route('/', methods=['GET'])
def index():
    """Render the home page for ClaimStore."""
    return render_template('claims/cover.html', active_menu='home')


@views_bp.route('/subscription', methods=['GET'])
def subscription():
    """Render the subscription form page."""
    return render_template(
        "claims/subscription.html",
        json_schema=get_json_schema('claims.claimant')
    )


@views_bp.route('/claimsubmit', methods=['GET'])
def claimsubmit():
    """Render the claim submission form page."""
    return render_template(
        "claims/claim_submit.html",
        json_schema=get_json_schema('claims.claim')
    )


@views_bp.route('/contact', methods=['GET'])
def contact():
    """Render the contact page."""
    return render_template("claims/contact.html", active_menu='contact')
