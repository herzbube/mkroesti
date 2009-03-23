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
import os
from optparse import OptionParser
import getpass

# mkroesti
import mkroesti   # import stuff from __init__.py (e.g. mkroesti.version)
from mkroesti import factory
from mkroesti import registry
from mkroesti.errorhandling import MKRoestiError


def main(args = None):
    """Run the main() function.

    args is the list of command line arguments that should be used (default is
    sys.argv[1:]). This is mainly intended for testing purposes.

    Writes output to sys.stdout.

    Does not return a value. If no error has been raised, a command line program
    should now return with exit code 0.

    Potentially raises all errors defined in mkroesti.errorhandling.

    As a special case, if the command line argument "-h" or "--version" is
    specified, sys.exit(0) is called, which raises SystemExit.
    """

    # Create and set up the option parser
    parser = setupOptionParser()

    # Start processing options
    # Note: The order in which arguments are checked is important!
    (options, args) = parser.parse_args(args = args)
    input = None
    if options.version:
        print os.path.basename(sys.argv[0]) + " " + mkroesti.version
        return

    # Registers providers with the registry; must do this early because
    # processing some of the options relies on providers already being present.
    providerModuleNames = list()
    if not options.excludeBuiltins:
        providerModuleNames.append("mkroesti.provider")
    if options.providers:
        providerModuleNames.extend(options.providers.split(","))
    registerProviders(providerModuleNames)

    # Check for different modes (batch, file, list, stdin)
    if options.batch:
        if options.echo:
            parser.error("batch mode cannot be combined with echo mode")
        elif options.file:
            parser.error("batch mode cannot be combined with reading input from file")
        elif options.list:
            parser.error("batch mode cannot be combined with list mode")
        elif len(args) == 0:
            parser.error("missing input for batch processing")
        elif len(args) > 1:
            parser.error("too many input arguments for batch processing")
        input = args[0]
    elif options.file is not None:
        if options.echo:
            parser.error("echo mode cannot be combined with reading from file")
        elif options.list:
            parser.error("batch mode cannot be combined with list mode")
        try:
            file = open(options.file, "r")
            try:
                input = file.read()   # read() returns data as string
            finally:
                file.close()
        except IOError, (errno, strerror): #@UnusedVariable
            raise MKRoestiError(strerror)
    elif options.list:
        # --list implies --duplicate-hashes
        if not options.duplicateHashes:
            options.duplicateHashes = True
        listAlgorithms()
        return
    else:
        # Get the input from stdin if it is not attached to a TTY (e.g. because
        # a pipe has been set up, or a file has been redirected to stdin). read()
        # will read until EOF is reached, it is therefore possible to process
        # input with, for instance, multiple lines. read() returns data as
        # string.
        # Note: Don't use input() or raw_input() because these are line
        # oriented
        if not sys.stdin.isatty():
            input = sys.stdin.read()
        else:
            # Get a single line of input (newline is stripped)
            prompt = "Enter text to hash: "
            if options.echo:
                input = raw_input(prompt)
            else:
                input = getpass.getpass(prompt)

    # Create algorithm objects
    algorithms = list()
    for name in options.algorithms.split(","):
        # Don't check whether the same algorithm name appears twice in
        # options.algorithms (we would need to resolve aliases first) - if the
        # user specifies the same algorithm multiple times, she will see the
        # same hash if she has also enabled --duplicate-hashes, but that is her
        # problem...
        algorithms.extend(factory.AlgorithmFactory.createAlgorithms(name, options.duplicateHashes))

    # Create hashes
    algorithmCount = len(algorithms)
    for algorithm in algorithms:
        hash = algorithm.getHash(input)
        if algorithmCount == 1:
            print hash
        else:
            algorithmName = algorithm.getName()
            if not options.duplicateHashes:
                print algorithmName + ": " + str(hash)
            else:
                print algorithmName + " (" + algorithm.getProvider().getAlgorithmSource(algorithmName) + "): " + str(hash)


def registerProviders(providerModuleNames):
    if len(providerModuleNames) == 0:
        return
    # For each provider module, do the following
    # - try to import it
    # - try and find the callable that returns provider instances
    # - execute the callable, then register every provider instance that the
    #   callable returned to us
    callableName = "getProviders"
    for providerModuleName in providerModuleNames:
        try:
            # We could test first whether the module has already been imported,
            # but we are lazy and rely on __import__() doing that for us...
            __import__(providerModuleName)
        except ImportError:
            raise MKRoestiError("Unable to import provider module " + providerModuleName)
        providerModule = sys.modules[providerModuleName]
        try:
            theCallable = getattr(providerModule, callableName)
        except AttributeError:
            raise MKRoestiError("Provider module " + providerModuleName + " has no attribute named " + callableName)
        if not callable(theCallable):
            raise MKRoestiError("Provider module " + providerModuleName + " has an attribute named " + callableName + ", but it is not a callable")
        # Don't check whether we have processed the same module in a previous
        # iteration - if the user specifies the same module multiple times, she
        # will see the same hash if she has also enabled --duplicate-hashes,
        # but that is her problem...
        providers = theCallable()
        # It's ok if the module returns 0 providers - we don't know why it
        # would want to do so, but who are we to judge :-)
        if providers is None:
            continue
        for provider in providers:
            registry.ProviderRegistry.getInstance().addProvider(provider)


