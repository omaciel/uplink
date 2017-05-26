# coding=utf-8
"""Unit tests for :mod:`uplink.config`."""
import builtins
import itertools
import json
import os
import random
import unittest
from unittest import mock

import xdg

from uplink import config, exceptions, utils

UPLINK_CONFIG = """
{
    "pulp": {
        "auth": ["username", "password"],
        "version": "2.12.1"
    },
    "systems": [
        {
            "hostname": "first.example.com",
            "roles": {
                "amqp broker": {"service": "qpidd"},
                "api": {"scheme": "https", "verify": true},
                "mongod": {},
                "pulp cli": {},
                "pulp celerybeat": {},
                "pulp resource manager": {},
                "pulp workers": {},
                "shell": {"transport": "local"},
                "squid": {}
            }
        },
        {
            "hostname": "second.example.com",
            "roles": {
                "api": {"scheme": "https", "verify": false},
                "pulp celerybeat": {},
                "pulp resource manager": {},
                "pulp workers": {},
                "shell": {"transport": "ssh"},
                "squid": {}
            }
        }
    ]
}
"""


OLD_CONFIG = """
{
    "pulp": {
        "base_url": "https://pulp.example.com",
        "auth": ["username", "password"],
        "verify": false,
        "version": "2.12",
        "cli_transport": "ssh"
    }
}
"""


def _gen_attrs():
    """Generate attributes for populating a ``UplinkConfig``.

    Example usage: ``UplinkConfig(**_gen_attrs())``.

    :returns: A dict. It populates all attributes in a ``UplinkConfig``.
    """
    return {
        'pulp_auth': [utils.uuid4() for _ in range(2)],
        'pulp_version': '.'.join(
            type('')(random.randint(1, 150)) for _ in range(4)
        ),
        'systems': [
            config.PulpSystem(
                hostname='pulp.example.com',
                roles={
                    'amqp broker': {'service': 'qpidd'},
                    'api': {
                        'scheme': 'https',
                        'verify': True
                    },
                    'mongod': {},
                    'pulp cli': {},
                    'pulp celerybeat': {},
                    'pulp resource manager': {},
                    'pulp workers': {},
                    'shell': {'transport': 'local'},
                    'squid': {}
                }
            )
        ],
    }


class GetConfigTestCase(unittest.TestCase):
    """Test :func:`uplink.config.get_config`."""

    def test_cache_full(self):
        """No config is read from disk if the cache is populated."""
        with mock.patch.object(config, '_CONFIG'):
            with mock.patch.object(config.UplinkConfig, 'read') as read:
                config.get_config()
        self.assertEqual(read.call_count, 0)

    def test_cache_empty(self):
        """A config is read from disk if the cache is empty."""
        with mock.patch.object(config, '_CONFIG', None):
            with mock.patch.object(config.UplinkConfig, 'read') as read:
                config.get_config()
        self.assertEqual(read.call_count, 1)


class ValidateConfigTestCase(unittest.TestCase):
    """Test :func:`uplink.config.validate_config`."""

    def test_valid_config(self):
        """A valid config does not raise an exception."""
        self.assertIsNone(
            config.validate_config(json.loads(UPLINK_CONFIG)))

    def test_invalid_config(self):
        """An invalid config raises an exception."""
        config_dict = json.loads(UPLINK_CONFIG)
        config_dict['pulp']['auth'] = []
        config_dict['systems'][0]['hostname'] = ''
        with self.assertRaises(exceptions.ConfigValidationError) as err:
            config.validate_config(config_dict)
        self.assertEqual(sorted(err.exception.error_messages), sorted([
            'Failed to validate config[\'pulp\'][\'auth\'] because [] is too '
            'short.',
            'Failed to validate config[\'systems\'][0][\'hostname\'] because '
            '\'\' is not a \'hostname\'.',
        ]))

    def test_config_missing_roles(self):
        """Missing required roles in config raises an exception."""
        config_dict = json.loads(UPLINK_CONFIG)
        for system in config_dict['systems']:
            system['roles'].pop('api', None)
            system['roles'].pop('pulp workers', None)
        with self.assertRaises(exceptions.ConfigValidationError) as err:
            config.validate_config(config_dict)
        self.assertEqual(
            err.exception.error_messages,
            ['The following roles are missing: api, pulp workers']
        )


