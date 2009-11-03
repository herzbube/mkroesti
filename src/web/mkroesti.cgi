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
import os
import sys
import codecs
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
    # Note 1: Multiplying by 1.0 forces Python 2.6 to do a floating point
    # division; if we don't do this, Python 2.6 will truncate the result to an
    # integer before math.ceil() has had a chance to do something. Another
    # variant would be to say: from future import division
    # Note 2: math.ceil() gives us a float, but we need an int for later
    # calculations
    rowCount = int(math.ceil(cellCount * 1.0 / columnCount))
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

# Define constants
nrOfColumnsInAlgorithmAndAliasTables = 5
formName = "theForm"
fieldNameHashInput = "hashInput"
fieldNameHashInputPassword = "hashInputPassword"

# Get the name that this CGI script has been executed as
scriptName = os.path.basename(os.environ["SCRIPT_NAME"])

# Get the form data. The first time this CGI script is invoked there is no
# form data.
form = cgi.FieldStorage()

# Evaluate whether or not the caller has provided us with some input. If so, we
# are later going to generate hashes for the input. We have two input fields:
# One is a regular text entry field, the other is a password entry field where
# the entered text is obscured. The input may come from either of the two
# fields; if for some strange reason both fields contain something, the input
# is taken from the regular text entry field.
hashInput = form.getfirst(fieldNameHashInput, None)
hashInputPassword = form.getfirst(fieldNameHashInputPassword, None)
mkroestiInput = None
if hashInput is None or hashInput == "":
    if hashInputPassword is None or hashInputPassword == "":
        pass
    else:
        mkroestiInput = hashInputPassword
else:
    mkroestiInput = hashInput

# Set up mkroesti
providerModuleNames = ["mkroesti.provider"]
main.registerProviders(providerModuleNames)
availableAlgorithmNames = registry.ProviderRegistry.getInstance().getAvailableAlgorithmNames()
availableAliasNames = registry.ProviderRegistry.getInstance().getAvailableAliasNames()

# If we got input values we are going to provide them as default values for the
# next invocation of the script
if hashInput is None:
    defaultHashInput = ''
else:
    defaultHashInput = 'value = "%s"' % hashInput
if hashInputPassword is None:
    defaultHashInputPassword = ''
else:
    defaultHashInputPassword = 'value = "%s"' % hashInputPassword

# ------------------------------------------------------------
# Hash generation phase
# ------------------------------------------------------------

sortedResults = None
errorResults = None
if mkroestiInput is not None:
    try:
        # Fill nameLists with lists of requested algorithm names; names may appear
        # multiple names because of aliases; also because of aliases, algorithms
        # may appear that are actually unavailable
        reg = registry.ProviderRegistry.getInstance()
        nameLists = [[name for name in availableAlgorithmNames if form.getfirst(name, None) is not None]]
        nameLists.extend([reg.resolveAlias(name) for name in availableAliasNames if form.getfirst(name, None) is not None])
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
            algorithmName = algorithm.getName()
            hashValue = None
            try:
                # Conversion to bytes() is done only if the algorithm requires it, and
                # if we are running with a Python version that has the bytes() type
                if algorithm.needBytesInput() and not mkroesti.python2:
                    # In the HTTP headers we said that the document is UTF-8 encoded,
                    # therefore it should be OK if we use that encoding here for
                    # converting to bytes
                    hashValue = algorithm.getHash(bytes(mkroestiInput, "utf-8"))
                else:
                    hashValue = algorithm.getHash(mkroestiInput)
            except:
                (exc_type, exc_value, exc_traceback) = sys.exc_info()
                hashValue = ('<span style="color:red">%s: %s</span>' % (str(exc_type.__name__), str(exc_value)))
            hashDict[algorithmName] = hashValue
        sortedResults = [(name, hashDict[name]) for name in sorted(hashAlgorithmNames)]
    except:
        errorResults = sys.exc_info()

# ------------------------------------------------------------
# Output phase
#
# Page layout:
#
#   +-column-1-------------+     +-column-2-------------+
#   |  +-input----------+  |     |  +-algorithms-----+  |
#   |  |                |  |     |  |                |  |
#   |  +-----------------  |     |  +-----------------  |
#   +----------------------+     |                      |
#                                |  +-aliases--------+  |
#                                |  |                |  |
#                                |  +-----------------  |
#                                |                      |
#                                +----------------------+
#
#   +-footer--------------------------------------------+
#   |  +-output / output-error-----------------------+  |
#   |  |                                             |  |
#   |  +---------------------------------------------+  |
#   +---------------------------------------------------+
#
# ------------------------------------------------------------

# Replace normal stdout with an UTF-8 enabled version. If we don't do this and
# then try to output non-ASCII characters (e.g. the user's input from a previous
# invocation of this CGI script), a UnicodeEncodeError will be raised.
# Note: I have seen this error being raised only under Python 3, but many
# people seem to have encountered the problem also under 2.6
# Credits: Solution found here:
# http://stackoverflow.com/questions/984014/python-3-is-using-sys-stdout-buffer-write-good-style
if not mkroesti.python2:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# Print HTTP headers
# Note: By specifying the UTF-8 encoding, we try to neatly circumvent all
# encoding problems.
print('Content-Type: text/html;charset=utf-8')
print('')

