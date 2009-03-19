#!/usr/bin/env python
# encoding=utf-8

import mkroesti.main
import mkroesti.errorhandling

try:
    if __name__ == "__main__":
        mkroesti.main.main()
except mkroesti.errorhandling.MKRoestiError, (errorInstance):
    print "mkroesti.py: error: " + errorInstance.message
    exit(1)
