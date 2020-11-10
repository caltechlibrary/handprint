'''
exit_codes.py: define exit codes for program return values

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2020 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from aenum import Enum, MultiValue

# I adapted the clever approach posted by the author of the Python aenum
# package, Ethan Furman, to Stack Overflow on 2016-03-13 at
# https://stackoverflow.com/a/35964875/743730
# The most important bit is realizing you can define __int__().

class ExitCode(Enum):
    '''Class of exit codes that this program may return.

    The numeric value of a given code can be obtained by using int().  For
    example, int(ExitCode.success) will produce 0.
    '''

    _init_ = 'value meaning'
    _settings_ = MultiValue

    success        = 0, "success -- program completed normally"
    user_interrupt = 1, "the user interrupted the program's execution"
    bad_arg        = 2, "encountered a bad or missing value for an option"
    no_network     = 3, "no network detected -- cannot proceed"
    file_error     = 4, "file error -- encountered a problem with a file or directory"
    server_error   = 5, "server error -- encountered a problem with the server"
    exception      = 6, "an exception or fatal error occurred"

    def __int__(self):
        return self.value
