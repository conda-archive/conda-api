import re
import os
import sys
import json
from subprocess import Popen, PIPE
from os.path import basename, isdir, join


__version__ = '1.2.1'

class CondaError(Exception):
    "General Conda error"
    pass

class CondaEnvExistsError(Exception):
    "Conda environment already exists"
    pass

def _call_conda(extra_args, abspath=True):
    # call conda with the list of extra arguments, and return the tuple
    # stdout, stderr
    if abspath:
        if sys.platform == 'win32':
            python = join(ROOT_PREFIX, 'python.exe')
            conda  = join(ROOT_PREFIX, 'Scripts', 'conda-script.py')
        else:
            python = join(ROOT_PREFIX, 'bin/python')
            conda  = join(ROOT_PREFIX, 'bin/conda')
        cmd_list = [python, conda]
    else: # just use whatever conda is on the path
        cmd_list = ['conda']

    cmd_list.extend(extra_args)

    try:
        p = Popen(cmd_list, stdout=PIPE, stderr=PIPE)
    except OSError:
        raise Exception("could not invoke %r\n" % args)
    return p.communicate()


def _call_and_parse(extra_args, abspath=True):
    stdout, stderr = _call_conda(extra_args, abspath=abspath)
    if stderr.decode().strip():
        raise Exception('conda %r:\nSTDERR:\n%s\nEND' % (extra_args,
                                                         stderr.decode()))
    return json.loads(stdout.decode())


def set_root_prefix(prefix=None):
    """
    Set the prefix to the root environment (default is /opt/anaconda).
    This function should only be called once (right after importing conda_api).
    """
    global ROOT_PREFIX

    if prefix:
        ROOT_PREFIX = prefix
    else: # find *some* conda instance, and then use info() to get 'root_prefix'
        i = info(abspath=False)
        ROOT_PREFIX = i['root_prefix']
        '''
        plat = 'posix'
        if sys.platform.lower().startswith('win'):
            listsep = ';'
            plat = 'win'
        else:
            listsep = ':'

        for p in os.environ['PATH'].split(listsep):
            if (os.path.exists(os.path.join(p, 'conda')) or
                os.path.exists(os.path.join(p, 'conda.exe')) or
                os.path.exists(os.path.join(p, 'conda.bat'))):

                # TEMPORARY:
                ROOT_PREFIX = os.path.dirname(p) # root prefix is one directory up
                i = info()
                # REAL:
                ROOT_PREFIX = i['root_prefix']
                break
        else: # fall back to standard install location, which may be wrong
            if plat == 'win':
                ROOT_PREFIX = 'C:\Anaconda'
            else:
                ROOT_PREFIX = '/opt/anaconda'
        '''


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
    info = _call_and_parse(['info', '--json'])
    return info['envs']


def get_prefix_envname(name):
    """
    Given the name of an environment return its full prefix path, or None
    if it cannot be found.
    """
    if name == 'root':
        return ROOT_PREFIX
    for prefix in get_envs():
        if basename(prefix) == name:
            return prefix
    return None


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


def info(abspath=True):
    """
    Return a dictionary with configuration information.
    No guarantee is made about which keys exist.  Therefore this function
    should only be used for testing and debugging.
    """
    return _call_and_parse(['info', '--json'], abspath=abspath)


def share(prefix):
    """
    Create a "share package" of the environment located in `prefix`,
    and return a dictionary with (at least) the following keys:
      - 'path': the full path to the created package
      - 'warnings': a list of warnings

    This file is created in a temp directory, and it is the callers
    responsibility to remove this directory (after the file has been
    handled in some way).
    """
    return _call_and_parse(['share', '--json', '--prefix', prefix])


def create(name=None, path=None, pkgs=None):
    """
    Create an environment either by name or path with a specified set of
    packages
    """
    if not pkgs or not isinstance(pkgs, (list, tuple)):
        raise TypeError('must specify a list of one or more packages to '
                        'install into new environment')

    cmd_list = ['create', '--yes', '--quiet']
    if name:
        ref         = name
        search      = [os.path.join(d, name) for d in info()['envs_dirs']]
        cmd_list    = ['create', '--yes', '--quiet', '--name', name]
    elif path:
        ref         = path
        search      = [path]
        cmd_list    = ['create', '--yes', '--quiet', '--path', path]
    else:
        raise TypeError('must specify either an environment name or a path '
                        'for new environment')

    if any(os.path.exists(path) for path in search):
        raise CondaEnvExistsError('Conda environment [%s] already exists' % ref)

    cmd_list.extend(pkgs)
    (out, err) = _call_conda(cmd_list)
    if err.decode().strip():
        raise CondaError('conda %s: %s' % (" ".join(cmd_list), err.decode()))
    return out


def install(name=None, path=None, pkgs=None):
    """
    Install packages into an environment either by name or path with a
    specified set of packages
    """
    if not pkgs or not isinstance(pkgs, (list, tuple)):
        raise TypeError('must specify a list of one or more packages to '
                        'install into existing environment')

    cmd_list = ['install', '--yes', '--quiet']
    if name:
        cmd_list.extend(['--name', name])
    elif path:
        cmd_list.extend(['--path', path])
    else: # just install into the current environment, whatever that is
        pass

    cmd_list.extend(pkgs)
    (out, err) = _call_conda(cmd_list)
    if err.decode().strip():
        raise CondaError('conda %s: %s' % (" ".join(cmd_list), err.decode()))
    return out

def process(name=None, path=None, cmd=None, args=None, stdin=None, stdout=None, stderr=None, timeout=None):
    """
    Create a Popen process for cmd using the specified args but in the conda
    environment specified by name or path.

    The returned object will need to be invoked with p.communicate() or similar.

    :param name: name of conda environment
    :param path: path to conda environment (if no name specified)
    :param cmd:  command to invoke
    :param args: argument
    :param stdin: stdin
    :param stdout: stdout
    :param stderr: stderr
    :return: Popen object
    """

    if bool(name) == bool(path):
        raise TypeError('exactly one of name or path must be specified')

    if not cmd:
        raise TypeError('cmd to execute must be specified')

    if not args:
        args = []

    if name:
        path = get_prefix_envname(name)

    plat = 'posix'
    if sys.platform.lower().startswith('win'):
        listsep = ';'
        plat = 'win'
    else:
        listsep = ':'

    conda_env = dict(os.environ)

    if plat == 'posix':
        conda_env['PATH'] = path + os.path.sep + 'bin' + listsep + conda_env['PATH']
    else: # win
        conda_env['PATH'] = path + os.path.sep + 'Scripts' + listsep + conda_env['PATH']

    conda_env['PATH'] = path + listsep + conda_env['PATH']

    cmd_list = [cmd]
    cmd_list.extend(args)

    try:
        p = Popen(cmd_list, env=conda_env, stdin=stdin, stdout=stdout, stderr=stderr)
    except OSError:
        raise Exception("could not invoke %r\n" % cmd_list)
    return p


def clone(path, prefix):
    """
    Clone a "share package" (located at `path`) by creating a new
    environment at `prefix`, and return a dictionary with (at least) the
    following keys:
      - 'warnings': a list of warnings

    The directory `path` is located in, should be some temp directory or
    some other directory OUTSIDE /opt/anaconda.  After calling this
    function, the original file (at `path`) may be removed (by the caller
    of this function).
    The return object is a list of warnings.
    """
    return _call_and_parse(['clone', '--json', '--prefix', prefix, path])


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
