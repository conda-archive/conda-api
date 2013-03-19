import re
import os
import sys
import json
from subprocess import Popen, PIPE
from os.path import isdir, join


__version__ = '1.0.0'

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


def _call_and_parse(extra_args):
    stdout, stderr = _call_conda(extra_args)
    if stderr.decode().strip():
        raise Exception('conda %r\n: BEGIN %s END' % (extra_args,
                                                      stderr.decode()))
    return json.loads(stdout.decode())


def set_root_prefix(prefix):
    """
    set the prefix to the root environment (default is /opt/anaconda)
    """
    global ROOT_PREFIX
    ROOT_PREFIX = prefix


def get_conda_version():
    """
    return the version of conda being used (invoked) as a string
    """
    pat = re.compile(r'conda:?\s+(\d+\.\d\S+)')
    stdout, stderr = _call_conda(['--version'])
    m = pat.match(stderr.decode().strip())
    if m is None:
        raise Exception('output did not match: %r' % stderr)
    return m.group(1)


def get_envs():
    """
    return all of the (named) environment (this does not include the root
    environment), as a list of absolute path to their prefixes
    """
    envs_dir = join(ROOT_PREFIX, 'envs')
    return [join(envs_dir, fn) for fn in os.listdir(envs_dir)
                  if isdir(join(envs_dir, fn))]


def linked(prefix):
    """
    return the (set of canonical names) of linked packages in prefix
    """
    if not isdir(prefix):
        raise Exception('no such directory: %r' % prefix)
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        # we might have nothing in linked (and no conda-meta directory)
        return set()
    return set(fn[:-5] for fn in os.listdir(meta_dir) if fn.endswith('.json'))


def split_canonical_name(cname):
    """
    split a canonical package name into (name, version, build) strings
    """
    return tuple(cname.rsplit('-', 2))


def share(prefix):
    """
    Create a "share package" of the environment located in `prefix`,
    and return the full path to the created package, as well as a list
    of warning, which might have occured while creating the package.
    This file is created in a temp directory, and it is the callers
    responsibility to remove this directory (after the file has been
    handled in some way).
    """
    d = _call_and_parse(['share', '--output-json', '--prefix', prefix])
    return d['path'], d['warnings']


def clone(path, prefix):
    """
    Clone the bundle (located at `path`) by creating a new environment at
    `prefix`.
    The directory `path` is located in should be some temp directory or
    some other directory OUTSITE /opt/anaconda (this function handles
    copying the of the file if necessary for you).  After calling this
    funtion, the original file (at `path`) may be removed.
    The return object is a list of warnings
    """
    return _call_and_parse(['clone', '--output-json',
                            '--prefix', prefix, path])


if __name__ == '__main__':
    set_root_prefix('/Users/ilan/python')
    print(repr(get_conda_version()))
    for prefix in get_envs():
        print(prefix)
        for dist in linked(prefix):
            print('\t' + dist)
    path, ws = share('/Users/ilan/python/envs/py3k')
    print ws
    ws = clone(path, '/Users/ilan/python/envs/clone7')
    print ws