# Print beginning-of-document (including CSS and beginning-of-form)
print('<html>')
print('<head>')
print('<title>mkroesti %s</title>' % str(mkroesti.version))
print('<style type="text/css">')
print('body {background-color:#dddddd}')
print('#column-1 {float:left; width:50%;}')  # 50% works because the column
print('#column-2 {float:left; width:50%;}')  # containers don't have margins
print('#footer {clear:both;}')
print('#input        {background-color:#cceeff;}')  # light cyan
print('#algorithms   {background-color:#eeccff;}')  # light purple
print('#aliases      {background-color:#ccffee;}')  # light green
print('#output       {background-color:#ffffaa; clear:both;}')  # light yellow
print('#output-error {background-color:#ffcccc; clear:both;}')  # light red
print('#powered-by   {text-align:center;}')
print('div.section {')
print('  padding-left: 5px;')
print('  padding-right: 5px;')
print('  margin-bottom: 10px;')
print('  margin-right: 10px;')
print('  border-style: solid;')
print('  border-width: thin;')
print('  border-color: black;')
print('}')
print('p.sectiontitle {font-weight:bold}')
print('</style>')
print('</head>')
print('<body>')
print('<form name="%s" action="%s" method="post">' % (formName, scriptName))

# Print data entry part (including end-of-form)
print('<div id="column-1">')
print('<div class="section" id="input">')
print('<p class="sectiontitle">Enter the string to hash:</p>')
print('<table cellspacing="5">')
print('<tr>')
print('<td>Hash input:</td> <td><input type="text" name="%s" size="40" %s/></td>' % (fieldNameHashInput, defaultHashInput))
print('</tr>')
print('<tr>')
print('<td>Hash input (password):</td> <td><input type="password" name="%s" size="40" %s/></td>' % (fieldNameHashInputPassword, defaultHashInputPassword))
print('</tr>')
print('<tr>')
print('<td></td> <td><input type="submit"/><input type="reset"/></td>')
print('</tr>')
print('</table>')
print('<p>Please note:<ul>')
print('<li>Use either of the two text entry fields, but not both (if you do, the password field will be ignored).</li>')
print('<li>The password field can be used to prevent the input from being displayed in clear text on your monitor.</li>')
print('<li><em>Even if you use the password field, the text you type will be transmitted over the network in clear text! Transmission can be made safe by using a secure/encrypted connection (i.e. https), but even then the text will still be visible in clear text on the server side and might show up somewhere in a logfile. <strong>Please do not type in a valuable password!</strong></em></li>')
print('<li>The input is expected to be in UTF-8 character encoding. If you change the encoding the resulting hash might be incorrect.</li>')
print('</ul></p>')
print('</div>')  # section, input
print('</div>')  # column-1

# Print available algorithms and aliases
print('<div id="column-2">')
print('<div class="section" id="algorithms">')
print('<p class="sectiontitle">Select one or more algorithms:</p>')
printTable(sorted(availableAlgorithmNames), nrOfColumnsInAlgorithmAndAliasTables, form)
print('</div>')  # section, algorithms
print('<div class="section" id="aliases">')
print('<p class="sectiontitle">Select one or more aliases:</p>')
printTable(sorted(availableAliasNames), nrOfColumnsInAlgorithmAndAliasTables, form)
print('</div>')  # section, aliases
print('</div>')  # column-2

# Print generated hashes
if sortedResults is not None:
    print('<div id="footer">')
    print('<div class="section" id="output">')
    print('<p class="sectiontitle">Hash results:</p>')
    print('<table cellspacing="5">')
    for algorithmName, hashValue in sortedResults:
        print('<tr>')
        print('<td>%s:</td> <td>%s</td>' % (algorithmName, str(hashValue)))
        print('</tr>')
    print('</table>')
    print('</div>')
elif errorResults is not None:
    (exc_type, exc_value, exc_traceback) = errorResults
    print('<div class="section" id="output-error">')
    print('<p class="sectiontitle">Encountered unexpected error!</p>')
    print('<dl>')
    print('<dt>Error type</dt><dd>%s</dd>' % str(exc_type.__name__))
    print('<dt>Error details</dt><dd>%s</dd>' % str(exc_value))
    print('</dl>')
    print('</div>')  # section, output
    print('</div>')  # footer

# Set the focus to the first form field (the "hashInput" text field) and select
# its content
print('<script type="text/javascript">field=document.%s.%s;field.focus();field.select();</script>' % (formName, fieldNameHashInput));

# Print end-of-document
print('</form>')
print('<div id="powered-by">Powered by <a href="%s">mkroesti %s</a></div>' % (mkroesti.url, str(mkroesti.version)))
print('</body>')
print('</html>')
