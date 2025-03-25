## Summary

`mkroesti` is a hash generator written in Python.

`mkroesti` can be used both as a command line utility and as a web tool. It takes an input (e.g. a file, or a password) and generates different kinds of hashes from that input. The hashes to generate are selected by naming them on the command line, or ticking the corresponding checkboxes in the web GUI.

`mkroesti` provides no hash algorithm implementations of its own. Instead it consists of a collection of front-ends to hash algorithms available in the Python Standard Library, and from a number of third-party modules. See the section [Dependencies](#Dependencies) for details.

`mkroesti` also defines a couple of interfaces that allow third parties to inject new front-ends to previously unavailable hash algorithms. For more information on how this extension mechanism works, please read the section "How to extend mkroesti" in the `README` file.

## License

`mkroesti` is released under the [GNU General Public License](http://www.gnu.org/copyleft/gpl.html) (GPLv3).

## Installation instructions

The tar balls that can be downloaded under ["Releases" on the project page](https://github.com/herzbube/mkroesti/releases) have been created using the Distutils Python module. In the terminology of Distutils, the tar ball is a so-called "source distribution". Read the file INSTALL inside the tar ball for more details.

[This page on my wiki](https://wiki.herzbube.ch/wiki/Mkroesti) also has step-by-step instructions how to install `mkroesti` on a Debian system.

## Bugs and source code

If you want to report a bug, please use the project's [issue tracker on GitHub](https://github.com/herzbube/mkroesti/issues).

The source code for `mkroesti` is maintained in [this Git repository](https://github.com/herzbube/mkroesti#), also on GitHub.

## Python versions

The minimum requirement for running a current version of `mkroesti` is Python 2.6 (tests were made with Python 2.6.2). It should also run fine with Python 3.

## Dependencies

This section documents which modules provide hash algorithms for `mkroesti`.

- The Python Standard Library ([external link](https://docs.python.org/3/library/crypto.html)) provides the following hashes:
  - `hashlib` module, always: md5, sha-1, sha-224, sha-256, sha-384, sha-512
  - `hashlib` module, depending on the version of the underlying OpenSSL: ripemd-160, sha-0, md2, md4
  - `base64` module: base16, base32, base64
  - `crypt` module: the system's crypt() function
- The module `smbpasswd` ([external link](https://github.com/barryp/py-smbpasswd/)) provides the following hashes:
  - windows-lm, windows-nt
- The module `mhash` ([external link](https://labix.org/python-mhash)) provides the following hashes:
  - haval-128, haval-160, haval-192, haval-224, haval-256 (3 rounds variant), ripemd-128, ripemd-256, ripemd-320, tiger-128, tiger-160, tiger-192, whirlpool, snefru-128, snefru-256, gost
- The module `bcrypt` ([external link](https://code.google.com/archive/p/py-bcrypt/)) provides the following hashes:
  - crypt-blowfish
- The module `aprmd5` ([external link](https://github.com/herzbube/python-aprmd5)) provides the following hashes:
  - crypt-apr1

