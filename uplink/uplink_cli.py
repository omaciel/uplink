# coding=utf-8
"""The entry point for Uplink's command line interface."""
import json

import click

from uplink import config, exceptions
from uplink.config import UplinkConfig


def _raise_settings_not_found():
    """Raise `click.ClickException` for settings file not found."""
    result = click.ClickException(
        'there is no settings file. Use `uplink settings create` to '
        'create one.'
    )
    result.exit_code = -1
    raise result


@click.group()
def uplink():
    """Uplink facilitates functional testing of Satellite."""


@uplink.group()
@click.pass_context
def settings(ctx):
    """Manage settings file."""
    cfg = UplinkConfig()
    try:
        cfg_path = cfg.get_config_file_path()
    except exceptions.ConfigFileNotFoundError:
        cfg_path = None
    ctx.obj = {
        'cfg_path': cfg_path,
        'default_cfg_path': cfg.default_config_file_path,
    }


@settings.command('create')
@click.pass_context
def settings_create(ctx):
    """Create a settings file."""
    path = ctx.obj['cfg_path']
    if path:
        click.echo('Settings file already exist, continuing will override it.')
        click.confirm('Do you want to continue?', abort=True)
    else:
        path = ctx.obj['default_cfg_path']
    uplink_username = click.prompt('Satellite admin username', default='admin')
    uplink_password = click.prompt('Satellite admin password', default='changeme')
    uplink_version = click.prompt('Satellite version')
    system_hostname = click.prompt('System hostname')
    if click.confirm('Is Satellite published using HTTP?'):
        system_api_scheme = 'http'
    else:
        system_api_scheme = 'https'

    if system_api_scheme == 'https' and click.confirm('Verify HTTPS?'):
        certificate_path = click.prompt('SSL certificate path', default='')
        if not certificate_path:
            system_api_verify = True  # pragma: no cover
        else:
            system_api_verify = certificate_path
    else:
        system_api_verify = False

    if click.confirm('Is Satellite\'s message broker Qpid?', default=True):
        amqp_broker = 'qpidd'
    else:
        amqp_broker = 'rabbitmq'
    using_ssh = not click.confirm(
        'Are you running Uplink on the Satellite system?')
    if using_ssh:
        click.echo(
            'Uplink will be configured to access the Satellite system using '
            'SSH, because that, some additional information will be required.'
        )
        ssh_user = click.prompt('SSH username to use', default='root')
        click.echo(
            'Make sure to have the following lines on your ~/.ssh/config file:'
            '\n\n'
            '  Host {system_hostname}\n'
            '      StrictHostKeyChecking no\n'
            '      User {ssh_user}\n'
            '      UserKnownHostsFile /dev/null\n'
            '      ControlMaster auto\n'
            '      ControlPersist 10m\n'
            '      ControlPath ~/.ssh/controlmasters/%C\n'
            .format(system_hostname=system_hostname, ssh_user=ssh_user)
        )

    click.echo('Creating the settings file at {}...'.format(path))
    config_dict = {
        'pulp': {
            'auth': [uplink_username, uplink_password],
            'version': uplink_version,
        },
        'systems': [{
            'hostname': system_hostname,
            'roles': {
                'amqp broker': {'service': amqp_broker},
                'api': {
                    'scheme': system_api_scheme,
                    'verify': system_api_verify,
                },
                'mongod': {},
                'pulp celerybeat': {},
                'pulp cli': {},
                'pulp resource manager': {},
                'pulp workers': {},
                'shell': {'transport': 'ssh' if using_ssh else 'local'},
                'squid': {},
            }
        }]
    }
    with open(path, 'w') as handler:
        handler.write(json.dumps(config_dict, indent=2, sort_keys=True))
    click.echo(
        'Settings file created, run `uplink settings show` to show its '
        'contents.'
    )


@settings.command('show')
@click.pass_context
def settings_show(ctx):
    """Show the settings file."""
    path = ctx.obj['cfg_path']
    if not path:
        _raise_settings_not_found()

    click.echo(
        'Showing settings file {}\n'
        .format(path)
    )
    with open(path) as handle:
        click.echo(json.dumps(json.load(handle), indent=2, sort_keys=True))


@settings.command('validate')
@click.pass_context
def settings_validate(ctx):
    """Validate the settings file."""
    path = ctx.obj['cfg_path']
    if not path:
        _raise_settings_not_found()

    with open(path) as handle:
        config_dict = json.load(handle)
    if 'systems' not in config_dict and 'pulp' in config_dict:
        message = (
            'the settings file at {} appears to be following the old '
            'configuration file format, please update it like below:\n'
            .format(path)
        )
        message += json.dumps(config.convert_old_config(config_dict), indent=2)
        result = click.ClickException(message)
        result.exit_code = -1
        raise result
    try:
        config.validate_config(config_dict)
    except exceptions.ConfigValidationError as err:
        message = (
            'invalid settings file {}\n'
            .format(path)
        )
        for error_message in err.error_messages:
            message += error_message
        result = click.ClickException(message)
        result.exit_code = -1
        raise result


if __name__ == '__main__':
    uplink()  # pragma: no cover
