#!/usr/bin/python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2022, Peter Levi <peterlevi@peterlevi.com>
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
from variety.AttrDict import AttrDict
from variety.plugins.builtin.downloaders.UnsplashConfigurableSource import (
    UnsplashConfigurableSource,
)


@unittest.skipIf(
    os.getenv("SKIP_DOWNLOADER_TESTS"), "Skipping downloader tests (SKIP_DOWNLOADER_TESTS is set)"
)
class TestUnsplashConfigurableDownloader(unittest.TestCase):
    def _source(self):
        parent = AttrDict()
        parent.size_ok = lambda x, y: True
        source = UnsplashConfigurableSource()
        source.set_variety(parent)
        return source

    def test_download_one(self):
        test_download_one_for(self, self._source().create_downloader("landscape"))

    def test_validate(self):
        source = self._source()
        self.assertIsNone(source.validate("nature")[1])
        self.assertIsNone(source.validate("https://unsplash.com/s/photos/landscape")[1])
        self.assertIsNone(source.validate("https://unsplash.com/@pawel_czerwinski")[1])
        self.assertIsNone(
            source.validate("https://unsplash.com/collections/3694365/Gradient-Nation")[1]
        )

    def test_fill_queue(self):
        dl = self._source().create_downloader("nature")
        queue = dl.fill_queue()
        self.assertTrue(len(queue) > 0)


if __name__ == "__main__":
    unittest.main()