class InitTestCase(unittest.TestCase):
    """Test :class:`uplink.config.UplinkConfig` instantiation."""

    @classmethod
    def setUpClass(cls):
        """Generate some attributes and use them to instantiate a config."""
        cls.kwargs = _gen_attrs()
        cls.cfg = config.UplinkConfig(**cls.kwargs)

    def test_public_attrs(self):
        """Assert that public attributes have correct values."""
        attrs = config._public_attrs(self.cfg)  # pylint:disable=W0212
        attrs['pulp_version'] = type('')(attrs['pulp_version'])
        self.assertEqual(self.kwargs, attrs)

    def test_private_attrs(self):
        """Assert that private attributes have been set."""
        for attr in ('_xdg_config_file', '_xdg_config_dir'):
            with self.subTest(attr):
                self.assertIsNotNone(getattr(self.cfg, attr))


class UplinkConfigFileTestCase(unittest.TestCase):
    """Verify the ``UPLINK_CONFIG_FILE`` environment var is respected."""

    def test_var_set(self):
        """Set the environment variable."""
        os_environ = {'UPLINK_CONFIG_FILE': utils.uuid4()}
        with mock.patch.dict(os.environ, os_environ, clear=True):
            cfg = config.UplinkConfig()
        self.assertEqual(
            cfg._xdg_config_file,  # pylint:disable=protected-access
            os_environ['UPLINK_CONFIG_FILE']
        )

    def test_var_unset(self):
        """Do not set the environment variable."""
        with mock.patch.dict(os.environ, {}, clear=True):
            cfg = config.UplinkConfig()
        # pylint:disable=protected-access
        self.assertEqual(cfg._xdg_config_file, 'settings.json')


class ReadTestCase(unittest.TestCase):
    """Test :meth:`uplink.config.UplinkConfig.read`."""

    def test_read_config_file(self):
        """Ensure Pulp Smash can read the config file."""
        open_ = mock.mock_open(read_data=UPLINK_CONFIG)
        with mock.patch.object(builtins, 'open', open_):
            with mock.patch.object(config, '_get_config_file_path'):
                cfg = config.UplinkConfig().read()
        with self.subTest('check pulp_auth'):
            self.assertEqual(cfg.pulp_auth, ['username', 'password'])
        with self.subTest('check pulp_version'):
            self.assertEqual(cfg.pulp_version, config.Version('2.12.1'))
        with self.subTest('check systems'):
            self.assertEqual(
                sorted(cfg.systems),
                sorted([
                    config.PulpSystem(
                        hostname='first.example.com',
                        roles={
                            'amqp broker': {'service': 'qpidd'},
                            'api': {
                                'scheme': 'https',
                                'verify': True,
                            },
                            'mongod': {},
                            'pulp cli': {},
                            'pulp celerybeat': {},
                            'pulp resource manager': {},
                            'pulp workers': {},
                            'shell': {'transport': 'local'},
                            'squid': {},
                        }
                    ),
                    config.PulpSystem(
                        hostname='second.example.com',
                        roles={
                            'api': {
                                'scheme': 'https',
                                'verify': False,
                            },
                            'pulp celerybeat': {},
                            'pulp resource manager': {},
                            'pulp workers': {},
                            'shell': {'transport': 'ssh'},
                            'squid': {}
                        }
                    ),
                ])
            )


class HelperMethodsTestCase(unittest.TestCase):
    """Test :meth:`uplink.config.UplinkConfig` helper methods."""

    def setUp(self):
        """Generate contents for a configuration file."""
        open_ = mock.mock_open(read_data=UPLINK_CONFIG)
        with mock.patch.object(builtins, 'open', open_):
            with mock.patch.object(config, '_get_config_file_path'):
                self.cfg = config.UplinkConfig().read()

    def test_get_systems(self):
        """``get_systems`` returns proper result."""
        with self.subTest('role with multiplie matching systems'):
            result = [
                system.hostname for system in self.cfg.get_systems('api')]
            self.assertEqual(len(result), 2)
            self.assertEqual(
                sorted(result),
                sorted(['first.example.com', 'second.example.com'])
            )
        with self.subTest('role with single match system'):
            result = [
                system.hostname for system in self.cfg.get_systems('mongod')]
            self.assertEqual(len(result), 1)
            self.assertEqual(
                sorted(result),
                sorted(['first.example.com'])
            )

    def test_services_for_roles(self):
        """``services_for_roles`` returns proper result."""
        roles = {role: {} for role in config.ROLES}
        expected_roles = {
            'httpd',
            'mongod',
            'pulp_celerybeat',
            'pulp_resource_manager',
            'pulp_workers',
            'squid',
        }
        with self.subTest('no amqp broker service'):
            self.assertEqual(
                self.cfg.services_for_roles(roles),
                expected_roles
            )
        with self.subTest('qpidd amqp broker service'):
            roles['amqp broker']['service'] = 'qpidd'
            self.assertEqual(
                self.cfg.services_for_roles(roles),
                expected_roles.union({'qpidd'})
            )
        with self.subTest('rabbitmq amqp broker service'):
            roles['amqp broker']['service'] = 'rabbitmq'
            self.assertEqual(
                self.cfg.services_for_roles(roles),
                expected_roles.union({'rabbitmq'})
            )


