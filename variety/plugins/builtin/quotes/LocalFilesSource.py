# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2013–2022, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2018, Brandon Jiang <Brandon.jiang.a@outlook.com>
# SPDX-FileCopyrightText: © 2018, James Lu <james@overdrivenetworks.com>
# SPDX-FileCopyrightText: © 2019, Satheesh Kumar Mohan <sathyz@gmail.com>
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

import logging
import os
import re

from variety.plugins.IQuoteSource import IQuoteSource
from variety.profile import get_profile_path
from variety.Util import _

logger = logging.getLogger("variety")


class LocalFilesSource(IQuoteSource):
    def __init__(self):
        super(IQuoteSource, self).__init__()
        self.quotes = []

    @classmethod
    def get_info(cls):
        return {
            "name": "Local text files",
            "description": _(
                "Displays quotes, defined in local text files.\n"
                "Put your own txt files in: {}pluginconfig/quotes/.\n"
                "The file format is:\n\n"
                '"First quote." -- Author\n.\n'
                '"Second quote,\nwrapped onto a new line." -- Author\n.\nEtc. …\n\n'
                "Example: https://web.archive.org/web/0if_/https://github.com/ranjith19/random-quotes-generator/blob/master/quotes.txt"
            ).format(get_profile_path(expanded=False)),
            "author": "Peter Levi",
            "version": "0.1",
        }

    def needs_internet(self):
        return False

    def supports_search(self):
        return True

    def activate(self):
        if self.active:
            return

        super(LocalFilesSource, self).activate()

        self.quotes = []

        # Prefer files in the plugin configuration
        for f in os.listdir(self.get_config_folder()):
            if f.endswith(".txt"):
                self.load(os.path.join(self.get_config_folder(), f))

        # Use the defaults if there's nothing useful in the plugin config
        if not self.quotes:
            for f in os.listdir(self.folder):
                if f.endswith(".txt"):
                    self.load(os.path.join(self.folder, f))

    def deactivate(self):
        self.quotes = []

    def load(self, path):
        try:
            logger.info(lambda: "Loading quotes file %s" % path)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                s = f.read()
                for q in re.split(r"(^\.$|^%$)", s, flags=re.MULTILINE):
                    try:
                        if q.strip() and len(q.strip()) > 5:
                            parts = q.split("-- ")
                            quote = parts[0]
                            if quote[0] == quote[-1] == '"':
                                quote = "\u201c%s\u201d" % quote[1:-1]
                            author = parts[1].strip() if len(parts) > 1 else None
                            self.quotes.append(
                                {
                                    "quote": quote,
                                    "author": author,
                                    "sourceName": os.path.basename(path),
                                }
                            )
                    except Exception:
                        logger.debug(lambda: "Could not process local quote %s" % q)
        except Exception:
            logger.exception(lambda: "Could not load quotes file %s" % path)

    def get_random(self):
        return self.quotes

    def get_for_author(self, author):
        return [
            q for q in self.quotes if q["author"] and q["author"].lower().find(author.lower()) >= 0
        ]

    def get_for_keyword(self, keyword):
        return self.get_for_author(keyword) + [
            q for q in self.quotes if q["quote"].lower().find(keyword.lower()) >= 0
        ]
