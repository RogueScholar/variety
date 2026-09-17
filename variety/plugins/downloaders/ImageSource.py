# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2018–2022, Peter Levi <peterlevi@peterlevi.com>
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

import abc
import collections
import logging
import time
from datetime import timedelta

from variety.plugins.IVarietyPlugin import IVarietyPlugin

logger = logging.getLogger("variety")


Throttling = collections.namedtuple(
    "Throttling", ["max_downloads_per_hour", "max_queue_fills_per_hour"]
)


class ImageSource(IVarietyPlugin, metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()
        self._last_download_times = []
        self._last_queue_fill_times = []
        self.variety = None

    def set_variety(self, variety):
        """Set the VarietyWindow instance name.

        This is called after Jumble creates the instance, but before it is actually used.
        :param variety: the instance of VarietyWindow
        """
        self.variety = variety

    def get_variety(self):
        """Return the VarietyWindow instance, if set by set_variety(), or None.

        This is available before the source is actually used.
        :return the instance of VarietyWindow
        """
        return self.variety

    @abc.abstractmethod
    def get_source_type(self):
        """Return key for a source to identify it in configuration files.

        This is saved in image metadata under Xmp.variety.sourceType for later use when determining
        which plugin can handle a particular saved image source configuration, and so should not
        collide between different image source plugins.
        :return: source type, e.g. "flickr", "unsplash", etc.
        """
        pass

    def get_source_name(self):
        """Return value to be set for Xmp.variety.sourceName in image metadata.

        This is also shown in the UI, set to the service that is used to fetch images, e.g. Flickr.
        The default implementation is to return source_type, with an uppercase first letter.
        :return: source name, e.g. "Flickr", "Unsplash", etc.
        """
        source_type = self.get_source_type()
        return source_type[0].upper() + source_type[1:]

    def needs_internet(self):
        """Report whether a configurable image source needs the internet.

        A Boolean value indicating if a source needs a working network link with DNS resolution in
        order to fetch new images.
        :return: True or False
        """
        return True

    def on_image_set_as_wallpaper(self, img, meta):
        """Call for wallpapers downloaded from a particular source.

        This can be used to call back the image provider for stats purposes.
        :param img path to the image file
        :param meta image metadata
        """
        pass

    def on_image_favorited(self, img, meta):
        """Call for images added to Favorites from a particular source.

        This can be used to call back the image provider for stats purposes.
        :param img path to the image file
        :param meta image metadata
        """
        pass

    def get_default_throttling(self):
        """Report the default upper bounds for image fetches per hour.

        Throttling serves to avoid overloading servers when multiple Variety instances use a source
        simultaneously. It is normally controlled via a remote configuration, but defaults should
        be provided for occasions when one is not set or cannot be fetched. All downloaders for the
        same source are throttled together.
        :return: a Throttling namedtuple
        """
        return Throttling(max_downloads_per_hour=None, max_queue_fills_per_hour=None)

    def get_server_options_key(self):
        """Show the key in server-side throttling options containing the configuration for a source.

        By default, it is the same as the source type.
        :return: key in remote server options for this source, e.g. "unsplash_v2"
        """
        return self.get_source_type()

    def get_server_options(self):
        """Return the server options for a source.

        The default implementation reads from get_variety().server_options, i.e. using Variety's
        central server-side options, but this can be overridden to read from elsewhere.
        :return: remotely-configured options for this image source
        """
        return self.get_variety().server_options[self.get_server_options_key()]

    def get_throttling(self):
        """Return the current throttling levels for a source.

        This should take remote configurations into account as well (if available).
        """
        defaults = self.get_default_throttling()

        max_downloads_per_hour, max_queue_fills_per_hour = defaults
        name = self.get_source_name()

        try:
            logger.info(lambda: "{}: parsing serverside options".format(name))
            options = self.get_server_options()
            logger.info(
                lambda: "{} serverside options: {}".format(self.get_source_name(), str(options))
            )
        except Exception:
            logger.info(
                lambda: "Could not parse {} serverside options, using defaults {}, {}".format(
                    name, max_downloads_per_hour, max_queue_fills_per_hour
                )
            )
            return defaults

        try:
            max_downloads_per_hour = int(options["max_downloads_per_hour"])
        except Exception:
            pass

        try:
            max_queue_fills_per_hour = int(options["max_queue_fills_per_hour"])
        except Exception:
            pass

        return Throttling(max_downloads_per_hour, max_queue_fills_per_hour)

    def _count_last_hour_downloads(self):
        now = time.time()
        self._last_download_times = [t for t in self._last_download_times if now - t < 3600]
        return len(self._last_download_times)

    def is_download_allowed(self):
        max_downloads_per_hour, _ = self.get_throttling()
        return (
            max_downloads_per_hour is None
            or self._count_last_hour_downloads() < max_downloads_per_hour
        )

    def register_download(self):
        self._last_download_times.append(time.time())

    def _count_last_hour_queue_fills(self):
        now = time.time()
        self._last_queue_fill_times = [t for t in self._last_queue_fill_times if now - t < 3600]
        return len(self._last_queue_fill_times)

    def is_fill_queue_allowed(self):
        _, max_queue_fills_per_hour = self.get_throttling()
        return (
            max_queue_fills_per_hour is None
            or self._count_last_hour_queue_fills() < max_queue_fills_per_hour
        )

    def register_fill_queue(self):
        self._last_queue_fill_times.append(time.time())
