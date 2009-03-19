from optparse import OptionParser
import algorithm

# ----------------------------------------------------------------------
# processes command line options
# ----------------------------------------------------------------------
def main():
  # Setup the option parser
  version = "%prog 0.1"
  usage = """
    %prog [-e] [-a LIST]
    %prog -b [-a LIST] input
    %prog -f file [-a LIST]
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

  # Process options
  (options, args) = parser.parse_args()

  # Note: The order in which arguments are checked is important!
  if options.batch:
    if options.echo:
      parser.error("batch mode cannot be combined with echo mode")
    elif options.file:
      parser.error("batch mode cannot be combined with reading input from file")
    elif len(args) == 0:
      parser.error("missing input for batch processing")
  elif options.file:
    if options.echo:
      parser.error("echo mode cannot be combined with reading from file")
    # todo: test whether file exists/can be read
  else:
    pass
    # todo: acquire input from stdin

  x = algorithm.AlgorithmRegistry.getInstance().getAlgorithm("base64");
  print x
  print "hash = ", x.getHash("iiiii")
