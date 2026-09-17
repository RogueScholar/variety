# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
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
import random
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from variety.plugins.downloaders.SimpleDownloader import SimpleDownloader
from variety.Util import Util, _

logger = logging.getLogger("variety")

random.seed()


class BingDownloader(SimpleDownloader):
    DESCRIPTION = _("Bing Photo of the Day")
    # n=100, but a max of eight images are actually returned…what a pity.
    BING_JSON_URL = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=100&mkt=en-US"

    @classmethod
    def get_info(cls):
        return {
            "name": "BingDownloader",
            "description": BingDownloader.DESCRIPTION,
            "author": "Peter Levi",
            "version": "0.1",
        }

    def get_source_type(self):
        return "bing"

    def get_description(self):
        return BingDownloader.DESCRIPTION

    def get_source_name(self):
        return "Bing"

    def get_source_location(self):
        return "https://www.bing.com/gallery/"

    def get_local_filename(self, url):
        return parse_qs(urlparse(url).query)["id"][0]

    def fill_queue(self):
        queue = []
        s = Util.fetch_json(BingDownloader.BING_JSON_URL)
        for item in s["images"]:
            try:
                if not item["wp"]:
                    # Not marked as a wallpaper
                    continue

                image_url = "https://www.bing.com" + item["urlbase"] + "_UHD.jpg"

                copyrightlink = item["copyrightlink"]
                if not "javascript:" in copyrightlink:
                    src_url = copyrightlink
                else:
                    filename = item["url"].split("/")[-1]
                    name = filename[0 : filename.find("_EN")]
                    src_url = "https://www.bing.com/gallery/#images/%s" % name

                try:
                    date = datetime.strptime(item["startdate"], "%Y%m%d").strftime("%Y-%m-%d")
                except:
                    date = item["startdate"]
                extra_metadata = {
                    "sourceType": "bing",
                    "sfwRating": 100,
                    "headline": "Bing Photo of the Day, %s" % date,
                    "description": item["copyright"],
                }
                queue.append((src_url, image_url, extra_metadata))
            except:
                logger.exception(lambda: "Could not process an item in the Bing JSON result.")

        random.shuffle(queue)
        return queue
