import os
import tempfile
import unittest

import conda_api

# Test Conda-Api by performing operations in a temporary directory

class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        conda_api.set_root_prefix()
        self.prefix = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(self):
        conda_api.remove_environment(path=self.prefix)

    def test_version(self):
        try:
            conda_api.get_conda_version()
        except Exception as e:
            self.fail("get_conda_version fails: %s" % e)

    def test_envs(self):
        self.assertIsInstance(conda_api.get_envs(), list)
        try:
            path = os.path.join(tempfile.mkdtemp(), 'conda_api_test')
            conda_api.create(path=path, pkgs=['python'])
            conda_api.remove_environment(path=path)
        except Exception as e:
            self.fail('create/remove fails: %s' % e)

    def test_install(self):
        try:
            for pkgset in (['python=3.4'], ['python=3.4.0']):
                result = conda_api.install(pkgs=pkgset, path=self.prefix)
        except conda_api.CondaError as e:
            self.fail("install fails: %s" % e)

        try:
            result = conda_api.update('python', path=self.prefix)
            self.assertIn('success', result)
            self.assertTrue(result['success'])
        except conda_api.CondaError as e:
            self.fail("update fails: %s" % e)

        linked = conda_api.linked(self.prefix)
        self.assertIsInstance(linked, set)
        self.assertTrue(any('python' in pkg for pkg in linked))

        try:
            result = conda_api.remove('python', path=self.prefix)
            self.assertIn('success', result)
            self.assertTrue(result['success'])
        except conda_api.CondaError as e:
            self.fail("update fails: %s" % e)

        self.assertRaises(TypeError, lambda: conda_api.install(path=self.prefix))
        self.assertRaises(TypeError, lambda: conda_api.update(path=self.prefix))

    def test_search(self):
        self.assertRaises(TypeError, lambda: conda_api.search(platform='dos'))
        self.assertRaises(TypeError, lambda: conda_api.search(regex='test', spec='test'))

        result = conda_api.search(spec='ipython')
        self.assertIn('ipython', result)
        self.assertIsInstance(result['ipython'], list)
        self.assertIsInstance(result['ipython'][0], dict)

# print(conda_api.config_path())
# print(conda_api.config_path(system=True))
# print(conda_api.config_get())
# print(conda_api.config_get('channels'))
# print(conda_api.config_get('use_pip'))
# print(conda_api.config_set('use_pip', True))
# print(conda_api.config_get('use_pip'))
# print(conda_api.config_set('use_pip', False))
# print(conda_api.config_get('use_pip'))
# print(conda_api.config_add('channels', 'binstar'))
# print(conda_api.config_remove('channels', 'binstar'))
# print(conda_api.config_delete('use_pip'))
