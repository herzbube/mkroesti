# encoding=utf-8

"""Unit tests for mkroesti.main.py"""

# PSL
import unittest
import sys

# mkroesti
from mkroesti.main import main
from mkroesti.registry import ProviderRegistry
import mkroesti


class StandardOutputReplacement():
    """An instance of this class can be used to replace sys.stdout."""

    def __init__(self):
        self.lastMessageString = None
    def write(self, messageString):
        self.lastMessageString = messageString
    def getLastMessageString(self):
        return self.lastMessageString

class MainTest(unittest.TestCase):
    """Exercise mkroesti.main.main()"""

    def setUp(self):
        self.stdoutOriginal = sys.stdout
        self.stdoutReplacement = StandardOutputReplacement()
        sys.stdout = self.stdoutReplacement 

    def tearDown(self):
        ProviderRegistry.deleteInstance()
        sys.stdout = self.stdoutOriginal

    def testHelp(self):
        try:
            args = ["-h"]
            main(args)
        except SystemExit, (errorInstance):
            self.assertEqual(errorInstance.code, 0)
        else:
            self.fail("SystemExit not raised")
        # Whatever this test is worth...
        self.assertEqual(self.stdoutReplacement.getLastMessageString()[:6], "Usage:")

    def testVersion(self):
        try:
            args = ["--version"]
            main(args)
        except SystemExit, (errorInstance):
            self.assertEqual(errorInstance.code, 0)
        else:
            self.fail("SystemExit not raised")
        # Whatever this test is worth...
        versionLength = len(mkroesti.version)
        strippedMessage = self.stdoutReplacement.getLastMessageString().strip()
        self.assertEqual(strippedMessage[-versionLength:], mkroesti.version)

    def testBatchMode(self):
        try:
            # Make only a single test with MD5 (this algorithm should be
            # available on all systems)
            args = ["-a", "md5", "-b", "foo"]
            main(args)
        except SystemExit, (errorInstance):
            self.assertEqual(errorInstance.code, 0)
        else:
            self.fail("SystemExit not raised")
        expectedHash = "acbd18db4cc2f85cedef654fccc4a4d8"
        actualHash = self.stdoutReplacement.getLastMessageString().strip()
        self.assertEqual(actualHash, expectedHash)

    def testListMode(self):
        try:
            # Make only a single test with MD5 (this algorithm should be
            # available on all systems)
            args = ["-l"]
            main(args)
        except SystemExit, (errorInstance):
            self.assertEqual(errorInstance.code, 0)
        else:
            self.fail("SystemExit not raised")
        expectedOutput = "TODO"
        actualOutput = self.stdoutReplacement.getLastMessageString().strip()
        self.assertEqual(actualOutput, expectedOutput)

    def testFileMode(self):
        try:
            # Make only a single test with MD5 (this algorithm should be
            # available on all systems)
            args = ["-f", "foo"]
            main(args)
        except SystemExit, (errorInstance):
            self.assertEqual(errorInstance.code, 0)
        else:
            self.fail("SystemExit not raised")
        expectedOutput = "TODO"
        actualOutput = self.stdoutReplacement.getLastMessageString().strip()
        self.assertEqual(actualOutput, expectedOutput)


if __name__ == "__main__":
    unittest.main()