class GetRequestsKwargsTestCase(unittest.TestCase):
    """Test :meth:`uplink.config.UplinkConfig.get_requests_kwargs`."""

    @classmethod
    def setUpClass(cls):
        """Create a mock server config and call the method under test."""
        cls.attrs = _gen_attrs()
        cls.cfg = config.UplinkConfig(**cls.attrs)
        cls.kwargs = cls.cfg.get_requests_kwargs()

    def test_kwargs(self):
        """Assert that the method returns correct values."""
        self.assertEqual(
            self.kwargs,
            {
                'auth': tuple(self.attrs['pulp_auth']),
                'verify': True,
            }
        )

    def test_cfg_auth(self):
        """Assert that the method does not alter the config's ``auth``."""
        # _gen_attrs() returns ``auth`` as a list.
        self.assertIsInstance(self.cfg.pulp_auth, list)

    def test_kwargs_auth(self):
        """Assert that the method converts ``auth`` to a tuple."""
        self.assertIsInstance(self.kwargs['auth'], tuple)


class ReprTestCase(unittest.TestCase):
    """Test calling ``repr`` on a `uplink.config.UplinkConfig`."""

    @classmethod
    def setUpClass(cls):
        """Generate attributes and call the method under test."""
        cls.attrs = _gen_attrs()
        cls.cfg = config.UplinkConfig(**cls.attrs)
        cls.result = repr(cls.cfg)

    def test_is_sane(self):
        """Assert that the result is in an expected set of results."""
        # permutations() → (((k1, v1), (k2, v2)), ((k2, v2), (k1, v1)))
        # kwargs_iter = ('k1=v1, k2=v2', 'k2=v2, k1=v1)
        kwargs_iter = (
            ', '.join(key + '=' + repr(val) for key, val in two_tuples)
            for two_tuples in itertools.permutations(self.attrs.items())
        )
        targets = tuple(
            'UplinkConfig({})'.format(arglist) for arglist in kwargs_iter
        )
        self.assertIn(self.result, targets)

    def test_can_eval(self):
        """Assert that the result can be parsed by ``eval``."""
        from uplink.config import UplinkConfig, PulpSystem  # noqa pylint:disable=unused-variable
        # pylint:disable=eval-used
        cfg = eval(self.result)
        with self.subTest('check pulp_version'):
            self.assertEqual(cfg.pulp_version, self.cfg.pulp_version)
        with self.subTest('check pulp_version'):
            self.assertEqual(cfg.pulp_version, self.cfg.pulp_version)
        with self.subTest('check systems'):
            self.assertEqual(cfg.systems, self.cfg.systems)


class GetConfigFilePathTestCase(unittest.TestCase):
    """Test ``uplink.config._get_config_file_path``."""

    def test_success(self):
        """Assert the method returns a path when a config file is found."""
        with mock.patch.object(xdg.BaseDirectory, 'load_config_paths') as lcp:
            lcp.return_value = ('an_iterable', 'of_xdg', 'config_paths')
            with mock.patch.object(os.path, 'isfile') as isfile:
                isfile.return_value = True
                # pylint:disable=protected-access
                config._get_config_file_path(utils.uuid4(), utils.uuid4())
        self.assertGreater(isfile.call_count, 0)

    def test_failures(self):
        """Assert the  method raises an exception when no config is found."""
        with mock.patch.object(xdg.BaseDirectory, 'load_config_paths') as lcp:
            lcp.return_value = ('an_iterable', 'of_xdg', 'config_paths')
            with mock.patch.object(os.path, 'isfile') as isfile:
                isfile.return_value = False
                with self.assertRaises(exceptions.ConfigFileNotFoundError):
                    # pylint:disable=protected-access
                    config._get_config_file_path(utils.uuid4(), utils.uuid4())
        self.assertGreater(isfile.call_count, 0)


def _get_written_json(mock_obj):
    """Return the JSON that has been written to a mock `open` object."""
    # json.dump() calls write() for each individual JSON token.
    return json.loads(''.join(
        tuple(call_obj)[1][0]
        for call_obj
        in mock_obj().write.mock_calls
    ))
