# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2017–2018, James Lu <james@overdrivenetworks.com>
# SPDX-FileCopyrightText: © 2018, Brandon Jiang <Brandon.jiang.a@outlook.com>
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

"""Provide helpers for application instances in Ubuntu environments."""

import logging
import os

from .Builder import Builder
from .varietyconfig import get_data_file


def get_builder(builder_file_name):
    """Return a fully-instantiated Gtk.Builder instance from specified UI file.

    :param builder_file_name: The name of the builder file, without extension;
                              assumed to be in 'ui' directory under data path.
    """
    # Look for the UI file that describes the user interface.
    ui_filename = get_data_file("ui", "%s.ui" % (builder_file_name,))
    if not os.path.exists(ui_filename):
        ui_filename = None

    builder = Builder()
    builder.set_translation_domain("variety")
    builder.add_from_file(ui_filename)
    return builder


# Owais Lone : To get quick access to icons and stuff.
def get_media_file(media_file_name):
    media_filename = get_data_file("media", "%s" % (media_file_name,))
    if not os.path.exists(media_filename):
        media_filename = None

    return "file:///" + media_filename


def get_help_uri(page=None):
    # help_uri from source tree - language-agnostic using C locale
    here = os.path.dirname(__file__)
    help_uri = os.path.abspath(os.path.join(here, "..", "help", "C"))

    if not os.path.exists(help_uri):
        # Installed in system path, so use GNOME help tree with user's locale.
        help_uri = "variety"

    # If the page is unspecified, use index.page.
    if page is not None:
        help_uri = "%s#%s" % (help_uri, page)

    return help_uri


def show_uri(parent, link):
    from gi.repository import Gtk  # pylint: disable=E0611

    screen = parent.get_screen()
    Gtk.show_uri(screen, link, Gtk.get_current_event_time())


def alias(alternative_function_name):
    """See <http://www.drdobbs.com/web-development/184406073#l9>."""

    def decorator(function):
        """Attach alternative_function_name(s) to a function."""
        if not hasattr(function, "aliases"):
            function.aliases = []
        function.aliases.append(alternative_function_name)
        return function

    return decorator
