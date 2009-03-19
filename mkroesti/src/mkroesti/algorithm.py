"""Contains algorithm related classes.

AlgorithmFactory is used to create instances of algorithm classes based on the
algorithm's name. An algorithm class must derive from AlgorithmInterface and
upon instantiation must register its instances with the AlgorithmRegistry.

AbstractAlgorithm derives from AlgorithmInterface. It is a base class that
concrete algorithm classes may inherit from. It implements some useful features
such as registering with the AlgorithmRegistry singleton. Notably, it does not
implement the getHash() function.

AlgorithmRegistry is where algorithm objects register themselves and clients
get references to these algorithm objects. AlgorithmRegistry is a singleton.

Apart from the classes mentioned so far, this module contains a number of
concrete algorithm classes. These classes are not listed here. Clients should
not need to know about these concrete algorithm classes, instead they should
refer to algorithms by name.
"""


import base64
import hashlib

import smbpasswd

from mkroesti.errorhandling import MKRoestiError


class AlgorithmRegistry:
    """Registry where algorithm objects register themselves.

    AlgorithmRegistry uses an algorithm object's name to maintain the registry.
    Clients may retrieve an algorithm object by calling getAlgorithm() and
    specifying the algorithm name. Clients should use the interface defined by
    AlgorithmInterface to interact with the algorithm object.

    AlgorithmRegistry is a singleton. The singleton accessor (and creator)
    is AlgorithmRegistry.getInstance().
    """

    _instance = None

    @staticmethod
    def getInstance():
        """Access the singleton."""
        if None == AlgorithmRegistry._instance:
            AlgorithmRegistry()
        return AlgorithmRegistry._instance

    def __init__(self):
        """Create the singleton."""
        if None != AlgorithmRegistry._instance:
            raise MKRoestiError("Only one instance of AlgorithmRegistry is allowed!")
        AlgorithmRegistry._instance = self
        self.algorithms = dict()

    def getAlgorithm(self, name):
        """Returns the algorithm object that implements the algorithm name."""
        if not name in self.algorithms:
            raise MKRoestiError("Unknown algorithm " + name)
        return self.algorithms[name]

    def addAlgorithm(self, algorithm):
        """Adds an algorithm objects to this registry."""
        if algorithm.name in self.algorithms:
            raise MKRoestiError("Algorithms can be registered only once!")
        if not isinstance(algorithm, AlgorithmInterface):
            raise MKRoestiError(str(algorithm) + " is not derived from AlgorithmInterface!")
        self.algorithms[algorithm.name] = algorithm


class AlgorithmInterface:
    """Interface that must be implemented by algorithm classes."""

    def getName(self):
        """Returns a string that is the name of the algorithm."""
        raise NotImplementedError

    def getHash(self, input):
        """Returns a string that is the result of the algorithm hashing input."""
        raise NotImplementedError


class AbstractAlgorithm(AlgorithmInterface):
    """Abstract base class that implements common features of algorithm classes."""

    def __init__(self, name):
        self.name = name
        AlgorithmRegistry.getInstance().addAlgorithm(self)

    def getName(self):
        return self.name


class Base64Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "base64")

    def getHash(self, input):
        return base64.b64encode(input)


class MD5Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "md5")

    def getHash(self, input):
        algorithm = hashlib.md5(input)
        return algorithm.hexdigest()


class SHA1Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-1")

    def getHash(self, input):
        algorithm = hashlib.sha1(input)
        return algorithm.hexdigest()


class SHA224Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-224")

    def getHash(self, input):
        algorithm = hashlib.sha224(input)
        return algorithm.hexdigest()


class SHA256Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-256")

    def getHash(self, input):
        algorithm = hashlib.sha256(input)
        return algorithm.hexdigest()


class SHA384Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-384")

    def getHash(self, input):
        algorithm = hashlib.sha384(input)
        return algorithm.hexdigest()


class SHA512Algorithm(AbstractAlgorithm):
    def __init__(self):
        AbstractAlgorithm.__init__(self, "sha-512")

    def getHash(self, input):
        algorithm = hashlib.sha512(input)
        return algorithm.hexdigest()


class OpenSSLAlgorithm(AbstractAlgorithm):
    """Generic class that provides access to OpenSSL algorithms by name.

    Use the supportsAlgorithm() method to check whether you can create an
    instance of OpenSSLAlgorithm using the given name.
    """
    
    def __init__(self, name):
        AbstractAlgorithm.__init__(self, name)

    def getHash(self, input):
        opensslAlgorithmName = OpenSSLAlgorithm.mapAlgorithmName(self.getName())
        algorithm = hashlib.new(opensslAlgorithmName)
        algorithm.update(input)
        return algorithm.hexdigest()

    @staticmethod
    def mapAlgorithmName(mkroestiName):
        if "ripemd-160" == mkroestiName:
           return "rmd160"
        if "sha-0" == mkroestiName:
           return "sha"
        elif "md2" == mkroestiName or \
             "md4" == mkroestiName:
           return mkroestiName
        else:
           return None

    @staticmethod
    def supportsAlgorithm(name):
       if OpenSSLAlgorithm.mapAlgorithmName(name) is not None:
           return True
       else:
          return False


