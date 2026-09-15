# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2020, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2026, James Lu <james@overdrivenetworks.com>
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

import optparse

from variety.Util import _, safe_print
from variety_lib import varietyconfig


class VarietyOptionParser(optparse.OptionParser):
    """Override OptionParser to allow for errors in options without exiting."""

    def __init__(self, usage, version, report_errors=True):
        optparse.OptionParser.__init__(self, usage=usage, version=version)
        self.report_errors = report_errors

    def print_help(self, file=None):
        """Print an extended help message to 'file' (default stdout).

        List all options and any help text provided with them.
        """
        if file is None:
            safe_print(self.format_help())
        else:
            file.write(self.format_help().encode())

    def error(self, msg):
        if self.report_errors:
            optparse.OptionParser.error(self, msg)
        else:
            raise ValueError(msg)


def parse_options(arguments, report_errors=True):
    """Define supported command line options."""
    usage = _(
        """%prog [options] [files or URLs]

        Passing local files will add them to Variety's queue, while remote URLs
        will be populated to the Fetched folder and placed in the queue.
        To set a specific wallpaper: %prog --set /path/to/image.jpg
        """
    )

    parser = VarietyOptionParser(
        version="%%prog %s" % varietyconfig.get_version(),
        usage=usage,
        report_errors=report_errors
    )

    parser.add_option(
        "--profile",
        action="store",
        dest="profile",
        default=None,
        help=_(
            "Profile name or full path to the configuration folder Variety should use; falling "
            'back to "${HOME}/.config/variety" if not defined. If just a name is used instead of '
            "a full path, the configuration folder will instead be set to "
            '"${HOME}/.config/variety-profiles/<name>". Use only when initially launching Variety '
            "as changing the profile path requires the process to restart. Several instances of "
            "Variety can operate simultaneously when using different profiles, each with its own "
            "separate configuration. This can be used, for example, to independently manage "
            "multiple screens or workspaces under desktop environments which allow this, like "
            "XFCE. To pass commands to a running instance, pass the same --profile argument in "
            "subsequent commands as the one it was started with."
        )
    )

    parser.add_option(
        "-v",
        "--verbose",
        action="count",
        dest="verbose",
        default=0,
        help=_(
            "Show logging messages with a variable level of specificity; flag may be repeated up "
            "to four additional times, each increasing the amount of detail reported."
        )
    )

    parser.add_option(
        "-q",
        "--quit",
        action="store_true",
        dest="quit",
        help=_("Quit the running instance.")
    )

    parser.add_option(
        "--get",
        "--get-wallpaper",
        "--current",
        "--show-current",
        action="store_true",
        dest="show_current",
        help=_("Print the current wallpaper filename and path from a running instance of Variety.")
    )

    parser.add_option(
        "--meta",
        action="store_true",
        dest="show_meta",
        help=_("Print the current wallpaper metadata from a running instance of Variety.")
    )

    parser.add_option(
        "--set",
        "--set-wallpaper",
        action="store",
        dest="set_wallpaper",
        help=_("Set the given file as wallpaper; requires an absolute path as the value.")
    )

    parser.add_option(
        "-n",
        "--next",
        action="store_true",
        dest="next",
        help=_("Skip to the next wallpaper in the queue.")
    )

    parser.add_option(
        "-p",
        "--previous",
        action="store_true",
        dest="previous",
        help=_("Return to the most recent previous wallpaper from the queue.")
    )

    parser.add_option(
        "--fast-forward",
        action="store_true",
        dest="fast_forward",
        help=_(
            "Skip ahead to the first unused wallpaper in the queue, bypassing the forward history."
        )
    )

    parser.add_option(
        "-t",
        "--trash",
        action="store_true",
        dest="trash",
        help=_("Move the current wallpaper to the Trash; image must have been set by Variety.")
    )

    parser.add_option(
        "-f",
        "--favorite",
        action="store_true",
        dest="favorite",
        help=_("Copy the current wallpaper to Favorites; image must have been set by Variety.")
    )

    parser.add_option(
        "--move-to-favorites",
        action="store_true",
        dest="movefavorite",
        help=_("Move the current wallpaper to Favorites; image must have been set by Variety.")
    )

    parser.add_option(
        "--pause",
        action="store_true",
        dest="pause",
        help=_("Pause further wallpaper changes and remain on current image.")
    )

    parser.add_option(
        "--resume",
        action="store_true",
        dest="resume",
        help=_("Resume configured wallpaper change schedule.")
    )

    parser.add_option(
        "--toggle-pause",
        action="store_true",
        dest="toggle_pause",
        help=_("Reverse the current pause state of wallpaper changes.")
    )

    parser.add_option(
        "--toggle-no-effects",
        action="store_true",
        dest="toggle_no_effects",
        help=_("Reverse the current image effects state for the current wallpaper.")
    )

    parser.add_option(
        "--quotes-next",
        action="store_true",
        dest="quotes_next",
        help=_("Skip to the next quote in the queue.")
    )

    parser.add_option(
        "--quotes-previous",
        action="store_true",
        dest="quotes_previous",
        help=_("Return to the most recent previous quote from the queue.")
    )

    parser.add_option(
        "--quotes-fast-forward",
        action="store_true",
        dest="quotes_fast_forward",
        help=_("Skip ahead to the first unused quote in the queue, bypassing the forward history.")
    )

    parser.add_option(
        "--quotes-toggle-pause",
        action="store_true",
        dest="quotes_toggle_pause",
        help=_("Reverse the activation state for showing quotes on the desktop.")
    )

    parser.add_option(
        "--quotes-save-favorite",
        action="store_true",
        dest="quotes_save_favorite",
        help=_("Save the current quote to Favorites.")
    )

    parser.add_option(
        "--history",
        action="store_true",
        dest="history",
        help=_("Show/Hide the wallpaper history ribbon.")
    )

    parser.add_option(
        "--downloads",
        action="store_true",
        dest="downloads",
        help=_("Show/Hide the recent downloads ribbon.")
    )

    parser.add_option(
        "--preferences",
        "--show-preferences",
        action="store_true",
        dest="preferences",
        help=_("Open the Variety configuration panel.")
    )

    parser.add_option(
        "--selector",
        "--show-selector",
        action="store_true",
        dest="selector",
        help=_(
            "Show the manual selection ribbon with thumbnails of all images from the active "
            "sources."
        )
    )

    parser.add_option(
        "--set-option",
        action="append",
        dest="set_options",
        nargs=2,
        help=_(
            "Assign a value to the specified Variety configuration option; the name must match "
            "a valid entry for Variety's configuration file, found at "
            '"${HOME}/.config/variety/variety.conf". This flag may be repeated to cpnfigure '
            "multiple options in a single command, for example: "
            "'variety --set-option icon Dark --set-option clock_enabled True'. USE WITH CAUTION: "
            "Configuration options can be assigned invalid values when using this flag."
        )
    )

    options, args = parser.parse_args(arguments)

    if report_errors:
        if (options.next or options.fast_forward) and options.previous:
            parser.error(_(
                "The --next, --fast-forward and --previous flags are mutually exclusive."
            ))

        if options.trash and options.favorite:
            parser.error(_("The --trash and --favorite flags are mutually exclusive."))

        if options.pause and options.resume:
            parser.error(_("The --pause and --resume flags are mutually exclusive."))

        if (options.quotes_next or options.quotes_fast_forward) and options.quotes_previous:
            parser.error(_(
                "The --quotes-next, --quotes-fast-forward and --quotes-previous flags are "
                "mutually exclusive."
            ))

    return options, args
