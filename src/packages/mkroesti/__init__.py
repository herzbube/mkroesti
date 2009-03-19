# encoding=utf-8

# $Id: __init__.py 40 2008-12-02 00:04:32Z patrick $

# Copyright 2008 Patrick Näf
# 
# This file is part of mkroesti
#
# mkroesti is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mkroesti is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mkroesti. If not, see <http://www.gnu.org/licenses/>.


# Feed these modules to clients that say "from mkroesti import *"
__all__ = (["algorithm", "errorhandling", "factory", "main", "names",
            "provider", "registry"])

# The package version; this is used by "mkroesti --version"
version = "0.1"
