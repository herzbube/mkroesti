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
import sys
import os
from optparse import OptionParser
import getpass
import codecs

# mkroesti
import mkroesti   # import stuff from __init__.py (e.g. mkroesti.version)
from mkroesti import factory
from mkroesti import registry
from mkroesti.errorhandling import MKRoestiError, ConversionError


def main(args = None):
    """Run the main() function of the mkrosti program.

    This function is intended to be called by different clients: The mkroesti
    front-end script (usually invoked from the command line), an automated
    testing environment (e.g. tests/test_main.py), another third-party python
    program, etc.

    This function is driven by command line arguments. It looks for them either
    in sys.argv[1:] (if args is None, which is the default), or in the args
    parameter itself. If sys.argv is used, this function assumes that it runs
    in a true command line environment, which means that in certain situations
    it may write a warning message to sys.stderr in order to notify the user
    that something fishy is going on :-)

    Regular output (i.e. the hash) is always written to sys.stdout. This output
    can be captured by replacing sys.stdout with a custom object. See
    tests.test_main.StandardOutputReplacement for an example.

    This function does not return a value. If no error has been raised, a
    command line program should now terminate with exit code 0.

    This function potentially raises all errors defined in
    mkroesti.errorhandling.

    As a special case, if the command line argument "-h" is specified,
    sys.exit(0) is called, which raises SystemExit.
    """

    # Determine whether we are running in a true command line argument. We
    # assume that this is the case if the caller of this function does not
    # specify any arguments in args, but lets us use sys.argv instead.
    cmdlineEnvironment = (args is None)

    # Create and set up the option parser
    parser = setupOptionParser()

    # Start processing options. If args is None (the default), the option parser
    # will use sys.argv as the source for command line arguments.
    (options, args) = parser.parse_args(args = args)
    hashInput = None
    if options.version:
        print(os.path.basename(sys.argv[0]) + " " + mkroesti.version)
        print("Default encoding: " + sys.getdefaultencoding())
        return

    # Register providers with the registry; must do this early because
    # processing some of the options relies on providers already being present.
    providerModuleNames = list()
    if not options.excludeBuiltins:
        providerModuleNames.append("mkroesti.provider")
    if options.providers:
        providerModuleNames.extend(options.providers.split(","))
    registerProviders(providerModuleNames)

    # Determine the encoding that should be used to convert between binary and
    # string data (or vice versa).
    # Note 1: There is a check further down to prevent character encoding
    # specification when the input is read interactively via sys.stdin.
    # Note 2: Encodings are ignored in Python 2.6 because Python 2.6 has no
    # binary data type that might require converting.
    encoding = sys.getdefaultencoding()
    if options.codec is not None:
        if options.list:
            raise MKRoestiError("Cannot specify a character encoding in list mode")
        encoding = options.codec
        if mkroesti.python2:
            print("Warning: Ignoring --codec because it has no meaning for Python 2.6", file = sys.stderr)
        else:
            try:
                # We are not interested in the codec object returned by lookup(),
                # we just want to know if the name specified by --codec exists
                codecs.lookup(encoding)
            except LookupError:
                raise MKRoestiError("Unknown encoding: " + encoding)

    # Check for different modes (batch, file, list, stdin)
    # Note: The order in which arguments are checked is important!
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
        # In Python 3, hashInput is of type str (not bytes). It has already
        # been interpreted using the default encoding.
        hashInput = args[0]
    elif options.file is not None:
        if options.echo:
            parser.error("echo mode cannot be combined with reading from file")
        elif options.list:
            parser.error("list mode cannot be combined with reading from file")
        try:
            # Explicitly use "binary" mode. If omitted, Python 3 would open the
            # file in text mode and interpret the file's content using the
            # current default encoding - which might, or might not, produce the
            # correct results. In Python 2.6, read() returns data as type str,
            # but in its raw, uninterpreted form.
            file = open(options.file, "rb")
            try:
                hashInput = file.read()
            finally:
                file.close()
        except IOError as exc:
            # TODO: We previously accessed exc.arg (singular), but changed this
            # to exc.args (plural). Check if this (the plural) works with
            # Python 2.6. Probably not...
            errno, strerror = exc.args
            raise MKRoestiError(strerror)   # pass on detailed error description (e.g. "no such file")
    elif options.list:
        # --list implies --duplicate-hashes
        if not options.duplicateHashes:
            options.duplicateHashes = True
        listAlgorithms()
        return
    else:
        if not sys.stdin.isatty():
            # Get the input directly from the stdin file object, if stdin is
            # not attached to a TTY. This is the case e.g. because a pipe has
            # been set up, or a file has been redirected to stdin. read() will
            # read until EOF is reached, it is therefore possible to process
            # input with, for instance, multiple lines, or an entire file. We
            # don't use input() or raw_input() because these are line oriented.
            #
            # Python 3: sys.stdin is in text mode, so reading from it would cause
            # Python 3 to interpret the data using the current default encoding.
            # To prevent that, we are using the underlying binary buffer of
            # sys.stdin to read binary data (this is recommended by the Python 3
            # docs for sys.stdin)
            #
            # Python 2.6: We perform the read operation directly on the
            # sys.stdin object because Python 2.6 does not have the bytes data
            # type, so read() will give us a str object with raw, uninterpreted
            # data.
            if mkroesti.python2:
                hashInput = sys.stdin.read()
            else:
                hashInput = sys.stdin.buffer.read()
        else:
            # Get a single line of input (newline is stripped). In Python 3, the
            # input is of type str for both functions.
            prompt = "Enter text to hash: "
            if options.echo:
                if mkroesti.python2:
                    hashInput = raw_input(prompt)
                else:
                    hashInput = input(prompt)
            else:
                hashInput = getpass.getpass(prompt)

    # Create algorithm objects
    algorithms = list()
    for name in options.algorithms.split(","):
        # Don't check whether the same algorithm name appears twice in
        # options.algorithms (we would need to resolve aliases first) - if the
        # user specifies the same algorithm multiple times, she will see the
        # same hash if she has also enabled --duplicate-hashes, but that is her
        # problem...
        algorithms.extend(factory.AlgorithmFactory.createAlgorithms(name, options.duplicateHashes))

    if mkroesti.python2:
        # Hash input type handling is not required for Python 2.6
        pass
    else:
        # In Python 3 only: The input might be present as either type str or bytes.
        # We might need to convert from one to the other, depending on the
        # requirements of each algorithm. We delay such conversion until it becomes
        # really necessary. Reason 1: Efficiency. For instance, it makes no sense
        # to convert a large file to type str, when we will never need that str.
        # Reason 2 (the real reason :-): It is actually impossible to convert
        # *binary* files into str. Should the user request an algorithm that
        # requires conversion to str, the result will be an error. If we were to
        # perform conversion up front, we would therefore *always* have an error.
        hashInputType = type(hashInput)
        if hashInputType is type(str()):
            hashInputAsStr = hashInput
            hashInputAsBytes = None
        elif hashInputType == type(bytes()):
            hashInputAsStr = None
            hashInputAsBytes = hashInput
        else:
            raise MKRoestiError("Hash input object has unsupported type: " + str(hashInputType))

        # Find out what kind of input data we need to make all algorithms happy
        needBytesInput = False
        needStrInput = False
        for algorithm in algorithms:
            if algorithm.needBytesInput():
                needBytesInput = True
            else:
                needStrInput = True

        # Perform the actual conversion
        conversionRequired = False
        if needBytesInput:
            if hashInputAsBytes is None:
                conversionRequired = True
                try:
                    hashInputAsBytes = hashInputAsStr.encode(encoding)
                except UnicodeEncodeError:
                    # This happens, for instance, if we try to encode a
                    # character that does not exist in the encoding's target
                    # character set (e.g. "β" does not exist in "iso-8859-1")
                    raise ConversionError("Cannot convert input to binary data (the encoding used was '" + encoding + "')")
        if needStrInput:
            if hashInputAsStr is None:
                conversionRequired = True
                try:
                    hashInputAsStr = hashInputAsBytes.decode(encoding)
                except UnicodeDecodeError:
                    # This happens, for instance, if we try to decode binary
                    # data, because no encoding can sensibly decode binary data
                    raise ConversionError("Cannot convert input to string data (the encoding used was '" + encoding + "')")

        # Issue final warnings before we start generating hashes
        # Note: Only warn if the user explicitly specified --codec.
        if not conversionRequired and options.codec:
            print("Warning: Ignoring --codec because no conversion was required", file = sys.stderr)
        if hashInputType is type(str()) and needBytesInput and options.codec:
            print("Warning: Re-interpreting input data using encoding '" + encoding + "' (Python has already interpreted your input using a locale-based encoding)", file = sys.stderr)

    # Create hashes
    algorithmCount = len(algorithms)
    for algorithm in algorithms:
        algorithmName = algorithm.getName()
        if mkroesti.python2:
            hash = algorithm.getHash(hashInput)
        else:
            if algorithm.needBytesInput():
                hash = algorithm.getHash(hashInputAsBytes)
            else:
                hash = algorithm.getHash(hashInputAsStr)
        if algorithmCount == 1:
            print(hash)
        else:
            if not options.duplicateHashes:
                print(algorithmName + ": " + str(hash))
            else:
                print(algorithmName + " (" + algorithm.getProvider().getAlgorithmSource(algorithmName) + "): " + str(hash))


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
        if not hasattr(theCallable, "__call__"):
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
    for (algorithmName, sourceString, availableString) in lineList:
        print(algorithmName.ljust(algorithmColumnWidth), \
              columnSeparator, \
              sourceString.ljust(sourceColumnWidth), \
              columnSeparator, \
              availableString.ljust(availableColumnWidth))


def setupOptionParser():
    usage = """
    %prog [-a LIST] [-d] [-x] [-p LIST] [-c CODEC] [-e]
    %prog [-a LIST] [-d] [-x] [-p LIST] [-c CODEC] -b input
    %prog [-a LIST] [-d] [-x] [-p LIST] [-c CODEC] -f file
    %prog -l [-x] [-p LIST]
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
    parser.add_option("-c", "--codec",
                      action="store", dest="codec", metavar="CODEC", default=None,
                      help="interpret the input using the character encoding named CODEC; see man page for details")
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
