from flask import Flask, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from claimstore.core.exception import InvalidUsage

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy()


def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def create_app(db_create_all=False):
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
