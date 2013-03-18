import re
import os
from os.path import isdir, join

import utils


ROOT_PREFIX = '/opt/anaconda'


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
    stdout, stderr = utils.call_conda(ROOT_PREFIX, ['--version'])
    m = pat.match(stderr.strip())
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
    Return the (set of canonical names) of linked packages in prefix.
    """
    meta_dir = join(prefix, 'conda-meta')
    if not isdir(meta_dir):
        return set()
    return set(fn[:-5] for fn in os.listdir(meta_dir) if fn.endswith('.json'))


if __name__ == '__main__':
    #set_root_prefix('/Users/ilan/python')
    print repr(get_conda_version())
    for prefix in get_envs():
        print prefix
        for dist in linked(prefix):
            print '\t', dist
