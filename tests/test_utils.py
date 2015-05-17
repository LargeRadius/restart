from __future__ import absolute_import

import os
import sys
import shutil
import tempfile

import pytest

from restart.utils import load_resources, expand_wildcards


def mkdir(path):
    os.mkdir(path)


def mkfile(path):
    open(path, 'w').close()


class TestUtils(object):

    def setup_class(cls):
        cls.tempdir = tempfile.mkdtemp()

        # build the directory structure
        origin_cwd = os.getcwd()
        os.chdir(cls.tempdir)

        mkdir('testapi')
        mkfile('testapi/__init__.py')
        mkdir('testapi/resources')
        mkfile('testapi/resources/__init__.py')
        mkdir('testapi/resources/users')
        mkfile('testapi/resources/users/__init__.py')
        mkfile('testapi/resources/users/resource.py')
        mkdir('testapi/resources/orders')
        mkfile('testapi/resources/orders/__init__.py')
        mkfile('testapi/resources/orders/resource.py')

        os.chdir(origin_cwd)

        # add cls.tempdir into sys.path
        sys.path.insert(0, cls.tempdir)

    def teardown_class(cls):
        sys.path.remove(cls.tempdir)
        shutil.rmtree(cls.tempdir)

    def test_load_resources(self):
        load_resources(['testapi.resources.users.resource'])

    def test_load_resources_with_nonexistent_entrypoints(self):
        with pytest.raises(ImportError):
            load_resources(['testapi.resources.counts.resource'])

    def test_load_resources_with_wildcards_entrypoints(self):
        load_resources(['testapi.resources.*.resource'])

    def test_load_resources_with_nonexistent_wildcards_entrypoints(self):
        entrypoint = 'testapi.resources.users.*.resource'
        with pytest.raises(ImportError) as exc:
            load_resources([entrypoint])
        expected_exc_msg = 'No module found with wildcards %r' % entrypoint
        assert str(exc.value) == expected_exc_msg

    def test_expand_wildcards(self):
        entrypoints = expand_wildcards('testapi.resources.*.resource')
        assert entrypoints == ['testapi.resources.users.resource',
                               'testapi.resources.orders.resource']

        entrypoints = expand_wildcards('testapi.*.*.resource')
        assert entrypoints == ['testapi.resources.users.resource',
                               'testapi.resources.orders.resource']

    def test_expand_wildcards_with_nonexistent_entrypoint(self):
        entrypoints = expand_wildcards('testapi.resources.users.*.resource')
        assert not entrypoints

    def test_expand_wildcards_package(self):
        entrypoints = expand_wildcards('testapi.resources.*')
        assert entrypoints == ['testapi.resources',
                               'testapi.resources.users',
                               'testapi.resources.orders']
