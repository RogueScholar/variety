#!/usr/bin/python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2018, Brandon Jiang <Brandon.jiang.a@outlook.com>
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

import os
import unittest

from tests.TestDownloader import get_plugin_downloader, test_download_one_for


@unittest.skipIf(
    os.getenv("SKIP_DOWNLOADER_TESTS"), "Skipping downloader tests (SKIP_DOWNLOADER_TESTS is set)"
)
class TestBingDownloader(unittest.TestCase):
    def test_download_one(self):
        dl = get_plugin_downloader("BingDownloader")
        test_download_one_for(self, dl)

    def test_fill_queue(self):
        dl = get_plugin_downloader("BingDownloader")
        queue = dl.fill_queue()
        self.assertTrue(len(queue) > 0)


if __name__ == "__main__":
    unittest.main()
