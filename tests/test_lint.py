#!/usr/bin/python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2018, James Lu <james@overdrivenetworks.com>
# SPDX-FileCopyrightText: © 2026, Rob Keys <rob_keys@outlook.com>
# SPDX-License-Identifier: GPL-3.0-only
### BEGIN LICENSE
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
### END LICENSE

import subprocess
import unittest


class TestPylint(unittest.TestCase):
    def test_project_errors_only(self):
        """Run Pylint in error-only mode.

        The code may still function adequately, even with Pylint errors, but
        have some unusual code.
        """
        return_code = subprocess.call(["pylint", "-E", "variety"])
        # Not needed because nosetests displays the Pylint console output.
        # self.assertEqual(return_code, 0)

    # Uncomment for loads of diagnostics.
    # ~ def test_project_full_report(self):
    # ~ '''Only for the brave.
    # ~
    # ~ You will have to make judgement calls about your code standards that
    # ~ differ from the norm.
    # ~ '''
    # ~ return_code = subprocess.call(["pylint", "variety"])


if __name__ == "__main__":
    "You will get better results with nosetests."
    unittest.main()
