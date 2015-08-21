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

"""Basic run module."""

import argparse
from claimstore.app import create_app


def main():
    """Create app and run server."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--initdb",
        help="creates all db structure",
        action='store_true'
    )
    args = parser.parse_args()

    app = create_app(args.initdb)
    app.run(host='0.0.0.0', port=8080, debug=True)


if __name__ == '__main__':
    main()
