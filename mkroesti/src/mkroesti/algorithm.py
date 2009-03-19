"""Contains the AlgorithmInterface and AbstractAlgorithm classes, as well as
a couple of concrete algorithm implementations.

Algorithm classes *must* implement AlgorithmInterface. See that class'
documentation for details. To contribute to the system, one or more algorithm
provider classes must instantiate the concrete algorithm class. See the
documentation of mkroesti.provider.ProviderInterface for details.

AbstractAlgorithm derives from AlgorithmInterface. It is a base class that
concrete algorithm classes may inherit from. It requires that algorithm name
and provider be specified on construction, which allows it to implement
getters for these attributes.
"""


# PSL
import base64
import crypt
import hashlib
from random import randint
import string
import zlib

# Third party
availableModules = list()
try:
    import smbpasswd
    availableModules.append("smbpasswd")
except ImportError:
    pass
try:
    import mhash
    availableModules.append("mhash")
except ImportError:
    pass
try:
    import bcrypt
    availableModules.append("bcrypt")
except ImportError:
    pass

# mkroesti
from mkroesti.errorhandling import MKRoestiError
from mkroesti.names import *


class AlgorithmInterface:
    """Interface that must be implemented by algorithm classes."""

    def getName(self):
        """Returns a string that is the name of the algorithm."""
        raise NotImplementedError

    def getProvider(self):
        """Returns the provider that created the instance of the algorithm class."""
        raise NotImplementedError

    def getHash(self, input):
        """Returns a string that is the result of the algorithm hashing input."""
        raise NotImplementedError


class AbstractAlgorithm(AlgorithmInterface):
    """Abstract base class that implements common features of algorithm classes."""

    def __init__(self, name, provider):
        self.name = name
        self.provider = provider

    def getName(self):
        return self.name

    def getProvider(self):
        return self.provider

    def getHash(self, input):
        """Raises mkroesti.errorhandling.MKRoestiError."""
        raise MKRoestiError("Unknown algorithm " + self.getName())


class HashlibAlgorithms(AbstractAlgorithm):
    """Implements all algorithms available from the Python Standard Library
    module hashlib.
    """

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_MD5 == algorithmName:
            algorithm = hashlib.md5()
        elif ALGORITHM_SHA_1 == algorithmName:
            algorithm = hashlib.sha1()
        elif ALGORITHM_SHA_224 == algorithmName:
            algorithm = hashlib.sha224()
        elif ALGORITHM_SHA_256 == algorithmName:
            algorithm = hashlib.sha256()
        elif ALGORITHM_SHA_384 == algorithmName:
            algorithm = hashlib.sha384()
        elif ALGORITHM_SHA_512 == algorithmName:
            algorithm = hashlib.sha512()
        else:
            opensslAlgorithmName = HashlibAlgorithms.mapAlgorithmName(algorithmName)
            if opensslAlgorithmName is not None:
                algorithm = hashlib.new(opensslAlgorithmName)
            else:
                return AbstractAlgorithm.getHash(self, input)
        algorithm.update(input)
        return algorithm.hexdigest()

    @staticmethod
    def mapAlgorithmName(algorithmName):
        """Maps an algorithm name defined by mkroesti into a name known by OpenSSL."""
        if ALGORITHM_RIPEMD_160 == algorithmName:
           return "rmd160"
        elif ALGORITHM_SHA_0 == algorithmName:
           return "sha"
        elif ALGORITHM_MD2 == algorithmName or \
             ALGORITHM_MD4 == algorithmName:
           return algorithmName
        else:
           return None


class Base64Algorithms(AbstractAlgorithm):
    """Implements all algorithms available from the Python Standard Library
    module base64.
    """

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_BASE16 == algorithmName:
            return base64.b16encode(input)
        elif ALGORITHM_BASE32 == algorithmName:
            return base64.b32encode(input)
        elif ALGORITHM_BASE64 == algorithmName:
            return base64.b64encode(input)
        else:
            return AbstractAlgorithm.getHash(self, input)


class ZlibAlgorithms(AbstractAlgorithm):
    """Implements all algorithms available from the Python Standard Library
    module zlib.
    """

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_ADLER32 == algorithmName:
            # TODO should return an unsigned hex value
            return zlib.adler32(input)
        elif ALGORITHM_CRC32 == algorithmName:
            # TODO should return an unsigned hex value
            return zlib.crc32(input)
        else:
            return AbstractAlgorithm.getHash(self, input)


class CryptAlgorithm(AbstractAlgorithm):
    salt_chars = './' + string.ascii_letters + string.digits

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def getHash(self, input):
        if ALGORITHM_CRYPT_SYSTEM != self.getName():
            return AbstractAlgorithm.getHash(self, input)
        # As described in the docs of the crypt module:
        #   salt is usually a random two-character string which will be used
        #   to perturb the DES algorithm in one of 4096 ways. The characters
        #   in salt must be in the set [./a-zA-Z0-9].
        # The following implementation of generating the salt is taken verbatim
        # (with the exception of fixing a typo) from this mailing list post:
        #   http://mail.python.org/pipermail/python-list/2004-March/252058.html
        # os.urandom() would be better than randint() because it is explicitly
        # suitable for cryptographic use, but as the mailing list post points
        # out:
        #   [...] we don't need cryptographically strong random numbers. No
        #   attack on crypt() depends on guessing the salt, the salt is in
        #   the output anyway.
	salt = CryptAlgorithm.salt_chars[randint(0, 63)] + CryptAlgorithm.salt_chars[randint(0, 63)]
        return crypt.crypt(input, salt)