def listAlgorithms():
    # Hard-coded
    columnSeparatorWidth = 2
    # Calculated during first pass
    algorithmColumnWidth = 0
    sourceColumnWidth = 0
    availableColumnWidth = 0
    # First pass: collect strings to output and calculate column widths
    lineList = list()
    algorithmNames = registry.ProviderRegistry.getInstance().getAlgorithmNames()
    # Sort by algorithm name
    algorithmNames.sort()
    for algorithmName in algorithmNames:
        providers = registry.ProviderRegistry.getInstance().getProviders(algorithmName)
        for provider in providers:
            sourceString = provider.getAlgorithmSource(algorithmName)
            (isAvailable, reason) = provider.isAlgorithmAvailable(algorithmName)
            if isAvailable:
                availableString = "yes"
            else:
                availableString = "no (" + reason + ")"
            if len(algorithmName) > algorithmColumnWidth:
                algorithmColumnWidth = len(algorithmName)
            if len(sourceString) > sourceColumnWidth:
                sourceColumnWidth = len(sourceString)
            if len(availableString) > availableColumnWidth:
                availableColumnWidth = len(availableString)
            lineList.append((algorithmName, sourceString, availableString))
    # Second pass: print output
    columnSeparator = " ".ljust(columnSeparatorWidth)
    print "Algorithm".ljust(algorithmColumnWidth), columnSeparator, "Source".ljust(sourceColumnWidth), columnSeparator, "Available (reason)".ljust(availableColumnWidth)
    print "---------".ljust(algorithmColumnWidth), columnSeparator, "------".ljust(sourceColumnWidth), columnSeparator, "------------------".ljust(availableColumnWidth)
    for (algorithmName, sourceString, availableString) in lineList:
        print algorithmName.ljust(algorithmColumnWidth), \
              columnSeparator, \
              sourceString.ljust(sourceColumnWidth), \
              columnSeparator, \
              availableString.ljust(availableColumnWidth)


def setupOptionParser():
    usage = """
    %prog [-e] [-a LIST] [-d]
    %prog -b [-a LIST] [-d] input
    %prog -f file [-a LIST] [-d]
    %prog -l
    %prog -V
    %prog -h"""

    parser = OptionParser(usage = usage)
    # "dest" is the name that can be used to refer to the option's value when
    # actual argument parsing commences
    parser.add_option("-V", "--version",
                      action="store_true", dest="version", default=False,
                      help="show program's version number and exit")
    parser.add_option("-a", "--algorithms",
                      action="store", dest="algorithms", metavar="ALGORITHMS", default="all",
                      help="comma separated list of algorithms for which to generate hashes; see man page for details")
    parser.add_option("-b", "--batch",
                      action="store_true", dest="batch", default=False,
                      help="use batch mode; i.e., get the input from the command line rather than prompting for it; this option should be used with extreme care, since if the input is a password, it will be visible to any program or user looking at the system's list of processes at the time when mkroesti is run")
    parser.add_option("-d", "--duplicate-hashes",
                      action="store_true", dest="duplicateHashes", default=False,
                      help="allow duplicate hashes; i.e. if the same algorithm is available from multiple implementation sources, generate a hash for each implementation")
    parser.add_option("-e", "--echo",
                      action="store_true", dest="echo", default=False,
                      help="enable echo mode; i.e. when the user is prompted for input, the characters she types are echoed on the screen")
    parser.add_option("-f", "--file",
                      action="store", dest="file", metavar="FILE",
                      help="read the input from FILE")
    parser.add_option("-l", "--list",
                      action="store_true", dest="list", default=False,
                      help="list supported algorithms, which ones are available, and which implementation sources exist for them")
    parser.add_option("-p", "--providers",
                      action="store", dest="providers", metavar="PROVIDERS", default=None,
                      help="comma separated list of third party Python modules that provide hash algorithms; see man page for details")
    parser.add_option("-x", "--exclude-builtins",
                      action="store_true", dest="excludeBuiltins", default=False,
                      help="exclude built-in algorithms from the operation of mkroesti")
    return parser


if __name__ == "__main__":
    main()
