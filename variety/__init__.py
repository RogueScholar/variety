# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2017–2025, James Lu <james@overdrivenetworks.com>
# SPDX-FileCopyrightText: © 2018, Brandon Jiang <Brandon.jiang.a@outlook.com>
# SPDX-FileCopyrightText: © 2019, Pedro Romano <pedro@paparomeo.net>
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

import logging
import os
import signal
import sys

import dbus
import dbus.glib
import dbus.service
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk  # pylint: disable=E0611


class SafeLogger(logging.Logger):
    """Fix UnicodeDecodeError occurrences in logging calls.

    Accepts lambda as well string messages, catching errors when evaluating the passed lambda.
    """

    def makeRecord(self, name, level, fn, lno, msg, *args, **kwargs):
        try:
            new_msg = msg if isinstance(msg, str) else msg()
        except:
            locale_info = "Unknown"
            try:
                locale_info = "Terminal encoding=%s, LANG=%s, LANGUAGE=%s" % (
                    sys.stdout.encoding,
                    os.getenv("LANG"),
                    os.getenv("LANGUAGE"),
                )
                logging.getLogger("variety").exception(
                    "Errors while logging. Locale info: %s" % locale_info
                )
                # TODO: Gather and log more info here <PL 2015-01-11>
            except:
                pass
            new_msg = "Errors while logging. Locale info: %s" % locale_info

        return super().makeRecord(name, level, fn, lno, new_msg, *args, **kwargs)


logging.setLoggerClass(SafeLogger)


# These must occur after the setLoggerClass call, as they obtain the Variety logger.
from variety import ThumbsManager, ThumbsWindow, VarietyWindow
from variety.profile import get_profile_id, get_profile_path, is_default_profile, set_profile_path
from variety.Util import ModuleProfiler, Util, _, safe_print


def _get_dbus_key():
    """Set D-Bus key for Variety.

    Variety uses a different D-Bus keys per profile, so several instances can run simultaneously if
    running with different profiles. Commands any instance from the terminal by explicitly passing
    the same --profile options as it was started with.

    :return: the D-Bus key
    """
    if is_default_profile():
        return "com.peterlevi.Variety"
    else:
        return "com.peterlevi.Variety_{}".format(get_profile_id())


DBUS_PATH = "/com/peterlevi/Variety"


class VarietyService(dbus.service.Object):
    def __init__(self, variety_window):
        self.variety_window = variety_window
        bus_name = dbus.service.BusName(_get_dbus_key(), bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, DBUS_PATH)

    @dbus.service.method(dbus_interface=_get_dbus_key(), in_signature="as", out_signature="s")
    def process_command(self, arguments):
        result = self.variety_window.process_command(arguments, initial_run=False)
        return "" if result is None else result


VARIETY_WINDOW = None

terminate = False


def _sigint_handler(*args):
    global terminate
    terminate = True


def _check_quit():
    global terminate
    if not terminate:
        GObject.timeout_add(1000, _check_quit)
        return

    logging.getLogger("variety").info("Terminating signal received, quitting…")
    safe_print(
        _("Terminating signal received, quitting…"),
        "Terminating signal received, quitting…",
        file=sys.stderr,
    )

    global VARIETY_WINDOW
    if VARIETY_WINDOW:
        VARIETY_WINDOW.on_quit()
    Util.start_force_exit_thread(10)


