# PSL
import sys
from optparse import OptionParser

# mkroesti
from mkroesti import factory
from mkroesti.errorhandling import MKRoestiError
import mkroesti.provider


def main():
    # Setup the option parser
    version = "%prog 0.1"
    usage = """
    %prog [-e] [-a LIST]
    %prog -b [-a LIST] input
    %prog -f file [-a LIST]
    %prog -l
    %prog -h"""

    parser = OptionParser(usage=usage, version=version)
    # "dest" is the name that can be used to refer to the option's value when
    # actual argument parsing commences
    parser.add_option("-a", "--algorithms",
                      action="store", dest="algorithms", metavar="ALGORITHMS", default="all",
                      help="Comma separated list of algorithms for which to generate hashes. See man page for details.")
    parser.add_option("-b", "--batch",
                      action="store_true", dest="batch", default=False,
                      help="Use batch mode; i.e., get the input from the command line rather than prompting for it. This option should be used with extreme care, since if the input is a password, it will be clearly visible on the command line.")
    parser.add_option("-e", "--echo",
                      action="store_true", dest="echo", default=False,
                      help="Enable Echo mode; i.e. when the user is prompted for input, the characters she types are echoed on the screen")
    parser.add_option("-f", "--file",
                      action="store", dest="file", metavar="FILE",
                      help="Read the input from FILE")
    parser.add_option("-l", "--list",
                      action="store_true", dest="list", default=False,
                      help="List supported algorithms, which ones are available, and which implementation sources exist for them")

    # Process options
    # Note: The order in which arguments are checked is important!
    (options, args) = parser.parse_args()
    input = None
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
                input = file.read()
            finally:
                file.close()
        except IOError, (errno, strerror):
            raise MKRoestiError(strerror)
    elif options.list:
        pass
    else:
        # Use read() to read until EOF is reached (e.g. Ctrl+D is pressed)
        # Note: Don't use input() or raw_input() because these are line oriented
        input = sys.stdin.read()

    # Create algorithm objects
    algorithms = list()
    for name in options.algorithms.split(","):
        # TODO we should make first resolve everything in options.algorithms
	# and then make sure that no algorithm name appears twice
        algorithms.extend(factory.AlgorithmFactory.createAlgorithms(name))

    # Create hashes
    algorithmCount = len(algorithms)
    for algorithm in algorithms:
        hash = algorithm.getHash(input)
        if algorithmCount == 1:
            print hash
        else:
            print algorithm.getName() + ": " + str(hash)

