import re
import os
import sys
from subprocess import Popen, PIPE
from os.path import isdir, join


ROOT_PREFIX = '/opt/anaconda'


def _call_conda(extra_args):
    # call conda with the list of extra arguments, and return the tuple
    # stdout, stderr
    if sys.platform == 'win32':
        python = join(ROOT_PREFIX, 'python.exe')
        conda = join(ROOT_PREFIX, 'Scripts', 'conda-script.py')
    else:
        python = join(ROOT_PREFIX, 'bin/python')
        conda = join(ROOT_PREFIX, 'bin/conda')

    args = [python, conda] + extra_args
    try:
        p = Popen(args, stdout=PIPE, stderr=PIPE)
    except OSError:
        sys.exit("Error: could not invoke %r\n" % args)
    return p.communicate()


def set_root_prefix(prefix):
    """
    set the prefix to the root environment (default is /opt/anaconda)
    """
    global ROOT_PREFIX
    ROOT_PREFIX = prefix


def get_conda_version():
    """
    return the version of conda being used as a string
    """
    pat = re.compile(r'conda:?\s+(\d\.\d\S+)')
    stdout, stderr = _call_conda(['--version'])
    m = pat.match(stderr.strip())
    if m is None:
        raise Exception('output did not match: %r' % stderr)
    return m.group(1)


def get_envs():
    """
    return all of the (named) environment (this does not include the root
    environment), as a set of absolute path to their prefixes
    """
    res = set()
    envs_dir = join(ROOT_PREFIX, 'envs')
    for fn in os.listdir(envs_dir):
        path = join(envs_dir, fn)
        if isdir(path):
            res.add(join(path, fn))
    return res


def linked(prefix):
    """
    Return the (set of canonical names) of linked packages in prefix.
    """
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        return set()
    return set(fn[:-5] for fn in os.listdir(meta_dir) if fn.endswith('.json'))


if __name__ == '__main__':
    set_root_prefix('/Users/ilan/python')
    print repr(get_conda_version())
    print get_envs()
