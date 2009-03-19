# encoding=utf-8

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
        # Asserts that the option --version exits with code 0, and that it
        # prints a version string to stdout. The version string must end with
        # the current mkroesti version.
        try:
            args = ["--version"]
            main(args)
        except SystemExit, (errorInstance):
            self.assertEqual(errorInstance.code, 0)
        else:
            self.fail("SystemExit not raised")
        # Whatever this test is worth...
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
