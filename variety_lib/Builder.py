# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2018, Brandon Jiang <Brandon.jiang.a@outlook.com>
# SPDX-FileCopyrightText: © 2018, James Lu <james@overdrivenetworks.com>
# SPDX-FileCopyrightText: © 2020, Terni <LIE3APb@users.noreply.github.com>
# SPDX-FileCopyrightText: © 2020, Karthikeyan Singaravelan <tir.karthi@gmail.com>
# SPDX-FileCopyrightText: © 2026, Peter J. Mello <admin@petermello.net>
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

"""Enhance builder connections by providing objects to access Glade objects."""

import functools
import inspect
import logging
from xml.etree.cElementTree import ElementTree

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GObject, Gtk  # pylint: disable=E0611

logger = logging.getLogger("variety_lib")


# This module is big, so it uses some conventional pre- and postfixes:
# *s     = list (except self.widgets is a dictionary)
# *_dict = dictionary
# *name  = string
# ele_*  = element (in an ElementTree)


# pylint: disable=R0904
# The plentiful public methods are a feature of Gtk.Builder.
class Builder(Gtk.Builder):
    """A bevy of extra helper features.

    * Connects a Glade-defined handler to default_handler, if necessary.
    * Auto-connects a widget to the handler with a matching name or alias.
    * Auto-connects several widgets to their handler via multiple aliases.
    * Allow handlers to lookup widget names.
    * Logs every connection made, and any on_* that is not made.
    """

    def __init__(self):
        Gtk.Builder.__init__(self)
        self.widgets = {}
        self.glade_handler_dict = {}
        self.connections = []
        self._reverse_widget_dict = {}

    # pylint: disable=R0201
    # This is a method for subclasses of Builder to redefine as-needed.
    def default_handler(self, handler_name, filename, *args, **kwargs):
        """Help the apprentice guru.

        Glade-defined handlers that do not exist come here instead. An
        apprentice guru might wonder which signal does what it wants, and here
        it can define any likely candidates in Glade and notice which ones get
        triggered when it plays with the project. This method does not appear
        in Gtk.Builder
        """
        logger.debug(
            """tried to call non-existent function:%s()
            expected in %s
            args:%s
            kwargs:%s""",
            handler_name,
            filename,
            args,
            kwargs,
        )

    # pylint: enable=R0201

    def get_name(self, widget):
        """Allow a handler to get the name (id) of a widget.

        This method does not appear in Gtk.Builder.
        """
        return self._reverse_widget_dict.get(widget)

    def add_from_file(self, filename):
        """Parse an XML file and store the needed details."""
        Gtk.Builder.add_from_file(self, filename)

        # Extract data for the extra interfaces.
        tree = ElementTree()
        tree.parse(filename)

        ele_widgets = tree.iter("object")
        for ele_widget in ele_widgets:
            name = ele_widget.attrib.get("id")
            if not name:
                continue

            widget = self.get_object(name)

            # Populate indexes with a dictionary of widgets.
            self.widgets[name] = widget

            # Populate a reversed dictionary
            self._reverse_widget_dict[widget] = name

            # Populate connections list
            ele_signals = ele_widget.findall("signal")

            connections = [
                (name, ele_signal.attrib["name"], ele_signal.attrib["handler"])
                for ele_signal in ele_signals
            ]

            if connections:
                self.connections.extend(connections)

        ele_signals = tree.iter("signal")
        for ele_signal in ele_signals:
            self.glade_handler_dict.update({ele_signal.attrib["handler"]: None})

    def connect_signals(self, callback_obj):
        """Connect the handlers defined in Glade.

        This logs successful connections and failed calls to missing handlers.
        """
        filename = inspect.getfile(callback_obj.__class__)
        callback_handler_dict = dict_from_callback_obj(callback_obj)
        connection_dict = {}
        connection_dict.update(self.glade_handler_dict)
        connection_dict.update(callback_handler_dict)
        for item in connection_dict.items():
            if item[1] is None:
                # The handler is missing, so reroute to default_handler.
                handler = functools.partial(self.default_handler, item[0], filename)

                connection_dict[item[0]] = handler

                # Replace the runtime warning
                logger.warn("expected handler '%s' in %s", item[0], filename)

        # Connect Glade-defined handlers
        Gtk.Builder.connect_signals(self, connection_dict)

        # Tell the user how the Glade design was applied.
        for connection in self.connections:
            widget_name, signal_name, handler_name = connection
            logger.debug(
                "connect builder by design '%s', '%s', '%s'", widget_name, signal_name, handler_name
            )

    def get_ui(self, callback_obj=None, by_name=True):
        """Create a UI object with widgets as attributes.

        Connects signals by two methods; this does not appear in Gtk.Builder.
        """

        result = UiFactory(self.widgets)

        # Hook into any signals the user defined in Glade.
        if callback_obj is not None:
            # Connect the Glade-defined handlers
            self.connect_signals(callback_obj)

            if by_name:
                auto_connect_by_name(callback_obj, self)

        return result


