'''
cpus.py: find out about CPUS on the host computer

Authors
-------

Michael Hucka <mhucka@caltech.edu> -- Caltech Library

Copyright
---------

Copyright (c) 2019 by the California Institute of Technology.  This code is
open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import os
import re
import subprocess

from handprint.debug import log


# Main functions.
# .............................................................................

# The following function was originally obtained on 2019-01-20 from a posting
# by user "phihag" to https://stackoverflow.com/a/1006301/743730/.
# Code posted to Stack Overflow falls under the CC BY-SA 4.0 (International).
# Subsequent modifications were made here by the author of this file.

def available_cpus():
    '''Number of available virtual or physical CPUs on this system, taking into
    account possible limitations set for this process (e.g., via cpuset).
    '''

    # cpuset may restrict the number of *available* processors.
    try:
        if __debug__: log('trying /proc/self/status to get CPU count')
        m = re.search(r'(?m)^Cpus_allowed:\s*(.*)$',
                      open('/proc/self/status').read())
        if m:
            res = bin(int(m.group(1).replace(',', ''), 16)).count('1')
            if res > 0:
                return res
    except IOError:
        pass

    # Python 2.6+
    try:
        import multiprocessing
        if __debug__: log('trying multiprocessing package to get CPU count')
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        pass

    # https://github.com/giampaolo/psutil
    try:
        import psutil
        if __debug__: log('trying psutil to get CPU count')
        return psutil.cpu_count()   # psutil.NUM_CPUS on old versions
    except (ImportError, AttributeError):
        pass

    # POSIX
    try:
        if __debug__: log('trying SC_NPROCESSORS_ONLN to get CPU count')
        res = int(os.sysconf('SC_NPROCESSORS_ONLN'))
        if res > 0:
            return res
    except (AttributeError, ValueError):
        pass

    # Windows
    try:
        res = int(os.environ['NUMBER_OF_PROCESSORS'])
        if __debug__: log('trying NUMBER_OF_PROCESSORS to get CPU count')
        if res > 0:
            return res
    except (KeyError, ValueError):
        pass

    # jython
    try:
        if __debug__: log('trying Jython getRuntime() to get CPU count')
        from java.lang import Runtime
        runtime = Runtime.getRuntime()
        res = runtime.availableProcessors()
        if res > 0:
            return res
    except ImportError:
        pass

    # BSD
    try:
        if __debug__: log('trying sysctl to get CPU count')
        sysctl = subprocess.Popen(['sysctl', '-n', 'hw.ncpu'],
                                  stdout = subprocess.PIPE)
        scStdout = sysctl.communicate()[0]
        res = int(scStdout)
        if res > 0:
            return res
    except (OSError, ValueError):
        pass

    # Linux
    try:
        if __debug__: log('trying /proc/cpuinfo to get CPU count')
        res = open('/proc/cpuinfo').read().count('processor\t:')
        if res > 0:
            return res
    except IOError:
        pass

    # Solaris
    try:
        if __debug__: log('trying /devices/pseudo to get CPU count')
        pseudoDevices = os.listdir('/devices/pseudo/')
        res = 0
        for pd in pseudoDevices:
            if re.match(r'^cpuid@[0-9]+$', pd):
                res += 1
        if res > 0:
            return res
    except OSError:
        pass

    # Other UNIXes (heuristic)
    try:
        try:
            if __debug__: log('trying /var/run/dmesg.boot to get CPU count')
            dmesg = open('/var/run/dmesg.boot').read()
        except IOError:
            dmesgProcess = subprocess.Popen(['dmesg'], stdout=subprocess.PIPE)
            dmesg = dmesgProcess.communicate()[0]

        res = 0
        while '\ncpu' + str(res) + ':' in dmesg:
            res += 1
        if res > 0:
            return res
    except OSError:
        pass

    return 1
