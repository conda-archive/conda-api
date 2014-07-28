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
        handle, fpath = tempfile.mkstemp()
        self.config = fpath

    @classmethod
    def tearDownClass(self):
        os.remove(self.config)
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
            clone = os.path.join(tempfile.mkdtemp(), 'conda_api_test_clone')
            conda_api.create(path=path, pkgs=['python'])
            conda_api.clone_environment(path, path=clone)
            self.assertEqual(conda_api.linked(path), conda_api.linked(clone))
            conda_api.remove_environment(path=path)
            conda_api.remove_environment(path=clone)
        except Exception as e:
            self.fail('create/remove fails: %s' % e)

    def test_install(self):
        try:
            for pkgset in (['python=3.4'], ['python=3.4.0']):
                result = conda_api.install(pkgs=pkgset, path=self.prefix)
        except conda_api.CondaError as e:
            self.fail("install fails: %s" % e)

        for pkg in conda_api.linked(self.prefix):
            info = conda_api.package_info(pkg + '.tar.bz2')
            # info isn't necessarily complete because conda info only checks
            # prefixes in default prefix dirs and there isn't a way to
            # specify a prefix to check yet
            self.assertIn(pkg + '.tar.bz2', info)

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

    def test_config(self):
        self.assertIsInstance(conda_api.config_path(), str)
        self.assertEqual(conda_api.config_set('use_pip', False, file=self.config), [])
        self.assertEqual(conda_api.config_add('channels', 'wakari', file=self.config), [])
        self.assertEqual(conda_api.config_get('channels', file=self.config), {'channels': ['wakari']})
        self.assertEqual(conda_api.config_get('use_pip', file=self.config), {'use_pip': False})
        self.assertEqual(conda_api.config_remove('channels', 'wakari', file=self.config), [])
        self.assertEqual(conda_api.config_get('channels', file=self.config).get('channels', []), [])
        self.assertEqual(conda_api.config_delete('use_pip', file=self.config), [])
        self.assertEqual(conda_api.config_get('use_pip', file=self.config), {})
