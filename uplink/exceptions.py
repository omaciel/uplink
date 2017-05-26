# coding=utf-8
"""Custom exceptions defined by Uplink."""


class BugStatusUnknownError(Exception):
    """We have encountered a bug whose status is unknown to us.

    See :mod:`uplink.selectors` for more information on how bug statuses
    are used.
    """


class BugTPRMissingError(Exception):
    """We have encountered a bug with no "Target Platform Release" field.

    See :mod:`uplink.selectors` for more information.
    """


class CallReportError(Exception):
    """A call report contains an error.

    For more information about pulp's task handling, see
    `Synchronous and Asynchronous Calls`_ and `Task Management`_.

    .. _Synchronous and Asynchronous Calls:
        http://docs.pulpproject.org/en/latest/dev-guide/conventions/sync-v-async.html
    .. _Task Management:
        http://docs.pulpproject.org/en/latest/dev-guide/integration/rest-api/tasks.html
    """


class CalledProcessError(Exception):
    """Indicates a CLI process has a non-zero return code.

    See :meth:`uplink.cli.CompletedProcess` for more information.
    """

    def __str__(self):
        """Provide a human-friendly string representation of this exception."""
        return (
            'Command {} returned non-zero exit status {}.\n\n'
            'stdout: {}\n\n'
            'stderr: {}'
        ).format(*self.args)


class ConfigFileNotFoundError(Exception):
    """We cannot find the requested Uplink configuration file.

    See :mod:`uplink.config` for more information on how configuration
    files are handled.
    """


class ConfigValidationError(Exception):
    """The configuration file has validation errors.

    See :func:`uplink.config.validate_config` for more information on how
        configuration validation is handled.
    """

    def __init__(self, error_messages, *args, **kwargs):
        """Require that the validation messages list is defined."""
        super().__init__(error_messages, *args, **kwargs)
        self.error_messages = error_messages

    def __str__(self):
        """Provide a human-friendly string representation of this exception."""
        return (
            'Configuration file is not valid:\n\n'
            '{}'
        ).format('\n'.join(self.error_messages))


class ConfigFileSectionNotFoundError(Exception):
    """We cannot read the requested Uplink configuration file section.

    See :mod:`uplink.config` for more information on how configuration
    files are handled.
    """


class NoKnownBrokerError(Exception):
    """We cannot determine the AMQP broker used by a system.

    An "AMQP broker" is a tool such as RabbitMQ or Apache Qpid.
    """


class NoKnownPackageManagerError(Exception):
    """We cannot determine the package manager used by a system.

    A "package manager" is a tool such as ``yum`` or ``dnf``.
    """


class NoKnownServiceManagerError(Exception):
    """We cannot determine the service manager used by a system.

    A "service manager" is a tool such as ``systemctl`` or ``service``.
    """


class TaskReportError(Exception):
    """A task contains an error.

    For more information about pulp's task handling, see
    `Synchronous and Asynchronous Calls`_ and `Task Management`_.

    .. _Synchronous and Asynchronous Calls:
        http://docs.pulpproject.org/en/latest/dev-guide/conventions/sync-v-async.html
    .. _Task Management:
        http://docs.pulpproject.org/en/latest/dev-guide/integration/rest-api/tasks.html
    """

    def __init__(self, msg, task, *args, **kwargs):
        """Require that a task object is defined."""
        super().__init__(msg, task, *args, **kwargs)
        self.task = task


class TaskTimedOutError(Exception):
    """We timed out while polling a task and waiting for it to complete.

    See :func:`uplink.api.poll_spawned_tasks` and
    :func:`uplink.api.poll_task` for more information on how task polling
    is handled.
    """
