import sys
from subprocess import Popen, PIPE
from os.path import join



def call_conda(prefix, extra_args):
    # call conda with the list of extra arguments, and return the tuple
    # stdout, stderr
    if sys.platform == 'win32':
        python = join(prefix, 'python.exe')
        conda = join(prefix, 'Scripts', 'conda-script.py')
    else:
        python = join(prefix, 'bin/python')
        conda = join(prefix, 'bin/conda')

    args = [python, conda] + extra_args
    try:
        p = Popen(args, stdout=PIPE, stderr=PIPE)
    except OSError:
        sys.exit("Error: could not invoke %r\n" % args)
    return p.communicate()