class CryptBlowfishAlgorithm(AbstractAlgorithm):
    @staticmethod
    def isAvailable():
        moduleName = "bcrypt"
        isAvailable = moduleName in availableModules
        return (isAvailable, moduleName)

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def getHash(self, input):
        if ALGORITHM_CRYPT_BLOWFISH != self.getName():
            return AbstractAlgorithm.getHash(self, input)
        salt = bcrypt.gensalt()   # default value for log_rounds parameter = 12
        return bcrypt.hashpw(input, salt)


class WindowsHashAlgorithms(AbstractAlgorithm):
    """Implements Windows LanManager and NT password hashes."""

    @staticmethod
    def isAvailable():
        moduleName = "smbpasswd"
        isAvailable = moduleName in availableModules
        return (isAvailable, moduleName)

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_WINDOWS_LM == algorithmName:
            return smbpasswd.lmhash(input)
        elif ALGORITHM_WINDOWS_NT == algorithmName:
            return smbpasswd.nthash(input)
        else:
            return AbstractAlgorithm.getHash(self, input)

class MHashAlgorithms(AbstractAlgorithm):
    """Implements all algorithms available from the third party module mhash."""

    @staticmethod
    def isAvailable():
        moduleName = "mhash"
        isAvailable = moduleName in availableModules
        return (isAvailable, moduleName)

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def getHash(self, input):
        mhashAlgorithmName = MHashAlgorithms.mapAlgorithmName(self.getName())
	if mhashAlgorithmName is None:
            return AbstractAlgorithm.getHash(self, input)
        algorithm = mhash.MHASH(mhashAlgorithmName)
        algorithm.update(input)
        return algorithm.hexdigest()

    @staticmethod
    def mapAlgorithmName(algorithmName):
        """Maps an algorithm name defined by mkroesti into a name known by mhash."""
        if ALGORITHM_SHA_1 == algorithmName:
           return mhash.MHASH_SHA1
        elif ALGORITHM_SHA_224 == algorithmName:
           return mhash.MHASH_SHA224
        elif ALGORITHM_SHA_256 == algorithmName:
           return mhash.MHASH_SHA256
        elif ALGORITHM_SHA_384 == algorithmName:
           return mhash.MHASH_SHA384
        elif ALGORITHM_SHA_512 == algorithmName:
           return mhash.MHASH_SHA512
        elif ALGORITHM_RIPEMD_128 == algorithmName:
           return mhash.MHASH_RIPEMD128
        elif ALGORITHM_RIPEMD_160 == algorithmName:
           return mhash.MHASH_RIPEMD160
        elif ALGORITHM_RIPEMD_256 == algorithmName:
           return mhash.MHASH_RIPEMD256
        elif ALGORITHM_RIPEMD_320 == algorithmName:
           return mhash.MHASH_RIPEMD320
        elif ALGORITHM_HAVAL_128_3 == algorithmName:
           return mhash.MHASH_HAVAL128
        elif ALGORITHM_HAVAL_160_3 == algorithmName:
           return mhash.MHASH_HAVAL160
        elif ALGORITHM_HAVAL_192_3 == algorithmName:
           return mhash.MHASH_HAVAL192
        elif ALGORITHM_HAVAL_224_3 == algorithmName:
           return mhash.MHASH_HAVAL224
        elif ALGORITHM_HAVAL_256_3 == algorithmName:
           return mhash.MHASH_HAVAL256
        elif ALGORITHM_SNEFRU_128 == algorithmName:
           return mhash.MHASH_SNEFRU128
        elif ALGORITHM_SNEFRU_256 == algorithmName:
           return mhash.MHASH_SNEFRU256
        elif ALGORITHM_TIGER_128 == algorithmName:
           return mhash.MHASH_TIGER128
        elif ALGORITHM_TIGER_160 == algorithmName:
           return mhash.MHASH_TIGER160
        elif ALGORITHM_TIGER_192 == algorithmName:
           return mhash.MHASH_TIGER
        elif ALGORITHM_WHIRLPOOL == algorithmName:
           return mhash.MHASH_WHIRLPOOL
        elif ALGORITHM_GOST == algorithmName:
           return mhash.MHASH_GOST
        elif ALGORITHM_ADLER32 == algorithmName:
           return mhash.MHASH_ADLER32
        elif ALGORITHM_CRC32 == algorithmName:
           return mhash.MHASH_CRC32
        elif ALGORITHM_CRC32B == algorithmName:
           return mhash.MHASH_CRC32B
        elif ALGORITHM_MD2 == algorithmName:
           return mhash.MHASH_MD2
        elif ALGORITHM_MD4 == algorithmName:
           return mhash.MHASH_MD4
        elif ALGORITHM_MD5 == algorithmName:
           return mhash.MHASH_MD5
        else:
           return None

