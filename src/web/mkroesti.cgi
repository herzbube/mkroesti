#!/usr/bin/env python
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


# Compatibility Python 2.6
from __future__ import print_function

# PSL
import cgi
import math
# Enable this line only for debugging purposes
import cgitb; cgitb.enable()

# mkroesti
import mkroesti   # import stuff from __init__.py (e.g. mkroesti.version)
from mkroesti import factory
from mkroesti import main
from mkroesti import registry


# Prints out algorithm or alias names in HTML table format. Each table cell
# is filled with a checkbox and a label. 
# - tableData: list of names to print
# - columnCount: generate a table with this many columns
# - form: a reference to the form data (instance of cgi.FieldStorage()); if
#   one of the names in tableData appears as a key in the form data, the name's
#   checkbox is initially checked
def printTable(tableData, columnCount, form):
    cellCount = len(tableData)
    # math.ceil() gives us a float, but we need an int for later calculations
    rowCount = int(math.ceil(cellCount / columnCount))
    print('<table cellspacing="5">')
    iterRow = 0
    while iterRow < rowCount:
        print('<tr>')
        iterColumn = 0
        iterCell = iterRow
        while iterColumn < columnCount and iterCell < cellCount:
            itemName = tableData[iterCell]
            if form.getfirst(itemName, None) is None:
                checked = ""
            else:
                checked = "checked"
            print('<td><input type="checkbox" name="' + itemName + '" ' + checked + '/>' + itemName + '</td>')
            iterColumn += 1
            iterCell += rowCount
        print('</tr>')
        iterRow += 1
    print('</table>')

# ------------------------------------------------------------
# Setup phase
# ------------------------------------------------------------

# Get the form data. The first time this CGI script is invoked there is no
# form data.
form = cgi.FieldStorage()

# Evaluate whether or not the caller has provided us with some input. If so, we
# are later going to generate hashes for the input. We have two input fields:
# One is a regular text entry field, the other is a password entry field where
# the entered text is obscured. The input may come from either of the two
# fields; if for some strange reason both fields contain something, the input
# is taken from the regular text entry field.
hashInput = form.getfirst("hashInput", None)
if hashInput is None or hashInput == "":
    hashInput = form.getfirst("hashInputPassword", None)
    if hashInput is None or hashInput == "":
        hashMode = False
    else:
        hashMode = True
else:
    hashMode = True

# Set up mkroesti
providerModuleNames = ["mkroesti.provider"]
main.registerProviders(providerModuleNames)
availableAlgorithmNames = registry.ProviderRegistry.getInstance().getAvailableAlgorithmNames()
aliasNames = registry.ProviderRegistry.getInstance().getAliasNames()

# Define constants
nrOfColumnsInAlgorithmAndAliasTables = 5

# ------------------------------------------------------------
# Output phase
# ------------------------------------------------------------

# Print HTTP headers
# Note: By specifying the UTF-8 encoding, we try to neatly circumvent all
# encoding problems.
print('Content-Type: text/html;charset=utf-8')
print('')

# Print beginning-of-document (including beginning-of-form)
print('<html>')
print('<head><title>mkroesti ' + str(mkroesti.version) + '</title></head>')
print('<body>')
print('<form action="mkroesti.cgi" method="post">')

# Print available algorithms and aliases
print('<p>Select one or more algorithms:</p>')
printTable(sorted(availableAlgorithmNames), nrOfColumnsInAlgorithmAndAliasTables, form)
print('<hr/>')
print('<p>Select one or more aliases:</p>')
printTable(sorted(aliasNames), nrOfColumnsInAlgorithmAndAliasTables, form)
print('<hr/>')

# Print data entry part (including end-of-form)
print('<p>Enter the string to hash:</p>')
print('<table cellspacing="5">')
print('<tr>')
print('<td>Hash input:</td> <td><input type="text" name="hashInput" size="40"/></td>')
print('</tr>')
print('<tr>')
print('<td>Hash input (password):</td> <td><input type="password" name="hashInputPassword" size="40"/></td>')
print('</tr>')
print('<tr>')
print('<td></td> <td><input type="submit"/><input type="reset"/></td>')
print('</tr>')
print('</table>')
print('<p>Notes:<ul>')
print('<li>Use either of the two text entry fields, but not both (if you do, the password field will be ignored).</li>')
print('<li>The password field can be used to prevent the input from being displayed in clear text on your monitor.</li>')
print('<li><em>Even if you use the password field, the text you type will be transmitted over the network in clear text! Transmission can be made safe by using a secure/encrypted connection (i.e. https), but even then the text will still be visible in clear text on the server side and might show up somewhere in a logfile. <strong>Please do not type in a valuable password!</strong></em></li>')
print('<li>The hash input is expected to be in UTF-8 character encoding. If you change the encoding the resulting hash might be incorrect.</li>')
print('</ul></p>')
print('</form>')

# If hashing is requested, generate and print hashes
if hashMode:
    print('<hr/>')
    print('<p>Hash results:</p>')
    # Fill nameLists with lists of requested algorithm names; names may appear
    # multiple names because of aliases; also because of aliases, algorithms
    # may appear that are actually unavailable
    reg = registry.ProviderRegistry.getInstance()
    nameLists = [[name for name in availableAlgorithmNames if form.getfirst(name, None) is not None]]
    nameLists.extend([reg.resolveAlias(name) for name in aliasNames if form.getfirst(name, None) is not None])
    # Clear duplicates and algorithms that are unavailable
    hashAlgorithmNames = list()
    for nameList in nameLists:
        for name in nameList:
            if name not in hashAlgorithmNames and reg.isAlgorithmAvailable(name):
                hashAlgorithmNames.append(name)
    # Create algorithm objects
    hashAlgorithms = list()
    for name in hashAlgorithmNames:
        hashAlgorithms.extend(factory.AlgorithmFactory.createAlgorithms(name))
    # Generate hashes
    hashDict = dict()
    for algorithm in hashAlgorithms:
        # Conversion to bytes() is done only if the algorithm requires it, and
        # if we are running with a Python version that has the bytes() type
        if algorithm.needBytesInput() and not mkroesti.python2:
            # In the HTTP headers we said that the document is UTF-8 encoded,
            # therefore it should be OK if we use that encoding here for
            # converting to bytes
            hashDict[algorithm.getName()] = algorithm.getHash(bytes(hashInput, "utf-8"))
        else:
            hashDict[algorithm.getName()] = algorithm.getHash(hashInput)
    sortedResults = [(name, hashDict[name]) for name in sorted(hashAlgorithmNames)]
    print('<table cellspacing="5">')
    for name, hash in sortedResults:
        print('<tr>')
        print('<td>' + name + ':</td> <td>' + str(hash) + '</td>')
        print('</tr>')
    print('</table>')

# Print end-of-document
print('</body>')
print('</html>')
