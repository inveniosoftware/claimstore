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

"""Useful JSON-related methods."""

import json
import os
import pathlib

import jsonschema  # noqa (pytest-isort is happy, flake8 not here)
from flask import current_app


def get_json_schema(schema):
    """Return a given json schema.

    :param schema: schema to be fetched. It must be a string with the format:
                   module.schema_name (e.g. claims.claimants).
    :type schema: str.
    :returns: a str with the requested json schema.
    :rtype: str.
    """
    module_name, schema_name = schema.split(".")

    schema_file_path = os.path.join(
        current_app.config['BASE_DIR'],
        'claimstore',
        'modules',
        module_name,
        'static',
        'json',
        'schemas',
        '{}.json'.format(schema_name)
    )

    with open(schema_file_path) as f:
        return f.read()


def validate_json(json_input, schema):
    """Validate JSON against a given schema.

    :param json_input: a dict with the full json to be validated.
    :type json_input: dict.
    :param schema: JSON schema to use in the validation. It must be a string
                   with the format module.schema_name (e.g. claims.claimants).
    :type schema: str.
    :returns: True if `json_input` follows the schema. False otherwise.
    :rtype: bool.
    """
    if schema:
        schema_content = get_json_schema(schema)
        module_name, schema_name = schema.split('.')
        resolver = jsonschema.RefResolver('{}/'.format(
            pathlib.Path(
                os.path.join(
                    current_app.config['BASE_DIR'],
                    'claimstore',
                    'modules',
                    module_name,
                    'static',
                    'json',
                    'schemas'
                )
            ).as_uri()),
            schema_content
        )
        jsonschema.Draft4Validator(
            json.loads(schema_content),
            resolver=resolver
        ).validate(json_input)
        return True
    return False