def _set_up_logging(verbose):
    # Add a handler to prevent basicConfig
    root = logging.getLogger()
    null_handler = logging.NullHandler()
    root.addHandler(null_handler)

    formatter = logging.Formatter("%(levelname)s: %(asctime)s: %(funcName)s() '%(message)s'")

    logger = logging.getLogger("variety")
    logger_sh = logging.StreamHandler()
    logger_sh.setFormatter(formatter)
    logger.addHandler(logger_sh)

    try:
        logger_file = logging.FileHandler(os.path.join(get_profile_path(), "variety.log"), "w")
        logger_file.setFormatter(formatter)
        logger.addHandler(logger_file)
    except Exception:
        logger.exception("Could not create log file")

    lib_logger = logging.getLogger("variety_lib")
    lib_logger_sh = logging.StreamHandler()
    lib_logger_sh.setFormatter(formatter)
    lib_logger.addHandler(lib_logger_sh)

    logger.setLevel(logging.INFO)
    # Set the logging level to show debug messages.
    if verbose >= 2:
        logger.setLevel(logging.DEBUG)
    elif not verbose:
        # If we're not in verbose mode only send these messages to the log file, so as not to flood
        # syslog and/or ~/.xsession-errors (depending on how variety was started); see
        # <https://bugs.launchpad.net/variety/+bug/1685003>
        # FIXME: We should /really/ make the internal debug logging use logging.debug, as this is
        # really just a band-aid patch. <PL 2019-07-14>
        logger_sh.setLevel(logging.WARNING)

    if verbose >= 3:
        lib_logger.setLevel(logging.DEBUG)


def main():
    if os.geteuid() == 0:
        print(
            "Variety is not supposed to run as root.\n"
            "You should NEVER run desktop apps as root, unless they are supposed to make system-"
            "wide changes and you know very well what you are doing.\n"
            "Please run it as your normal user instead.\n\n"
            "If you are trying to run as root because Variety does not start at all from your "
            "normal user account, you may be encountering a file permissions issue or a bug.\n"
            "Here is what to do to troubleshoot:\n\n"
            '1. Open a terminal and run "variety -v" with your normal user.\n'
            "Look for exceptions and hints in the log for what the problem might be.\n\n"
            "2. You can try renaming the ~/.config/variety folder to ~/.config/variety_bak.\n"
            "This will start Variety with a clean slate of configuration defaults and keep your "
            "existing settings and images for selective restoration from variety_bak.\n\n"
            "3. If none of these help, create an issue report at "
            "https://github.com/varietywalls/variety/issues/new for assistence."
        )
        sys.exit(1)

    # Ctrl+C
    signal.signal(signal.SIGINT, _sigint_handler)
    signal.signal(signal.SIGTERM, _sigint_handler)
    signal.signal(signal.SIGQUIT, _sigint_handler)

    arguments = sys.argv[1:]

    # Validate arguments
    from variety import VarietyOptionParser

    options, args = VarietyOptionParser.parse_options(arguments)
    set_profile_path(options.profile)
    Util.makedirs(get_profile_path())

    # Ensure singleton per profile
    bus = dbus.SessionBus()
    dbus_key = _get_dbus_key()
    if bus.request_name(dbus_key) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
        if not arguments or (options.profile and len(arguments) <= 2):
            arguments = ["--preferences"]
        safe_print(
            _("Variety is already running; forwarding command to the existing instance."),
            "Variety is already running; forwarding command to the existing instance.",
            file=sys.stderr,
        )
        method = bus.get_object(dbus_key, DBUS_PATH).get_dbus_method("process_command")
        result = method(arguments)
        if result:
            safe_print(result)
        return

    # set_up_logging must be called after the D-Bus checks, by only one running instance, or the
    # log file can be corrupted.
    _set_up_logging(options.verbose)
    logging.getLogger("variety").info(lambda: "Using profile folder {}".format(get_profile_path()))

    if options.verbose >= 3:
        profiler = ModuleProfiler()
        if options.verbose >= 5:
            # The main Variety package
            pkgname = os.path.dirname(__file__)
            profiler.log_path(pkgname)

            if options.verbose >= 6:
                # Track variety_lib
                profiler.log_path(pkgname + "_lib")
        else:
            # Cherry-picked log items carried over from variety v0.6.x
            profiler.log_class(VarietyWindow.VarietyWindow)

            if options.verbose >= 4:
                profiler.log_class(ThumbsManager.ThumbsManager)
                profiler.log_class(ThumbsWindow.ThumbsWindow)

        profiler.start()

    # Run the application.
    window = VarietyWindow.VarietyWindow()
    global VARIETY_WINDOW
    VARIETY_WINDOW = window
    service = VarietyService(window)

    bus.call_on_disconnection(window.on_quit)

    window.start(arguments)
    GObject.timeout_add(2000, _check_quit)
    Gtk.main()
