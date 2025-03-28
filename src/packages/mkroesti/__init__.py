# encoding=utf-8

# Copyright 2009 Patrick Näf
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


# PSL
import sys

# mkroesti
from mkroesti.registry import ProviderRegistry


# Feed these modules to clients that say "from mkroesti import *"
__all__ = (["algorithm", "errorhandling", "factory", "main", "names",
            "provider", "registry"])


# The package version; this is used by "mkroesti --version"
version = "0.4"
# The project website
url = "http://www.herzbube.ch/mkroesti"


# Set python2 to True or False, depending on which version of the
# interpreter we are running
(major, minor, micro, releaselevel, serial) = sys.version_info
python2 = (major == 2)


def registerProvider(provider):
    """Registers a single provider.
    
    Convenience function for clients that want to remain ignorant of registry details.
    """

    ProviderRegistry.getInstance().addProvider(provider)


def registerProviders(providers):
    """Registers multiple providers.
    
    Convenience function for clients that want to remain ignorant of registry details.
    """

    for provider in providers:
        registerProvider(provider)
