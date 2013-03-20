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
        raise Exception("could not invoke %r\n" % args)
    return p.communicate()


def _call_and_parse(extra_args):
    stdout, stderr = _call_conda(extra_args)
    if stderr.decode().strip():
        raise Exception('conda %r:\nSTDERR:\n%s\nEND' % (extra_args,
                                                         stderr.decode()))
    return json.loads(stdout.decode())


def set_root_prefix(prefix):
    """
    Set the prefix to the root environment (default is /opt/anaconda).
    This function should only be called once (right after importing conda_api).
    """
    global ROOT_PREFIX
    ROOT_PREFIX = prefix


def get_conda_version():
    """
    return the version of conda being used (invoked) as a string
    """
    pat = re.compile(r'conda:?\s+(\d+\.\d\S+|unknown)')
    stdout, stderr = _call_conda(['--version'])
    # for some reason argparse decided to output the version to stderr
    m = pat.match(stderr.decode().strip())
    if m is None:
        raise Exception('output did not match: %r' % stderr)
    return m.group(1)


def get_envs():
    """
    Return all of the (named) environment (this does not include the root
    environment), as a list of absolute path to their prefixes.
    """
    envs_dir = join(ROOT_PREFIX, 'envs')
    return [join(envs_dir, fn) for fn in os.listdir(envs_dir)
                  if isdir(join(envs_dir, fn))]


def linked(prefix):
    """
    Return the (set of canonical names) of linked packages in `prefix`.
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
    Split a canonical package name into (name, version, build) strings.
    """
    return tuple(cname.rsplit('-', 2))


def info():
    """
    Return a dictionary with configuration information.
    No guarantee is made about which keys exist.  Therefore this function
    should only be used for testing and debugging.
    """
    return _call_and_parse(['info', '--output-json'])


def share(prefix):
    """
    Create a "share package" of the environment located in `prefix`,
    and return the full path to the created package, as well as a list
    of warning, which might have occurred while creating the package.

    This file is created in a temp directory, and it is the callers
    responsibility to remove this directory (after the file has been
    handled in some way).
    """
    return _call_and_parse(['share', '--output-json', '--prefix', prefix])


def clone(path, prefix):
    """
    Clone a "share package" (located at `path`) by creating a new
    environment at `prefix`, and return a list of warnings.

    The directory `path` is located in, should be some temp directory or
    some other directory OUTSIDE /opt/anaconda.  After calling this
    function, the original file (at `path`) may be removed (by the caller
    of this function).
    The return object is a list of warnings.
    """
    return _call_and_parse(['clone', '--output-json',
                            '--prefix', prefix, path])


def test():
    """
    Self-test function, which prints useful debug information.
    This function returns None on success, and will crash the interpreter
    on failure.
    """
    print('sys.version: %r' % sys.version)
    print('sys.prefix : %r' % sys.prefix)
    print('conda_api.__version__: %r' % __version__)
    print('conda_api.ROOT_PREFIX: %r' % ROOT_PREFIX)
    if isdir(ROOT_PREFIX):
        conda_version = get_conda_version()
        print('conda version: %r' % conda_version)
        print('conda info:')
        d = info()
        for kv in d.items():
            print('\t%s=%r' % kv)
        assert d['conda_version'] == conda_version
    else:
        print('Warning: no such directory: %r' % ROOT_PREFIX)
    print('OK')


if __name__ == '__main__':
    from optparse import OptionParser

    p = OptionParser(usage="usage: %prog [options] [ROOT_PREFIX]",
                     description="self-test conda-api")
    opts, args = p.parse_args()
    if len(args) == 0:
        pass
    elif len(args) == 1:
        set_root_prefix(args[0])
    else:
        p.error('did not expect more than one argument, try -h')
    test()