class AlgorithmFactory:
    """Factory class that instantiates algorithm classes."""

    @staticmethod
    def resolveAliases(algorithmNames):
        """Resolves aliases to real algorithm names.

        algorithmNames is expected to be a list of strings. The return value is
        a list whose members correspond to those of the input list
        algorithmNames. Any members that were aliases have been replaced by the
        real algorithm names that the alias refers to.
        """

        returnList = list()
        for algorithmName in algorithmNames:
            if "all" == algorithmName:
                returnList.append("base64")
                returnList.append("crypt")
                returnList.append("apr1")
                returnList.append("md2")
                returnList.append("md4")
                returnList.append("md5")
                returnList.append("whirlpool")
                returnList.append("windows-lm")
                returnList.append("windows-nt")
                returnList.append("mysql-password")
                returnList.extend(AlgorithmFactory.resolveAliases(["sha"]))
                returnList.extend(AlgorithmFactory.resolveAliases(["ripemd"]))
                returnList.extend(AlgorithmFactory.resolveAliases(["haval"]))
                returnList.extend(AlgorithmFactory.resolveAliases(["tiger"]))
            elif "sha" == algorithmName:
                returnList.append("sha-0")
                returnList.append("sha-1")
                returnList.append("sha-224")
                returnList.append("sha-256")
                returnList.append("sha-384")
                returnList.append("sha-512")
            elif "ripemed" == algorithmName:
                returnList.append("ripemd")
                returnList.append("ripemd-128")
                returnList.append("ripemd-160")
                returnList.append("ripemd-256")
                returnList.append("ripemd-320")
            elif "haval" == algorithmName:
                returnList.append("haval-128-3")
                returnList.append("haval-128-4")
                returnList.append("haval-128-5")
                returnList.append("haval-160-3")
                returnList.append("haval-160-4")
                returnList.append("haval-160-5")
                returnList.append("haval-192-3")
                returnList.append("haval-192-4")
                returnList.append("haval-192-5")
                returnList.append("haval-224-3")
                returnList.append("haval-224-4")
                returnList.append("haval-224-5")
                returnList.append("haval-256-3")
                returnList.append("haval-256-4")
                returnList.append("haval-256-5")
            elif "tiger" == algorithmName:
                returnList.append("tiger-128")
                returnList.append("tiger-160")
                returnList.append("tiger-192")
                returnList.append("tiger2")
            else:
                returnList.append(algorithmName)
        return returnList

    @staticmethod
    def createAlgorithms(algorithmNames):
        """Creates objects that implement the named algorithms.
        
        algorithmNames is expected to be a list of algorithm names. Each name is
        examined whether it is an alias, and, if it is, the alias is replaced by
        the real algorithm names that it refers to.

        Once all aliases have been resolved, instances of those algorithm
        classes that implement the named algorithms are created. The resulting
        algorithm objects register themselves with the AlgorithmRegistry
        singleton from where they can later be retrieved to perform hashing and
        other operations.

        This method returns a list of algorithm names for which objects were
        created. The list contains no aliases.
        """

        algorithmNames = AlgorithmFactory.resolveAliases(algorithmNames)
        # TODO: Check for names that appear multiple times and raise an
        # appropriate error. The current behaviour is that the registry
        # complains about algorithms registering multiple times, which might
        # confuse the user.
        for algorithmName in algorithmNames:
            if "base64" == algorithmName:
                Base64Algorithm()
            elif "md5" == algorithmName:
                MD5Algorithm()
            elif "sha-1" == algorithmName:
                SHA1Algorithm()
            elif "sha-224" == algorithmName:
                SHA224Algorithm()
            elif "sha-256" == algorithmName:
                SHA256Algorithm()
            elif "sha-384" == algorithmName:
                SHA384Algorithm()
            elif "sha-512" == algorithmName:
                SHA512Algorithm()
            elif OpenSSLAlgorithm.supportsAlgorithm(algorithmName):
                OpenSSLAlgorithm(algorithmName)
            else:
                # TODO: Check for not-yet-implemented algorithms.
                raise MKRoestiError("Unknown algorithm " + algorithmName)
        return algorithmNames
