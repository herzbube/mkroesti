# encoding=utf-8

# $Id: test_main.py 40 2008-12-02 00:04:32Z patrick $

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


"""Unit tests for mkroesti.main.py"""

# PSL
import unittest
import sys
import tempfile
import os

# mkroesti
from mkroesti.main import main
from mkroesti.registry import ProviderRegistry
import mkroesti


class StandardOutputReplacement():
    """An instance of this class can be used to replace sys.stdout.
    
    Starting with the moment when sys.stdout is replaced, any output to
    sys.stdout will be added to a continually growing string buffer. The
    current content of the string buffer can be requested at any time by
    calling getStdoutBuffer().
    """

    def __init__(self):
        self.stdoutBuffer = None
    def write(self, messageString):
        if self.stdoutBuffer is None:
            self.stdoutBuffer = messageString
        else:
            self.stdoutBuffer = self.stdoutBuffer + messageString
    def getStdoutBuffer(self):
        """Return current content of string buffer, or None if nothing has been output yet to sys.stdout."""
        return self.stdoutBuffer


class MainTest(unittest.TestCase):
    """Exercise mkroesti.main.main()"""

    def setUp(self):
        self.stdoutOriginal = sys.stdout
        self.stdoutReplacement = StandardOutputReplacement()
        sys.stdout = self.stdoutReplacement
        # A pre-defined algorithm with pre-defined input and expected output
        self.hashAlgorithmName = "md5"
        self.hashInput = "foo"
        self.hashExpectedOutput = "acbd18db4cc2f85cedef654fccc4a4d8" 

    def tearDown(self):
        ProviderRegistry.deleteInstance()
        sys.stdout = self.stdoutOriginal

    def testHelp(self):
        # Asserts that the option -h exits with code 0, and that it prints a
        # hopefully helpful message to stdout. The message must start with
        # "Usage:", which is a string defined by the optparse module. 
        try:
            args = ["-h"]
            main(args)
        except SystemExit, (errorInstance):
            self.assertEqual(errorInstance.code, 0)
        else:
            self.fail("SystemExit not raised")
        # Whatever this test is worth...
        self.assertEqual(self.stdoutReplacement.getStdoutBuffer()[:6], "Usage:")

    def testVersion(self):
        # Asserts that the version string printed to stdout ends with the
        # current mkroesti version.
        args = ["-V"]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        versionLength = len(mkroesti.version)
        strippedMessage = self.stdoutReplacement.getStdoutBuffer().strip()
        self.assertEqual(strippedMessage[-versionLength:], mkroesti.version)

    def testBatchMode(self):
        # Make only a single test with MD5 (this algorithm should be
        # available on all systems)
        args = ["-a", self.hashAlgorithmName, "-b", self.hashInput]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        actualHash = self.stdoutReplacement.getStdoutBuffer().strip()
        self.assertEqual(actualHash, self.hashExpectedOutput)

    def testListMode(self):
        args = ["-l"]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        # Collect the algorithm names printed by the list command. Assume that
        # 1) the first two lines of the output can be skipped, and that
        # 2) each line contains whitespace-separated columns where the first
        #    column contains the algorithm name 
        outputLines = self.stdoutReplacement.getStdoutBuffer().splitlines()
        outputAlgorithmNames = dict()
        skipLines = 2
        for outputLine in outputLines:
            if skipLines > 0:
                skipLines -= 1
                continue
            fields = outputLine.split()
            algorithmName = fields[0]
            outputAlgorithmNames[algorithmName] = None
        # Make sure that each algorithm known by the registry is also present
        # at least once in the output of the list command
        registryAlgorithmNames = ProviderRegistry.getInstance().getAlgorithmNames()
        for registryAlgorithmName in registryAlgorithmNames:
            self.assertTrue(registryAlgorithmName in outputAlgorithmNames)

    def testFileMode(self):
        (fileHandle, absPathName) = tempfile.mkstemp()
        os.write(fileHandle, self.hashInput)
        os.close(fileHandle)
        # Make only a single test with MD5 (this algorithm should be
        # available on all systems)
        args = ["-a", self.hashAlgorithmName, "-f", absPathName]
        main(args)
        actualOutput = self.stdoutReplacement.getStdoutBuffer().strip()
        self.assertEqual(actualOutput, self.hashExpectedOutput)
        os.remove(absPathName)


if __name__ == "__main__":
    unittest.main()
