#!/usr/bin/env python3
# =============================================================================
# @file    create-pyz
# @brief   Script to create Handprint executable zipapps using shiv
# @created 2021-06-25
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/handprint
#
# Preliminary setup (on macOS) assumed to have been done before this is run:
#   brew install python@3.8
#   brew install python@3.9
#   brew install pyenv
#   pyenv install 3.9.0  3.9.1  3.9.5
#   pyenv install 3.8.0  3.8.1  3.8.2  3.8.10
# =============================================================================

from   fastnumbers import isint
import pkg_resources
from   os import getcwd, chdir, system
from   os.path import exists, dirname, join, basename
from   rich.console import Console
import subprocess
from   subprocess import check_output, check_call
import sys
from   sys import exit


# Constants used later.
# .............................................................................

_HASHBANG = '/usr/bin/env python3 -X importtime'

_ENTRY_POINT = 'handprint.__main__:console_scripts_main'

_PREAMBLE = '''#!/usr/bin/env -i bash --noprofile --norc
[[ -e ~/.shiv/handprint-{0}-msg ]] || echo "Performing a one-time setup operation -- please be patient ..."
touch ~/.shiv/handprint-{0}-msg
'''


# Utility functions used below.
# .............................................................................

def run(cmd, quiet = False):
    if quiet:
        return check_output(cmd, shell = True).decode()
    else:
        return check_call(cmd, shell = True,
                          stdout = sys.stdout, stderr = subprocess.STDOUT)

def quit(msg):
    print(f'‼️  {msg}', flush = True)
    exit(1)


def inform(text):
    Console().print(text, style = "cyan")


# Sanity-check the run-time environment before attempting anything else.
# .............................................................................

here  = getcwd()
if not exists(join(here, 'requirements.txt')):
    quit(f'Expected to be in same directory as requirements.txt')

setup_file = join(here, 'setup.cfg')
if not exists(setup_file):
    quit(f'__init__.py does not exist in {setup_file}')

if len(sys.argv) < 2:
    quit(f'First argument must be destination where outputs will be written')

dest = sys.argv[1]
if not exists(dest):
    quit(f'Directory does not exist: {dest}')

if len(sys.argv) < 3:
    quit(f'Second argument must be the target Python version')

py_version = sys.argv[2]
if len(py_version.split('.')) < 3 or not all(isint(x) for x in py_version.split('.')):
    quit(f'Python version must be in the form x.y.z')

known_versions = [s.strip() for s in run('pyenv versions', True).split('\n')]
if py_version not in known_versions:
    quit(f'pyenv lacks version {py_version} -- run "pyenv install {py_version}"')


# Gather information.
# .............................................................................

short_version = '.'.join(py_version.split('.')[0:2])

with open('setup.cfg', 'r') as config_file:
    for line in config_file.readlines():
        if line.startswith('version'):
            h_version = line.split('=')[1].strip()

os      = run("uname -s | tr '[A-Z]' '[a-z]'", True)
outdir  = join(dest, f'handprint-{h_version}-python{py_version}')
outname = f'handprint'


# Do the work.
# .............................................................................

inform(f'Creating output directory in {outdir}')
run(f'rm -rf {outdir}')
run(f'mkdir -p {outdir}')
chdir(outdir)

with open('preamble.sh', 'w') as out:
    out.write(_PREAMBLE.format(h_version))
run('chmod +x preamble.sh')

inform(f'Setting up pyenv local environment')
run(f'pyenv local {py_version}')
run(f'~/.pyenv/shims/pip install shiv --upgrade')

inform(f'Building output with shiv')
run(f'~/.pyenv/shims/shiv -p "{_HASHBANG}" -e "{_ENTRY_POINT}" -o "{outname}" '
    + f'--preamble preamble.sh --prefer-binary handprint=={h_version}')

inform(f'Cleaning up')
run(f'rm {outdir}/preamble.sh')

inform(f'Done; output is in {outdir}')
