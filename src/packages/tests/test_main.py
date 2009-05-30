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


"""Unit tests for mkroesti.main.py"""

# PSL
import unittest
import sys
import tempfile
import os

# mkroesti
from mkroesti.algorithm import AbstractAlgorithm
from mkroesti.errorhandling import ConversionError
from mkroesti.main import main
from mkroesti.provider import AbstractProvider
from mkroesti.registry import ProviderRegistry
import mkroesti


class StandardOutputReplacement():
    """An instance of this class can be used to replace sys.stdout or
    sys.stderr.

    Starting with the moment when sys.stdout or sys.stderr is replaced, any
    output to sys.stdout or sys.stderr will be added to a continually growing
    string buffer. The current content of the string buffer can be requested at
    any time by calling getStdoutBuffer().
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
        self.thisModule = sys.modules[__name__]
        # Replace stdout so that we can watch out for the generated hash
        self.stdoutOriginal = sys.stdout
        self.stdoutReplacement = StandardOutputReplacement()
        sys.stdout = self.stdoutReplacement
        # Replace stderr to prevent warnings from being printed
        self.stderrOriginal = sys.stderr
        self.stderrReplacement = StandardOutputReplacement()
        sys.stderr = self.stderrReplacement
        # A pre-defined algorithm with pre-defined input and expected output.
        # Note 1: We use an algorithm that is normally available on all systems
        # Note 2: We include some special non-ASCII characters in the input to
        # make life more interesting :-)
        self.hashAlgorithmName = "md5"
        self.hashInput = "foo-äöü-αβγ-⅓⅙⅞"
        self.hashExpectedOutput = {"utf-8" : "3f920874c43f9aee62346ee6543f7c2c",
                                   "utf-16" : "eebf197417a9ace8fca4729be42ee594"}

    def tearDown(self):
        ProviderRegistry.deleteInstance()
        sys.stdout = self.stdoutOriginal
        sys.stderr = self.stderrOriginal

    def testHelp(self):
        """Exercise the --help option"""

        # Asserts that the option -h exits with code 0, and that it prints a
        # hopefully helpful message to stdout. The message must start with
        # "Usage:", which is a string defined by the optparse module. 
        try:
            args = ["-h"]
            main(args)
        except SystemExit as errorInstance:
            self.assertEqual(errorInstance.code, 0)
        else:
            self.fail("SystemExit not raised")
        # Whatever this test is worth...
        self.assertEqual(self.stdoutReplacement.getStdoutBuffer()[:6], "Usage:")

    def testVersion(self):
        """Exercise the --version option"""

        # Asserts that the first line printed to stdout ends with the current
        # mkroesti version.
        args = ["-V"]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        versionLength = len(mkroesti.version)
        messageLines = self.stdoutReplacement.getStdoutBuffer().splitlines()
        firstMessageLine = messageLines[0]
        self.assertEqual(firstMessageLine[-versionLength:], mkroesti.version)

    def testBatchMode(self):
        """Exercise the --batch option"""

        encoding = "utf-8"
        args = ["-a", self.hashAlgorithmName, "-b", self.hashInput, "-c", encoding]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        actualHash = self.stdoutReplacement.getStdoutBuffer().strip()
        self.assertEqual(actualHash, self.hashExpectedOutput[encoding])

    def testListMode(self):
        """Exercise the --list option"""

        args = ["-l"]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        # Collect the algorithm names printed by the list command. Assume that
        # 1) no lines of the output can be skipped, and that
        # 2) each line contains whitespace-separated columns where the first
        #    column contains the algorithm name 
        outputLines = self.stdoutReplacement.getStdoutBuffer().splitlines()
        outputAlgorithmNames = dict()
        skipLines = 0
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
            self.assertTrue(registryAlgorithmName in outputAlgorithmNames, registryAlgorithmName)

    def testFileMode(self):
        """Exercise the --file option"""

        # Prepare the file. Specify the UTF-8 encoding because we know that
        # this file and therefore the literal stored in self.hashInput is
        # UTF-8 encoded.
        encoding = "utf-8"
        (fileHandle, absPathName) = tempfile.mkstemp()
        if mkroesti.python2:
            os.write(fileHandle, self.hashInput)
        else:
            os.write(fileHandle, self.hashInput.encode(encoding))
        os.close(fileHandle)
        # Generate the hash. We don't need to specify the encoding because the
        # file will be read as binary data.
        args = ["-a", self.hashAlgorithmName, "-f", absPathName]
        main(args)
        actualOutput = self.stdoutReplacement.getStdoutBuffer().strip()
        self.assertEqual(actualOutput, self.hashExpectedOutput[encoding])
        # Cleanup
        os.remove(absPathName)

    def testProviderModule(self):
        """Exercise the --providers option"""

        algorithmName = "SomeUniqueAlgorithmName"
        self.thisModule.provider = TestProvider(algorithmName)
        args = ["-a", algorithmName, "-b", self.hashInput, "-c", "utf-8", "-p", __name__]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        actualHash = self.stdoutReplacement.getStdoutBuffer().strip()
        self.assertEqual(actualHash, TestAlgorithmFixedHashValue.fixedHashValue)

    def testProviderPrecedence(self):
        """Test that built-in algorithms have precedence over 3rd party algorithms."""
        
        # Tell the bogus test algorithm to use the name of a well-known,
        # built-in algorithm. We expect that the built-in algorithm will be
        # used to provide the hash value. We know that this has happened if we
        # get the real valid hash value instead of the bogus fixed hash value.
        self.thisModule.provider = TestProvider(self.hashAlgorithmName)
        encoding = "utf-8"
        args = ["-a", self.hashAlgorithmName, "-b", self.hashInput, "-c", encoding, "-p", __name__]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        actualHash = self.stdoutReplacement.getStdoutBuffer().strip()
        self.assertEqual(actualHash, self.hashExpectedOutput[encoding])

    def testExcludeBuiltins(self):
        """Exercise the --exclude-builtins option"""

        # Tell the bogus test algorithm to use the name of a well-known,
        # built-in algorithm. We expect that --exclude-builtins will disable
        # the built-in algorithm, which will allow our bogus test algorithm to
        # kick in. We know that this has happened if we get the bogus fixed
        # hash value instead of the real valid hash value.
        self.thisModule.provider = TestProvider(self.hashAlgorithmName)
        args = ["-a", self.hashAlgorithmName, "-b", self.hashInput, "-c", "utf-8", "-p", __name__, "-x"]
        returnValue = main(args)
        self.assertEqual(returnValue, None)
        actualHash = self.stdoutReplacement.getStdoutBuffer().strip()
        self.assertEqual(actualHash, TestAlgorithmFixedHashValue.fixedHashValue)

    def testCodecValid(self):
        """Exercise the --codec option using a valid encoding"""

        # This test is not relevant for Python 2.6 because there the --codec
        # argument is ignored
        if not mkroesti.python2:
            encoding = "utf-16"
            args = ["-a", self.hashAlgorithmName, "-b", self.hashInput, "-c", encoding]
            returnValue = main(args)
            self.assertEqual(returnValue, None)
            actualHash = self.stdoutReplacement.getStdoutBuffer().strip()
            self.assertEqual(actualHash, self.hashExpectedOutput[encoding])

    def testCodecInvalid(self):
        """Exercise the --codec option using an invalid encoding"""

        # This test is not relevant for Python 2.6 because there the --codec
        # argument is ignored
        if not mkroesti.python2:
            # Conversion to this encoding will fail because self.hashInput contains
            # characters that do not exist in the target encoding
            encoding = "iso-8859-1"
            args = ["-a", self.hashAlgorithmName, "-b", self.hashInput, "-c", encoding]
            try:
                main(args)
            except ConversionError:
                pass
            else:
                self.fail("ConversionError not raised")


class TestProvider(AbstractProvider):
    """Provides the pseudo algorithm TestAlgorithmFixedHashValue under an
    arbitrary algorithm name. The algorithm name must be specified when this
    provider is instantiated.

    The test case that is going to employ this provider must create an instance
    of this provider and store it in this module's list of global attributes
    under the attribute name "provider". The test case must do so prior to
    invoking mkroesti. When mkroesti is invoked, it will then call the
    getProviders() method, which in turn will return the pre-fabricated
    provider instance.

    This somewhat complicated approach allows the test case to inject an
    algorithm with an arbitrary name into the system.
    
    Note: In a previous somewhat simpler scheme, I tried to store the algorithm
    name (which is the actual variable part that the test case should be able
    to vary) in a class attribute TestAlgorithmFixedHashValue.algorithmName.
    Unfortunately, by the time that getProviders() had been called, the class
    attribute had somehow mysteriously been deleted.
    """ 

    def __init__(self, algorithmName):
        AbstractProvider.__init__(self, [algorithmName])

    def getAlgorithmSource(self, algorithmName):
        return __name__

    def createAlgorithm(self, algorithmName):
        return TestAlgorithmFixedHashValue(algorithmName, self)


class TestAlgorithmFixedHashValue(AbstractAlgorithm):
    """Implements a pseudo algorithm that always returns a fixed hash value."""

    fixedHashValue = "fixed hash value"

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def needBytesInput(self):
        return True   # we don't really care since we don't really operate on the input

    def getHash(self, input):
        return TestAlgorithmFixedHashValue.fixedHashValue


def getProviders():
    """Function is called if mkroesti is run with --providers tests.test_main"""

    # Return a provider instance that must have been prepared previously by the
    # test case which triggers this method call.
    return [sys.modules[__name__].provider]


if __name__ == "__main__":
    unittest.main()
