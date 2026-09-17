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

import os
import unittest

from tests.TestDownloader import test_download_one_for
from variety.plugins.builtin.downloaders.MediaRSSDownloader import MediaRSSDownloader
from variety.plugins.builtin.downloaders.MediaRSSSource import MediaRSSSource


@unittest.skipIf(
    os.getenv("SKIP_DOWNLOADER_TESTS"), "Skipping downloader tests (SKIP_DOWNLOADER_TESTS is set)"
)
class TestMediaRssDownloader(unittest.TestCase):
    def test_download_one(self):
        test_download_one_for(
            self,
            MediaRSSSource().create_downloader(
                "https://backend.deviantart.com/rss.xml?type=deviation&q=leaves"
            ),
        )

    def test_validate_deviantart(self):
        self.assertTrue(
            MediaRSSDownloader.validate(
                "https://backend.deviantart.com/rss.xml?type=deviation&q=leaves"
            )
        )

    def test_validate_non_media_rss(self):
        self.assertFalse(MediaRSSDownloader.validate("https://www.dnevnik.bg/rss/?page=index"))

    def test_validate_non_rss(self):
        self.assertFalse(MediaRSSDownloader.validate("https://www.google.com/"))


if __name__ == "__main__":
    unittest.main()
