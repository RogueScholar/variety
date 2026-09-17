# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2018, James Lu <james@overdrivenetworks.com>
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


class EditFavoriteOperationsDialog(Gtk.Dialog):
    __gtype_name__ = "EditFavoriteOperationsDialog"

    def __new__(cls):
        """Static method called when constructing a new instance of this class.

        Returns a fully instantiated EditFavoriteOperationsDialog object.
        """
        builder = get_builder("EditFavoriteOperationsDialog")
        new_object = builder.get_object("edit_favorite_operations_dialog")
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Call to finish initializing in __new__.

        finish_initalizing should be called after parsing the UI definition and
        creating a EditFavoriteOperationsDialog object from it to finish
        initializing the start of the new EditFavoriteOperationsDialog instance.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self)

    def on_btn_ok_clicked(self, widget, data=None):
        """Save the changes the user has finalized.

        This is called before the dialog returns Gtk.ResponseType.OK from run().
        """
        pass

    def on_btn_cancel_clicked(self, widget, data=None):
        """Forget the changes the user has elected to cancel.

        This is called before the dialog returns Gtk.ResponseType.CANCEL for run().
        """
        pass

    def on_reset_clicked(self, widget):
        self.ui.textbuffer.set_text("Downloaded:Copy\nFetched:Move\nOthers:Copy")
        return True


if __name__ == "__main__":
    dialog = EditFavoriteOperationsDialog()
    dialog.show()
    Gtk.main()
