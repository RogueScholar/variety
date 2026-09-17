# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2022, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2025, Peter Occil <poccil14@gmail.com>
# SPDX-FileCopyrightText: © 2026, Diego Alvarez <dp-alvarez@users.noreply.github.com>
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

from typing import List

from variety.plugins.IDisplayModesPlugin import (
    DisplayMode,
    DisplayModeData,
    IDisplayModesPlugin,
    StaticDisplayMode,
)
from variety.Util import Util, _

IMAGEMAGICK_ZOOM = "-scale %Wx%H^ "
IMAGEMAGICK_FIT_WITH_BLACK = "-resize %Wx%H -size %Wx%H xc:black +swap -gravity center -composite"
IMAGEMAGICK_FIT_WITH_BLUR = (
    r"-write mpr:src +delete "
    r"\( mpr:src -resize %Wx%H^ -gravity center -extent %Wx%H -scale 10% -blur 0x3 -resize 1000% \) "
    r"\( mpr:src -resize %Wx%H -background none -gravity center -extent %Wx%H \) "
    r"-composite"
)
IMAGEMAGICK_TILE = "-write mpr:x -delete -1 -size %Wx%H tile:mpr:x "


def _smart_fn(filename):
    try:
        image_w, image_h = Util.get_size(filename)
        primary_w, primary_h = Util.get_primary_display_size(hidpi_scaled=True)
        total_w, total_h = Util.get_multimonitor_display_size()
        if image_w * image_h * 10 < primary_w * primary_h:
            # Image is much smaller than the primary display, so tile it.
            cmd = IMAGEMAGICK_TILE.replace("%W", str(primary_w)).replace("%H", str(primary_h))
            return DisplayModeData(set_wallpaper_param="zoom", imagemagick_cmd=cmd)
        else:
            image_ratio = image_w / image_h
            primary_ratio = primary_w / primary_h
            total_ratio = total_w / total_h
            if 2 * abs(image_ratio - primary_ratio) / (image_ratio + primary_ratio) < 0.2:
                # Image aspect ratio is congruous with primary display, so zoom.
                return DisplayModeData(set_wallpaper_param="zoom")
            elif 2 * abs(image_ratio - total_ratio) / (image_ratio + total_ratio) < 0.2:
                # Image aspect ratio is congruous with multimonitor aggregate layout, so span it.
                return DisplayModeData(set_wallpaper_param="spanned")
            else:
                # Image aspect ratio is incongruous with display, so fit with a blurred background.
                cmd = IMAGEMAGICK_FIT_WITH_BLUR.replace("%W", str(primary_w)).replace(
                    "%H", str(primary_h)
                )
                return DisplayModeData(set_wallpaper_param="zoom", imagemagick_cmd=cmd)
    except:
        return DisplayModeData(set_wallpaper_param="zoom")


class ResizingDisplayModesPlugin(IDisplayModesPlugin):
    @classmethod
    def get_info(cls):
        return {
            "name": "ResizingDisplayModesPlugin",
            "description": "Display modes that use image resizing within Variety",
            "version": "1.0",
            "author": "Peter Levi",
        }

    def display_modes(self) -> List[DisplayMode]:
        return [
            DisplayMode(
                id="smart",
                fn=_smart_fn,
                title=_("Smart: Auto-select mode based on image size (recommended)"),
                description=(
                    "Use the fast, OS-provided zoom mode for images that are close to the display "
                    'proportions, the "Fit & pad with blurred background" mode when the aspect '
                    "ratios differ significantly (i.e. portrait image on a landscape display), or "
                    "tiles the image to fill the display if it is too small to undergo the "
                    "needed resize operation well."
                ),
            ),
            StaticDisplayMode(
                id="zoom",
                set_wallpaper_param="zoom",
                imagemagick_cmd=IMAGEMAGICK_ZOOM,
                title=_("Zoom to fill screen"),
                description=_(
                    "Zoom in or out so that the image fully fills the primary display, though some "
                    'parts of it will be "out of frame" if its aspect ratio differs substantially '
                    "from the display's; slower than using OS-native resize operations."
                ),
            ),
            StaticDisplayMode(
                id="fill-with-black",
                set_wallpaper_param="zoom",
                imagemagick_cmd=IMAGEMAGICK_FIT_WITH_BLACK,
                title=_("Fit to screen (black padding)"),
                description=_(
                    "Zoom in or out so that the image fills as much of the display as possible "
                    "without any cropping, while the rest of the desktop is filled with black; "
                    "slower than using OS-native resize operations."
                ),
            ),
            StaticDisplayMode(
                id="fill-with-blur",
                set_wallpaper_param="zoom",
                imagemagick_cmd=IMAGEMAGICK_FIT_WITH_BLUR,
                title=_("Fit to screen, (blurred padding, slower)"),
                description=_(
                    "Zoom in or out so that the image fills as much of the display as possible "
                    "without any cropping, while the rest of the desktop is filled with a blurred "
                    "version of the image."
                ),
            ),
        ]

    def order(self):
        return 2000
