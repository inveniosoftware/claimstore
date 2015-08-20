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
    return render_template("subscription.html", json_schema=get_json_schema('claims.claimant'))


@claims_views.route('/api', methods=['GET'])
def api():
    return render_template("api.html", active_menu='api')


@claims_views.route('/contact', methods=['GET'])
def contact():
    return render_template("contact.html", active_menu='contact')
