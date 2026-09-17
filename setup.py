#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# SPDX-FileCopyrightText: © 2012–2019, Peter Levi <peterlevi@peterlevi.com>
# SPDX-FileCopyrightText: © 2017–2025, James Lu <james@overdrivenetworks.com>
# SPDX-FileCopyrightText: © 2018, Brandon Jiang <Brandon.jiang.a@outlook.com>
# SPDX-FileCopyrightText: © 2025, Martin Gansser <martinkg@fedoraproject.org>
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

from setuptools import find_packages, setup

setup(
    packages=find_packages(exclude=["tests"]),
    long_description="""
Variety is a wallpaper manager for Linux systems. It supports numerous desktops
and wallpaper sources, including local files and online services:
Wallhaven, Unsplash, and more.

Where supported, Variety sits as a tray icon to allow easy pausing and resuming.
Otherwise, its desktop entry menu provides a similar set of options.

Variety also includes a range of image effects, such as oil painting and blur,
as well as options to layer quotes and a clock onto the background.""",
    # FIXME: data_files is deprecated <JL 2025-10-13>
    data_files=[
        ("share/applications", ["com.peterlevi.Variety.desktop"]),
        ("share/dbus-1/services", ["com.peterlevi.Variety.service"]),
        ("share/metainfo", ["com.peterlevi.Variety.metainfo.xml"]),
    ],
    package_data={
        "variety": ["data/**", "locale/**"],
    },
    include_package_data=True,
)
