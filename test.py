import shutil
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
        shutil.rmtree(self.prefix)

    def test_version(self):
        try:
            conda_api.get_conda_version()
        except Exception as e:
            self.fail("get_conda_version fails: %s" % e)

    def test_envs(self):
        self.assertIsInstance(conda_api.get_envs(), list)

    def test_install(self):
        try:
            conda_api.install(pkgs=['python'], path=self.prefix)
        except CondaError as e:
            self.fail("install fails: %s" % e)

    def test_linked(self):
        linked = conda_api.linked(self.prefix)
        self.assertIsInstance(linked, set)
        self.assertTrue(any('python' in pkg for pkg in linked))

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