# pylint: disable=R0903
# This class deliberately does not provide any public interfaces, apart from
# the Glade widgets.
class UiFactory:
    """Provide an object with attributes as Glade widgets."""

    def __init__(self, widget_dict):
        self._widget_dict = widget_dict
        for widget_name, widget in widget_dict.items():
            setattr(self, widget_name, widget)

        # Mangle unusable names (e.g., with spaces/dashes) into Pythonic ones.
        cannot_message = """Cannot bind ui.%s, name already exists.
        Consider using a Pythonic name instead of the design name '%s'."""
        consider_message = """Consider using a Pythonic name instead of the design name '%s'."""

        for widget_name, widget in widget_dict.items():
            pyname = make_pyname(widget_name)
            if pyname != widget_name:
                if hasattr(self, pyname):
                    logger.debug(cannot_message, pyname, widget_name)
                else:
                    logger.debug(consider_message, widget_name)
                    setattr(self, pyname, widget)

    def __iter__(self):
        """Implement iterables, such as 'for o in self'."""
        return self._widget_dict.values()

    def __getitem__(self, name):
        """Provide dictionary access for names that might be non-Pythonic."""
        return self._widget_dict[name]


# pylint: enable=R0903


def make_pyname(name):
    """Mangle non-Pythonic names into Pythonic ones."""
    pyname = ""
    for character in name:
        if character.isalpha() or character == "_" or (pyname and character.isdigit()):
            pyname += character
        else:
            pyname += "_"
    return pyname


# We need to reimplement inspect.getmembers until GNOME bug #652127 is fixed,
# since GObject introspection doesn't play nice with it.
# <https://bugzilla.gnome.org/show_bug.cgi?id=652127>
def getmembers(obj, check):
    members = []
    for k in dir(obj):
        try:
            attr = getattr(obj, k)
        except:
            continue
        if check(attr):
            members.append((k, attr))
    members.sort()
    return members


def dict_from_callback_obj(callback_obj):
    """Provide a dictionary interface to callback_obj."""
    methods = getmembers(callback_obj, inspect.ismethod)

    aliased_methods = [x[1] for x in methods if hasattr(x[1], "aliases")]

    # A method may have several aliases, for example:
    # ~ @alias('on_btn_foo_clicked')
    # ~ @alias('on_tool_foo_activate')
    # ~ on_menu_foo_activate():
    # ~ pass
    alias_groups = [(x.aliases, x) for x in aliased_methods]

    aliases = []
    for item in alias_groups:
        for alias in item[0]:
            aliases.append((alias, item[1]))

    dict_methods = dict(methods)
    dict_aliases = dict(aliases)

    results = {}
    results.update(dict_methods)
    results.update(dict_aliases)

    return results


def auto_connect_by_name(callback_obj, builder):
    """Find handlers like on_<widget_name>_<signal> and connect them.

    Takes the widget:signal pair in a builder and calls
    widget.connect(signal, on_<widget_name>_<signal>).
    """

    callback_handler_dict = dict_from_callback_obj(callback_obj)

    for item in builder.widgets.items():
        widget_name, widget = item
        signal_ids = []
        try:
            widget_type = type(widget)
            while widget_type:
                signal_ids.extend(GObject.signal_list_ids(widget_type))
                widget_type = GObject.type_parent(widget_type)
        except RuntimeError:  # Since Pylint wants a specific error…
            pass
        signal_names = [GObject.signal_name(sid) for sid in signal_ids]

        # Now, automatically find any signals the user didn't specify in Glade…
        for sig in signal_names:
            # …using the convention suggested by Glade.
            sig = sig.replace("-", "_")
            handler_names = ["on_%s_%s" % (widget_name, sig)]

            # Using the convention that the top-level window is not specified
            # in the handler name. That is, use on_destroy() instead of
            # on_windowname_destroy().
            if widget is callback_obj:
                handler_names.append("on_%s" % sig)

            do_connect(item, sig, handler_names, callback_handler_dict, builder.connections)

    log_unconnected_functions(callback_handler_dict, builder.connections)


def do_connect(item, signal_name, handler_names, callback_handler_dict, connections):
    """Connect this signal to an unused handler."""
    widget_name, widget = item

    for handler_name in handler_names:
        target = handler_name in list(callback_handler_dict.keys())
        connection = (widget_name, signal_name, handler_name)
        duplicate = connection in connections
        if target and not duplicate:
            widget.connect(signal_name, callback_handler_dict[handler_name])
            connections.append(connection)

            logger.debug(
                "Connect builder by name '%s', '%s', '%s'", widget_name, signal_name, handler_name
            )


def log_unconnected_functions(callback_handler_dict, connections):
    """Log functions like on_* that couldn't be connected."""

    connected_functions = [x[2] for x in connections]

    handler_names = list(callback_handler_dict.keys())
    unconnected = [x for x in handler_names if x.startswith("on_")]

    for handler_name in connected_functions:
        try:
            unconnected.remove(handler_name)
        except ValueError:
            pass

    for handler_name in unconnected:
        logger.debug("Not connected to builder '%s'", handler_name)
