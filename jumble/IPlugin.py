# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2013–2019, Peter Levi <peterlevi@peterlevi.com>
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


class IPlugin(object, metaclass=abc.ABCMeta):
    """The most simple interface to be inherited when creating a plugin."""

    @classmethod
    @abc.abstractmethod
    def get_info(cls):
        """Return basic information about a plugin.

        Please make sure that the name is unique among all Variety plugins.
        Format:
        return {
           "name": "Sample name",
           "description": "Sample description",
           "version": "1.0",
           "author": "Author name", # optional
           "url": "Plugin homepage URL"  # optional
        }
        """
        pass

    def __init__(self):
        """A default plugin constructor with no parameters.

        Remember to call super with this.
        """
        self.active = False

        # These are filled in by Jumble.load() and made available before the first activate() call.
        self.jumble = None
        self.path = None  # Path to a plugin's Python source file
        self.folder = (
            None  # The folder where plugin is located (can be used for loading UI resources, etc.)
        )
        # Folder may be read-only and require using another config folder convention for storage.

    def activate(self):
        """Activation called for a plugin.

        Please do not allocate large amounts of memory or other resources before this is called,
        and remember to call super first. This method can be called multiple times per session,
        even when a plugin is already active - in which case it should return silently.
        """
        if self.active:
            return
        self.active = True

    def deactivate(self):
        """Deactivation call for a plugin, leaving it disabled.

        Please free its used memory and resources here, remembering to call super first. This can
        be called multiple times per session, including when a plugin is already disabled - in
        which case it should return silently.
        """
        self.active = False

    def is_active(self):
        return self.active
