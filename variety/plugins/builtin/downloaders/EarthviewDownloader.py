# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2022, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2022, Eric Roesch <roesch.eric@protonmail.com>
# SPDX-FileCopyrightText: © 2025, Joel Beckmeyer <joel@beckmeyer.us>
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

from variety.plugins.downloaders.ImageSource import Throttling
from variety.plugins.downloaders.SimpleDownloader import SimpleDownloader
from variety.Util import Util, _

# Acknowledgment to Henry Lim for providing the data used here previously at
# <https://github.com/limhenry/earthview>.
DATA_URL = "https://new-images-preview-dot-earth-viewer.appspot.com/_api/photos.json"

logger = logging.getLogger("variety")

random.seed()


class EarthviewDownloader(SimpleDownloader):
    DESCRIPTION = _("Google Earth View wallpapers")
    ROOT_URL = "https://new-images-preview-dot-earth-viewer.appspot.com/"

    @classmethod
    def get_info(cls):
        return {
            "name": "EarthviewDownloader",
            "description": EarthviewDownloader.DESCRIPTION,
            "author": "Peter Levi",
            "version": "0.1",
        }

    def get_description(self):
        return EarthviewDownloader.DESCRIPTION

    def get_source_type(self):
        return "earthview"

    def get_source_name(self):
        return "Earth View"

    def get_source_location(self):
        return self.ROOT_URL

    def fill_queue(self):
        queue = Util.fetch_json(DATA_URL)
        random.shuffle(queue)
        return queue

    def get_default_throttling(self):
        # This source has to be throttled lest maps overpower all other types
        # of images under Variety's default settings, and we have no other way
        # to control source "weights."
        return Throttling(max_downloads_per_hour=20, max_queue_fills_per_hour=None)

    def download_queue_item(self, item):
        item = Util.fetch_json(
            "https://new-images-preview-dot-earth-viewer.appspot.com/_api/" + item["slug"] + ".json"
        )
        region = item["region"]
        filename = "{}{} (ID-{}).jpg".format(
            region + ", " if region and region != "-" else "", item["country"], item["id"]
        )
        origin_url = EarthviewDownloader.ROOT_URL + str(item["slug"])
        image_url = item["photoUrl"]
        if not image_url.startswith("http"):
            image_url = "https://" + image_url

        extra_metadata = {"description": item.get("name"), "author": item.get("attribution")}
        return self.save_locally(
            origin_url, image_url, local_filename=filename, extra_metadata=extra_metadata
        )
