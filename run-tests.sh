#!/bin/sh
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

sphinx-apidoc -f -e -o docs/api/ claimstore
if [ -n "$(git status -s)" ]; then
  echo
  echo "ERROR: there is a mismatch between sphinx-apidoc output and the actual content of docs/api/. Check 'git status'."
  exit 1
fi
sphinx-build -qnNW docs docs/_build/html
python setup.py test
sphinx-build -qnNW -b doctest docs docs/_build/doctest
