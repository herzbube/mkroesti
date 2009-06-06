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


"""Contains the AlgorithmInterface and AbstractAlgorithm classes, as well as
a couple of concrete algorithm implementations.

Algorithm classes *must* implement AlgorithmInterface (although they do not
need to inherit from it). See the class' documentation for details. To
contribute to the system, one or more algorithm provider classes must 
instantiate the concrete algorithm class. See the documentation of
mkroesti.provider.ProviderInterface for details.

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
try:
    import aprmd5
    availableModules.append("aprmd5")
except ImportError:
    pass

# mkroesti
from mkroesti.names import * #@UnusedWildImport
import mkroesti   # import stuff from __init__.py (e.g. mkroesti.python2)


class AlgorithmInterface:
    """Interface that must be implemented by algorithm classes.

    The main purpose of the class AlgorithmInterface is to document the
    interface. In the spirit of duck typing, a concrete algorithm class is not
    required to inherit from AlgorithmInterface (although it automatically does
    if it inherits from AbstractAlgorithm). 
    """

    def getName(self):
        """Returns a string that is the name of the algorithm."""
        raise NotImplementedError

    def getProvider(self):
        """Returns the provider that created the instance of the algorithm class."""
        raise NotImplementedError

    def needBytesInput(self):
        """Returns True if getHash() requires input to be of type bytes, False
        if it requires input to be of type str.

        If this program is run in versions prior to Python 3, this function will
        never be called and the input to getHash() will always be of type str.
        """
        raise NotImplementedError
        
    def getHash(self, input):
        """Returns a string that is the result of the algorithm hashing input.

        If this program is run in Python 3, the type of input (str or bytes) is
        determined by the return value of needBytesInput(). If this program is
        run in versions prior to Python 3, the type of input will always be str
        (because in versions prior to Python 3 the string data type is used to
        represent arrays of bytes).
        """
        raise NotImplementedError


class AbstractAlgorithm(AlgorithmInterface):
    """Abstract base class that implements common features of algorithm classes."""

    def __init__(self, name = None, provider = None):
        self.name = name
        self.provider = provider

    def getName(self):
        """This default implementation returns the name specified on construction."""
        return self.name

    def getProvider(self):
        """This default implementation returns the provider specified on construction."""
        return self.provider


class HashlibAlgorithms(AbstractAlgorithm):
    """Implements all algorithms available from the Python Standard Library
    module hashlib.
    """

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def needBytesInput(self):
        return True

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

    def needBytesInput(self):
        return True

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_BASE16 == algorithmName:
            result = base64.b16encode(input)
            if mkroesti.python2:
                return result
            else:
                return result.decode("ascii")
        elif ALGORITHM_BASE32 == algorithmName:
            result = base64.b32encode(input)
            if mkroesti.python2:
                return result
            else:
                return result.decode("ascii")
        elif ALGORITHM_BASE64 == algorithmName:
            result = base64.b64encode(input)
            if mkroesti.python2:
                return result
            else:
                return result.decode("ascii")
        else:
            return AbstractAlgorithm.getHash(self, input)


class ZlibAlgorithms(AbstractAlgorithm):
    """Implements all algorithms available from the Python Standard Library
    module zlib.
    """

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def needBytesInput(self):
        return True

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_ADLER32 == algorithmName or ALGORITHM_CRC32 == algorithmName:
            if ALGORITHM_ADLER32 == algorithmName:
                result = zlib.adler32(input)
            elif ALGORITHM_CRC32 == algorithmName:
                result = zlib.crc32(input)
            # Python 2: Result for both algorithms is in the range
            # [-2**31, 2**31-1], the &= operation makes it unsigned  and in the
            # range [0, 2**32-1] (same as in Python 3).
            if mkroesti.python2:
                result &= 0xffffffff
            # Convert decimal into hexadecimal value, and remove the "0x" prefix
            result = hex(result)[2:]
            # Python 2: Because result stores a long value, its string
            # representation has an "L" suffix. hex() does not strip that
            # suffix, so we have to do the stripping ourselves
            if mkroesti.python2:
                return result[:-1]
            return result
        else:
            return AbstractAlgorithm.getHash(self, input)


class CryptAlgorithm(AbstractAlgorithm):
    """Implements all crypt-based algorithms that can be accessed using the
    system's crypt(3) routine.

    Which algorithms are available from this class entirely depends on the
    implementation of the system's crypt(3) routine. The crypt-des algorithm
    should always be available. On any system with a reasonably modern glibc,
    at least crypt-md5 should be available. On a Debian 5.0.1 (lenny) system,
    crypt-sha-256 and crypt-sha-512 are also available.

    getHash() will blithely try to generate a hash for any one of the algorithms
    supported by this class, even if the algorithm is not available from the
    sytem's crypt(3) routine. The resulting hash will probably be a crypt-des
    hash, although this cannot be guaranteed and entirely depends on the
    behaviour of the system's crypt(3).

    The proper approach is to first call the static method isAvailable() to find
    out whether the desired algorithm is available. Only if isAvailable()
    returns True should you instantiate a CryptAlgorithm object and call its
    getHash() method.
    """

    salt_chars = './' + string.ascii_letters + string.digits
    availableAlgorithms = None

    @staticmethod
    def isAvailable(algorithmName):
        if CryptAlgorithm.availableAlgorithms is None:
            CryptAlgorithm.availableAlgorithms = list()
            # The basic crypt-des algorithm is always available
            CryptAlgorithm.availableAlgorithms.append(ALGORITHM_CRYPT_DES)
            # Each of the optional algorithms is available if we can generate a
            # hash that starts with the expected signature (e.g. "$1$")
            cryptAlgorithmDictionary = {ALGORITHM_CRYPT_MD5 : "$1$",
                                        ALGORITHM_CRYPT_SHA_256 : "$5$",
                                        ALGORITHM_CRYPT_SHA_256 : "$6$"
                                        }
            for (cryptAlgorithmName, signature) in cryptAlgorithmDictionary.items():
                cryptAlgorithmObject = CryptAlgorithm(cryptAlgorithmName, None)
                hash = cryptAlgorithmObject.getHash("foo")
                if hash[:len(signature)] == signature:
                    CryptAlgorithm.availableAlgorithms.append(cryptAlgorithmName)
        return (algorithmName in CryptAlgorithm.availableAlgorithms)

    @staticmethod
    def getSalt(length):
        # As described in the docs of the crypt module:
        #   salt is usually a random two-character string which will be used
        #   to perturb the DES algorithm in one of 4096 ways. The characters
        #   in salt must be in the set [./a-zA-Z0-9].
        # The following implementation of generating the salt is a modified
        # version of the code presented in this mailing list post (modification
        # includes fixing a typo :-):
        #   http://mail.python.org/pipermail/python-list/2004-March/252058.html
        # os.urandom() would be better than randint() because it is explicitly
        # suitable for cryptographic use, but as the mailing list post points
        # out:
        #   [...] we don't need cryptographically strong random numbers. No
        #   attack on crypt() depends on guessing the salt, the salt is in
        #   the output anyway.
        salt = ""
        while length > 0:
            salt += CryptAlgorithm.salt_chars[randint(0, 63)]
            length -= 1
        return salt

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def needBytesInput(self):
        return False

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_CRYPT_DES == algorithmName:
            return crypt.crypt(input, CryptAlgorithm.getSalt(2))
        elif ALGORITHM_CRYPT_MD5 == algorithmName:
            # We select the MD5-based algorithm by passing in a salt that starts
            # with "$1". From the glibc manual:
            #   For the MD5-based algorithm, the salt should consist of the
            #   string $1$, followed by up to 8 characters, terminated by
            #   either another $ or the end of the string. The result of crypt
            #   will be the salt, followed by a $ if the salt didn't end with
            #   one, followed by 22 characters from the alphabet ./0-9A-Za-z,
            #   up to 34 characters total. Every character in the key is
            #   significant.
            salt = "$1$" + CryptAlgorithm.getSalt(8) + "$"
            return crypt.crypt(input, salt)
        elif ALGORITHM_CRYPT_SHA_256 == algorithmName:
            # I have found experimentally that signature $5$ selects the crypt
            # algorithm based on SHA-256. Also by experiment, I have found that
            # the salt may consist of up to 16 characters.
            salt = "$5$" + CryptAlgorithm.getSalt(16) + "$"
            return crypt.crypt(input, salt)
        elif ALGORITHM_CRYPT_SHA_512 == algorithmName:
            # SHA-512 details also found out experimentally.
            salt = "$6$" + CryptAlgorithm.getSalt(16) + "$"
            return crypt.crypt(input, salt)
        else:
            return AbstractAlgorithm.getHash(self, input)


class CryptBlowfishAlgorithm(AbstractAlgorithm):
    """Implements the crypt-blowfish algorithm."""

    @staticmethod
    def isAvailable():
        moduleName = "bcrypt"
        isAvailable = moduleName in availableModules
        return (isAvailable, moduleName)

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def needBytesInput(self):
        return True

    def getHash(self, input):
        if ALGORITHM_CRYPT_BLOWFISH != self.getName():
            return AbstractAlgorithm.getHash(self, input)
        salt = bcrypt.gensalt()   # default value for log_rounds parameter = 12
        return bcrypt.hashpw(input, salt)


class WindowsHashAlgorithms(AbstractAlgorithm):
    """Implements the windows-lm and windows-nt algorithms."""

    @staticmethod
    def isAvailable():
        moduleName = "smbpasswd"
        isAvailable = moduleName in availableModules
        return (isAvailable, moduleName)

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def needBytesInput(self):
        return True

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

    def needBytesInput(self):
        return True

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
            return mhash.MHASH_SHA224 #@IndentOk
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

class AprMD5Algorithms(AbstractAlgorithm):
    """Implements all algorithms available from the third party module aprmd5."""

    @staticmethod
    def isAvailable():
        moduleName = "aprmd5"
        isAvailable = moduleName in availableModules
        return (isAvailable, moduleName)

    def __init__(self, algorithmName, provider):
        AbstractAlgorithm.__init__(self, algorithmName, provider)

    def needBytesInput(self):
        algorithmName = self.getName()
        if ALGORITHM_MD5 == algorithmName:
            return True
        elif ALGORITHM_CRYPT_APR1 == algorithmName:
            return False
        else:
            return AbstractAlgorithm.needBytesInput(self)

    def getHash(self, input):
        algorithmName = self.getName()
        if ALGORITHM_MD5 == algorithmName:
            return aprmd5.md5(input)
        elif ALGORITHM_CRYPT_APR1 == algorithmName:
            # Use an 8-character salt to mimick the behavior of the htpasswd
            # command line tool. For details about salt construction, see the
            # comments in CryptAlgorithm.
            salt = str()
            for i in range(8): #@UnusedVariable
                salt += CryptAlgorithm.salt_chars[randint(0, 63)]
            return aprmd5.md5_encode(input, salt)
        else:
            return AbstractAlgorithm.getHash(self, input)

