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

"""Flask app creation."""

from flask import Flask, jsonify, render_template
from flask.ext.sqlalchemy import SQLAlchemy

from claimstore.core.exception import InvalidUsage

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy()


def handle_invalid_usage(error):
    """Handle invalid usage exception."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def create_app(db_create_all=False):
    """Create flask app."""
    app = Flask(__name__)

    # Configurations
    app.config.from_object('config')

    # Blueprints
    from claimstore.modules.claims.restful import claims_restful
    from claimstore.modules.claims.views import claims_views

    app.register_blueprint(claims_views)
    app.register_blueprint(claims_restful)

    # Init databse
    db.init_app(app)
    if db_create_all:
        # Create schema
        with app.app_context():
            db.create_all()
            # Populate with predefined predicates
            from claimstore.modules.claims.models import Predicate
            predicates = [
                'is_same_as',
                'is_different_than',
                'is_erratum_of',
                'is_superseded_by',
                'is_cited_by',
                'is_software_for',
                'is_dataset_for'
            ]
            for pred_name in predicates:
                if not Predicate.query.filter_by(name=pred_name).first():
                    predicate = Predicate(name=pred_name)
                    db.session.add(predicate)
            db.session.commit()

    # Register exceptions
    app.register_error_handler(InvalidUsage, handle_invalid_usage)

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    return app
