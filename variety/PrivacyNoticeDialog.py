# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2018–2019, James Lu <james@overdrivenetworks.com>
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

from gi.repository import Gtk  # pylint: disable=E0611

from variety_lib.helpers import get_builder


class PrivacyNoticeDialog(Gtk.Dialog):
    __gtype_name__ = "PrivacyNoticeDialog"

    def __new__(cls):
        """Static method called when constructing a new instance of this class.

        Returns a fully instantiated PrivacyNoticeDialog object.
        """
        builder = get_builder("PrivacyNoticeDialog")
        new_object = builder.get_object("PrivacyNoticeDialog")
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Call made when finished initializing in __new__.

        finish_initalizing should be called after parsing the UI definition and
        creating a PrivacyNoticeDialog object with it to finish initializing
        the start of the new PrivacyNoticeDialog instance.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self)


if __name__ == "__main__":
    dialog = PrivacyNoticeDialog()
    dialog.show()
    Gtk.main()
