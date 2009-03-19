# ----------------------------------------------------------------------
# Algorithm classes register themselves here. This registry is a Singleton.
# Clients should call AlgorithmRegistry.getInstance()
# ----------------------------------------------------------------------
class AlgorithmRegistry:
  instance = None
  @staticmethod
  def getInstance():
    if None == AlgorithmRegistry.instance:
      AlgorithmRegistry()
    return AlgorithmRegistry.instance

  def __init__(self):
    # Check if someone tries to create an instance without going through
    # getInstance()
    if None != AlgorithmRegistry.instance:
      raise RuntimeError, "Only one instance of AlgorithmRegistry is allowed!"
    AlgorithmRegistry.instance = self
    self.algorithms = dict()

  # Return the class object that implements the algorithm name
  def getAlgorithm(self, name):
    return self.algorithms[name]

  # Add class object algorithm which implements algorithm name
  def addAlgorithm(self, algorithm):
    if algorithm.name in self.algorithms:
      raise RuntimeError, "Algorithms can be registered only once!"
    self.algorithms[algorithm.name] = algorithm

# ----------------------------------------------------------------------
# Abstract base class
# ----------------------------------------------------------------------
class AbstractAlgorithm:
  def __init__(self, name):
    self.name = name
    AlgorithmRegistry.getInstance().addAlgorithm(self)

  def getName(self):
    return self.name

  # Returns a single hash
  def getHash(self, input):
    # Built-in exception; used to indicate that a sub-class did not override
    # this abstract method
    raise NotImplementedError

# ----------------------------------------------------------------------
# Concrete algorithms
# ----------------------------------------------------------------------
class Base64Algorithm(AbstractAlgorithm):
  def __init__(self):
    AbstractAlgorithm.__init__(self, "base64")
  def getHash(self, input):
    return "foo"

# ----------------------------------------------------------------------
# Instantiate algorithms
# ----------------------------------------------------------------------
class AlgorithmFactory:
  Base64Algorithm()
