# -*- coding: utf-8 -*-
# Copyright © tandemdude 2020-present
#
# This file is part of Lightbulb.
#
# Lightbulb is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lightbulb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Lightbulb. If not, see <https://www.gnu.org/licenses/>.
__all__ = ["LightbulbError", "CheckFailure", "CommandNotFound"]

import typing as t


class LightbulbError(Exception):
    pass


class CheckFailure(LightbulbError):
    pass


class CommandNotFound(LightbulbError):
    def __init__(self, *args: t.Any, invoked_with: str):
        super().__init__(*args)
        self.invoked_with = invoked_with
