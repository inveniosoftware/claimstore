import os
import json
import jsonschema
from flask import current_app


def get_json_schema(schema):
    """Return a given json schema.

    The argument schema should have the format module.schema_name (e.g. claims.claimants)
    """

    module_name, schema_name = schema.split(".")
    schema_file_path = os.path.join(
        current_app.config['BASE_DIR'],
        'claimstore',
        'static',
        'json',
        'schemas',
        module_name,
        '{}.json'.format(schema_name)
    )

    with open(schema_file_path) as f:
        return f.read()


def validate_json(json_input, schema):
    """Validate JSON against a given schema."""

    if schema:
        schema_content = get_json_schema(schema)
        jsonschema.validate(json_input, json.loads(schema_content))
        return True
    return False
